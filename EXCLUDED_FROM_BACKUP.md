# What is and is not in this backup

Source: the project's Google Drive folder
(https://drive.google.com/drive/folders/1nFUDnOMdnBGV-g-H6MKEfSSq_1DqyKVp).
`DRIVE_MANIFEST.csv` lists every file found on Drive (31,340 unique files) with its
size, its status here and its path in this repo.

## Included

- `code/`: all seven repos, including build artifacts, bytecode, egg-info and cache/lock files.
  Each repo's original `.git` folder is stored as `_upstream_git/`; the two pack files above 100MB
  (OpenFusion, Grounded-Segment-Anything) are split into chunks.
- `drive_extras/logs`, `production_backup`, `contrib`, `outputs`: every file, including those over
  100MB (fusion `F*.npz` arrays, `vlfusion.npz`), stored as 90MiB chunks. Rebuild with
  `drive_extras/REASSEMBLE.md`; checksums are in `drive_extras/SPLIT_FILES_SHA256.txt`.
- `drive_extras/datasets/` and `code/OpenFusion/replica_office0|replica_room0`: the non-image Replica
  files (semantic ground-truth meshes, trajectories, ConceptGraphs RGB point clouds, meshes, metadata).
- Three Git LFS files from the first commit: `groundingdino_swint_ogc.pth` (662MB),
  `seem_focall_v1.pt` (1.3GB) and `OpenFusion/assets/output.gif` (72MB).

## Not in this repo (still only on Drive)

### Model checkpoints above GitHub's 2GB per-file LFS limit

| File | Size | Drive path |
|---|---|---|
| `ram_swin_large_14m.pth` | 5.6GB | `code/Grounded-Segment-Anything/Tag2Text/` |
| `tag2text_swin_14m.pth` | 4.5GB | `code/Grounded-Segment-Anything/Tag2Text/` |
| `sam_vit_h_4b8939.pth` | 2.6GB | `code/Grounded-Segment-Anything/` |

They are standard pretrained weights (RAM, Tag2Text, SAM ViT-H) and can be re-downloaded from
their original sources. They could be added by splitting into chunks under 100MB, but that would
push the repo far past GitHub's recommended size, so they were left out.

### Replica benchmark images and the raw dataset (27,230 files, sizes not measured)

Not downloaded, because it is public benchmark data and would exceed GitHub's recommended repo size:

- The RGB (`.jpg`) and depth (`.png`) frames under `datasets/replica/` (office0-3, room0),
  also linked at `code/OpenFusion/sample/replica/` (the same Drive files in two folders), and under
  `datasets/replica_conceptgraphs/` (office0, room0).
- `datasets/replica_v1_0/` (17-part `replica_v1_0.tar.gz`).

Everything else in those folders (ground-truth semantic meshes, trajectories, ConceptGraphs RGB
point clouds, OpenFusion meshes, JSON/text metadata; 56 files) is in the repo under
`drive_extras/datasets/` and `code/OpenFusion/replica_*`.

### Empty on Drive

`checkpoints/openclip`, `checkpoints/sam`, `checkpoints/seem` contain no files.

## Notes

- The results notes in `drive_extras/logs/session_checkpoints/` are dated 2026-09-13; the fusion
  results in `production_backup/` are from 2026-09-17.
- The code that defines the F1/F2/F3 fusion conditions was not found on Drive.
