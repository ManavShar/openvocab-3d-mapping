
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class GTQueryResult:
    """
    Result of semantic GT lookup for a batch of world-space points.

    labels:
        Semantic class IDs. -1 means IGNORE / no valid semantic label.

    distances_m:
        Exact point-to-semantic-surface distance in meters.
        NaN means no candidate surface was available.

    object_ids:
        Replica semantic object IDs. -1 means no accepted surface match.

    valid:
        True only when the point is within the configured surface
        tolerance and maps to a valid semantic class (class_id >= 0).

    surface_match:
        True when the nearest semantic surface is within the configured
        surface tolerance, regardless of whether its semantic class is
        valid.

    ignore:
        True when the point should be excluded from semantic evaluation.
        This includes:
          - no surface match,
          - missing object metadata,
          - object mapped to class_id < 0.
    """
    labels: np.ndarray
    distances_m: np.ndarray
    object_ids: np.ndarray
    valid: np.ndarray
    surface_match: np.ndarray
    ignore: np.ndarray


class ReplicaSemanticGT:
    """
    Replica v1.0 semantic ground-truth provider.

    Expected compact GT layout:

        <root>/
            office_0/
                semantic.bin
                semantic.json
                habitat/
                    info_semantic.json
                    mesh_semantic.ply
            ...

    The provider uses:
      - habitat/mesh_semantic.ply for geometric surface + face object_id
      - habitat/info_semantic.json for object_id -> class_id
      - K=32 centroid candidates followed by exact point-to-triangle
        distance, matching the validated project geometry procedure.

    semantic.bin and semantic.json are intentionally not used for
    face-level semantic class assignment.
    """

    SCENE_MAP = {
        "office0": "office_0",
        "office1": "office_1",
        "office2": "office_2",
        "office3": "office_3",
        "office4": "office_4",
        "room0": "room_0",
        "room1": "room_1",
        "room2": "room_2",
    }

    def __init__(
        self,
        root: str | Path,
        scene: str,
        candidate_k: int = 32,
        surface_tolerance_m: float = 0.005,
    ) -> None:
        if candidate_k <= 0:
            raise ValueError("candidate_k must be positive")

        if surface_tolerance_m <= 0:
            raise ValueError("surface_tolerance_m must be positive")

        self.root = Path(root)
        self.scene = scene
        self.candidate_k = int(candidate_k)
        self.surface_tolerance_m = float(surface_tolerance_m)

        if scene not in self.SCENE_MAP:
            raise ValueError(
                f"Unsupported Replica scene {scene!r}. "
                f"Expected one of {sorted(self.SCENE_MAP)}"
            )

        self.scene_dir = self.root / self.SCENE_MAP[scene]
        self.info_path = (
            self.scene_dir / "habitat" / "info_semantic.json"
        )
        self.mesh_path = (
            self.scene_dir / "habitat" / "mesh_semantic.ply"
        )

        self._vertices: Optional[np.ndarray] = None
        self._triangles: Optional[np.ndarray] = None
        self._triangle_object_ids: Optional[np.ndarray] = None
        self._triangle_centroids: Optional[np.ndarray] = None
        self._object_to_class: Optional[Dict[int, int]] = None
        self._object_to_name: Optional[Dict[int, str]] = None

        self._centroid_tree = None

        self._load()

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def vertices(self) -> np.ndarray:
        assert self._vertices is not None
        return self._vertices

    @property
    def triangles(self) -> np.ndarray:
        assert self._triangles is not None
        return self._triangles

    @property
    def triangle_object_ids(self) -> np.ndarray:
        assert self._triangle_object_ids is not None
        return self._triangle_object_ids

    @property
    def triangle_centroids(self) -> np.ndarray:
        assert self._triangle_centroids is not None
        return self._triangle_centroids

    @property
    def object_to_class(self) -> Dict[int, int]:
        assert self._object_to_class is not None
        return self._object_to_class

    @property
    def object_to_name(self) -> Dict[int, str]:
        assert self._object_to_name is not None
        return self._object_to_name

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self.scene_dir.exists():
            raise FileNotFoundError(
                f"Replica semantic scene directory does not exist: "
                f"{self.scene_dir}"
            )

        if not self.info_path.exists():
            raise FileNotFoundError(
                f"Missing semantic metadata: {self.info_path}"
            )

        if not self.mesh_path.exists():
            raise FileNotFoundError(
                f"Missing semantic mesh: {self.mesh_path}"
            )

        self._load_object_metadata()
        self._load_semantic_mesh()
        self._build_centroid_index()

    def _load_object_metadata(self) -> None:
        with open(self.info_path, "r") as f:
            info = json.load(f)

        objects = info.get("objects")
        if not isinstance(objects, list):
            raise ValueError(
                "info_semantic.json does not contain a list-valued "
                "'objects' field"
            )

        object_to_class: Dict[int, int] = {}
        object_to_name: Dict[int, str] = {}

        for obj in objects:
            if not isinstance(obj, dict):
                continue

            if "id" not in obj:
                continue

            object_id = int(obj["id"])

            class_id = int(obj.get("class_id", -1))
            class_name = str(obj.get("class_name", "UNKNOWN"))

            object_to_class[object_id] = class_id
            object_to_name[object_id] = class_name

        self._object_to_class = object_to_class
        self._object_to_name = object_to_name

    def _load_semantic_mesh(self) -> None:
        """
        Read the known Replica binary PLY representation without relying
        on an external PLY parser.

        The validated schema is:

          vertex:
            float x y z
            float nx ny nz
            uchar red green blue

          face:
            list uint8 uint32 vertex_indices
            uint16 object_id

        Replica office_0 contains quad faces. We triangulate each polygon
        as a fan. The implementation accepts polygons of arbitrary
        length >= 3 so the same provider works across Replica scenes.
        """

        with open(self.mesh_path, "rb") as f:
            header_lines = []

            while True:
                line = f.readline()

                if not line:
                    raise ValueError(
                        "Unexpected EOF before PLY end_header"
                    )

                text = line.decode("ascii", errors="strict").rstrip()
                header_lines.append(text)

                if text == "end_header":
                    break

            header = "\n".join(header_lines)

            if "format binary_little_endian 1.0" not in header:
                raise ValueError(
                    "Expected binary_little_endian PLY format"
                )

            vertex_count = None
            face_count = None

            for line in header_lines:
                parts = line.split()

                if len(parts) == 3 and parts[:2] == ["element", "vertex"]:
                    vertex_count = int(parts[2])

                if len(parts) == 3 and parts[:2] == ["element", "face"]:
                    face_count = int(parts[2])

            if vertex_count is None or face_count is None:
                raise ValueError(
                    "Could not determine PLY vertex/face counts"
                )

            # Exact validated vertex layout:
            # 6 float32 + 3 uint8 = 27 bytes.
            vertex_dtype = np.dtype(
                [
                    ("x", "<f4"),
                    ("y", "<f4"),
                    ("z", "<f4"),
                    ("nx", "<f4"),
                    ("ny", "<f4"),
                    ("nz", "<f4"),
                    ("red", "u1"),
                    ("green", "u1"),
                    ("blue", "u1"),
                ]
            )

            raw_vertices = np.fromfile(
                f,
                dtype=vertex_dtype,
                count=vertex_count,
            )

            if raw_vertices.shape[0] != vertex_count:
                raise ValueError(
                    f"Expected {vertex_count} vertices but read "
                    f"{raw_vertices.shape[0]}"
                )

            vertices = np.column_stack(
                [
                    raw_vertices["x"],
                    raw_vertices["y"],
                    raw_vertices["z"],
                ]
            ).astype(np.float64, copy=False)

            triangles = []
            triangle_object_ids = []

            for _ in range(face_count):
                count_raw = f.read(1)

                if len(count_raw) != 1:
                    raise ValueError(
                        "Unexpected EOF while reading face vertex count"
                    )

                n_vertices = int(np.frombuffer(count_raw, dtype="<u1")[0])

                if n_vertices < 3:
                    raise ValueError(
                        f"Invalid polygon with {n_vertices} vertices"
                    )

                indices_raw = f.read(4 * n_vertices)

                if len(indices_raw) != 4 * n_vertices:
                    raise ValueError(
                        "Unexpected EOF while reading face indices"
                    )

                indices = np.frombuffer(
                    indices_raw,
                    dtype="<u4",
                ).astype(np.int64)

                object_raw = f.read(2)

                if len(object_raw) != 2:
                    raise ValueError(
                        "Unexpected EOF while reading object_id"
                    )

                object_id = int(
                    np.frombuffer(
                        object_raw,
                        dtype="<u2",
                    )[0]
                )

                # Polygon fan triangulation:
                # (v0,v1,v2), (v0,v2,v3), ...
                for j in range(1, n_vertices - 1):
                    tri = (
                        int(indices[0]),
                        int(indices[j]),
                        int(indices[j + 1]),
                    )

                    triangles.append(tri)
                    triangle_object_ids.append(object_id)

            triangles_array = np.asarray(
                triangles,
                dtype=np.int64,
            )

            triangle_object_ids_array = np.asarray(
                triangle_object_ids,
                dtype=np.int64,
            )

            if triangles_array.ndim != 2 or triangles_array.shape[1] != 3:
                raise ValueError(
                    f"Unexpected triangle array shape: "
                    f"{triangles_array.shape}"
                )

            if triangle_object_ids_array.shape[0] != triangles_array.shape[0]:
                raise ValueError(
                    "Triangle/object_id count mismatch"
                )

            if (
                triangles_array.min() < 0
                or triangles_array.max() >= vertex_count
            ):
                raise ValueError(
                    "PLY contains an out-of-range vertex index"
                )

            self._vertices = vertices
            self._triangles = triangles_array
            self._triangle_object_ids = triangle_object_ids_array

    def _build_centroid_index(self) -> None:
        from scipy.spatial import cKDTree

        tri_vertices = self.vertices[self.triangles]

        self._triangle_centroids = tri_vertices.mean(
            axis=1
        )

        self._centroid_tree = cKDTree(
            self._triangle_centroids
        )

    # ------------------------------------------------------------------
    # Exact geometry
    # ------------------------------------------------------------------

    @staticmethod
    def _point_to_triangle_distance_squared(
        point: np.ndarray,
        triangle: np.ndarray,
    ) -> float:
        """
        Exact closest-point distance squared between a 3D point and
        a triangle using the standard region tests.
        """

        a = triangle[0]
        b = triangle[1]
        c = triangle[2]

        ab = b - a
        ac = c - a
        ap = point - a

        d1 = float(np.dot(ab, ap))
        d2 = float(np.dot(ac, ap))

        if d1 <= 0.0 and d2 <= 0.0:
            return float(np.dot(ap, ap))

        bp = point - b
        d3 = float(np.dot(ab, bp))
        d4 = float(np.dot(ac, bp))

        if d3 >= 0.0 and d4 <= d3:
            return float(np.dot(bp, bp))

        vc = d1 * d4 - d3 * d2

        if vc <= 0.0 and d1 >= 0.0 and d3 <= 0.0:
            denom = d1 - d3

            if abs(denom) < 1e-15:
                return min(
                    float(np.dot(ap, ap)),
                    float(np.dot(bp, bp)),
                )

            v = d1 / denom
            projection = a + v * ab
            diff = point - projection

            return float(np.dot(diff, diff))

        cp = point - c
        d5 = float(np.dot(ab, cp))
        d6 = float(np.dot(ac, cp))

        if d6 >= 0.0 and d5 <= d6:
            return float(np.dot(cp, cp))

        vb = d5 * d2 - d1 * d6

        if vb <= 0.0 and d2 >= 0.0 and d6 <= 0.0:
            denom = d2 - d6

            if abs(denom) < 1e-15:
                return min(
                    float(np.dot(ap, ap)),
                    float(np.dot(cp, cp)),
                )

            w = d2 / denom
            projection = a + w * ac
            diff = point - projection

            return float(np.dot(diff, diff))

        va = d3 * d6 - d5 * d4

        if (
            va <= 0.0
            and (d4 - d3) >= 0.0
            and (d5 - d6) >= 0.0
        ):
            denom = (d4 - d3) + (d5 - d6)

            if abs(denom) < 1e-15:
                return min(
                    float(np.dot(bp, bp)),
                    float(np.dot(cp, cp)),
                )

            w = (d4 - d3) / denom
            projection = b + w * (c - b)
            diff = point - projection

            return float(np.dot(diff, diff))

        # Inside the triangle.
        normal = np.cross(ab, ac)
        normal_norm_sq = float(np.dot(normal, normal))

        if normal_norm_sq < 1e-20:
            # Degenerate triangle: fall back to edge/vertex distances.
            return min(
                ReplicaSemanticGT._point_to_segment_distance_squared(
                    point, a, b
                ),
                ReplicaSemanticGT._point_to_segment_distance_squared(
                    point, a, c
                ),
                ReplicaSemanticGT._point_to_segment_distance_squared(
                    point, b, c
                ),
            )

        distance_to_plane = float(
            np.dot(point - a, normal)
        )

        return (
            distance_to_plane * distance_to_plane
            / normal_norm_sq
        )

    @staticmethod
    def _point_to_segment_distance_squared(
        point: np.ndarray,
        a: np.ndarray,
        b: np.ndarray,
    ) -> float:
        ab = b - a
        denom = float(np.dot(ab, ab))

        if denom < 1e-20:
            diff = point - a
            return float(np.dot(diff, diff))

        t = float(np.dot(point - a, ab) / denom)
        t = max(0.0, min(1.0, t))

        projection = a + t * ab
        diff = point - projection

        return float(np.dot(diff, diff))

    # ------------------------------------------------------------------
    # GT query
    # ------------------------------------------------------------------

    def query(
        self,
        points_world: np.ndarray,
    ) -> GTQueryResult:
        """
        Label a batch of world-space 3D points.

        Input:
            points_world: (N, 3), meters, Replica world coordinates.

        Output:
            GTQueryResult with N entries.

        Candidate selection:
            K nearest triangle centroids.

        Exact acceptance:
            nearest exact point-to-triangle distance <= tolerance.

        Semantic policy:
            class_id >= 0 -> VALID
            class_id < 0  -> IGNORE
            missing object metadata -> IGNORE
            no surface within tolerance -> IGNORE
        """

        points = np.asarray(points_world, dtype=np.float64)

        if points.ndim != 2 or points.shape[1] != 3:
            raise ValueError(
                f"points_world must have shape (N,3), "
                f"got {points.shape}"
            )

        n = points.shape[0]

        labels = np.full(n, -1, dtype=np.int32)
        distances = np.full(n, np.nan, dtype=np.float64)
        object_ids = np.full(n, -1, dtype=np.int32)

        valid = np.zeros(n, dtype=bool)
        surface_match = np.zeros(n, dtype=bool)
        ignore = np.ones(n, dtype=bool)

        if n == 0:
            return GTQueryResult(
                labels=labels,
                distances_m=distances,
                object_ids=object_ids,
                valid=valid,
                surface_match=surface_match,
                ignore=ignore,
            )

        assert self._centroid_tree is not None

        k = min(
            self.candidate_k,
            self.triangles.shape[0],
        )

        _, candidate_indices = self._centroid_tree.query(
            points,
            k=k,
            workers=-1,
        )

        if k == 1:
            candidate_indices = candidate_indices[:, None]

        for i in range(n):
            point = points[i]

            best_distance_sq = np.inf
            best_triangle = -1

            for tri_idx in candidate_indices[i]:
                tri_idx = int(tri_idx)

                triangle = self.vertices[
                    self.triangles[tri_idx]
                ]

                d2 = self._point_to_triangle_distance_squared(
                    point,
                    triangle,
                )

                if d2 < best_distance_sq:
                    best_distance_sq = d2
                    best_triangle = tri_idx

            if best_triangle < 0:
                continue

            distance = float(np.sqrt(best_distance_sq))

            distances[i] = distance

            if distance > self.surface_tolerance_m:
                continue

            surface_match[i] = True

            object_id = int(
                self.triangle_object_ids[best_triangle]
            )

            object_ids[i] = object_id

            class_id = self.object_to_class.get(
                object_id,
                -1,
            )

            if class_id < 0:
                continue

            labels[i] = class_id
            valid[i] = True
            ignore[i] = False

        return GTQueryResult(
            labels=labels,
            distances_m=distances,
            object_ids=object_ids,
            valid=valid,
            surface_match=surface_match,
            ignore=ignore,
        )

    def query_iter(
        self,
        points_world: np.ndarray,
        batch_size: int = 8192,
    ) -> Iterable[GTQueryResult]:
        """
        Memory-safe iterator over large point arrays.
        """

        if batch_size <= 0:
            raise ValueError("batch_size must be positive")

        points = np.asarray(points_world)

        for start in range(0, points.shape[0], batch_size):
            yield self.query(
                points[start:start + batch_size]
            )


def load_replica_semantic_gt(
    root: str | Path,
    scene: str,
    candidate_k: int = 32,
    surface_tolerance_m: float = 0.005,
) -> ReplicaSemanticGT:
    """
    Convenience constructor.
    """

    return ReplicaSemanticGT(
        root=root,
        scene=scene,
        candidate_k=candidate_k,
        surface_tolerance_m=surface_tolerance_m,
    )
