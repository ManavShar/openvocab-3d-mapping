# Research Project — Latest Progress
Date: 2026-09-13

## Overall Phase Status

0. Colab + Drive validation              — COMPLETE
1. Repositories + dependencies           — COMPLETE
2. Replica dataset preparation           — COMPLETE
3. Open-Fusion reproduction               — COMPLETE
4. ConceptGraphs reproduction             — COMPLETE for room0
5. Own pipeline                           — NOT STARTED / DESIGN PENDING
6. Fusion ablation                        — NOT STARTED
7. Evaluation                             — NOT STARTED
8. Closed-vocabulary baseline             — NOT STARTED
9. Tables + figures                       — NOT STARTED
10. Final verification                    — NOT STARTED

---

## Phase 3 — Open-Fusion

Official repository:
UARK-AICV/OpenFusion

Commit:
86bdc1ab173a203e7157ab055ff1fc96c786d86a

Full Replica runs completed:

office0:
- 2000 frames
- Frame loop: ~121 sec
- Total wall time: ~166 sec
- ~16.51 FPS
- Exit code: 0

room0:
- 2000 frames
- Frame loop: ~164 sec
- Total wall time: ~213 sec
- ~12.14 FPS
- Exit code: 0

Outputs archived under:
outputs/openfusion_repro/office0/
outputs/openfusion_repro/room0/

---

## Phase 4 — ConceptGraphs

Official repository:
concept-graphs/concept-graphs

Commit:
93277a02bd89171f8121e84203121cf7af9ebb5d

Environment:
- Python 3.10.13
- PyTorch 2.0.1+cu118
- torchvision 0.15.2+cu118
- NumPy 1.24.3
- CUDA 11.8
- A100 80GB
- PyTorch3D 0.7.4
- Open3D 0.17.0
- GradSLAM installed
- ChamferDist installed

Replica ConceptGraphs dataset:
datasets/replica_conceptgraphs/

Exact layout:
<scene>/results/frameXXXXXX.jpg
<scene>/results/depthXXXXXX.png
<scene>/traj.txt

---

## ConceptGraphs RGB Reconstruction

Scene:
room0

Configuration:
- stride 5
- 400 frames
- image height 480
- image width 640

Result:
- Exit code 0
- Runtime ~55.6 sec
- RGB cloud successfully generated
- Point cloud shape: 7,754,935 points

---

## ConceptGraphs GSA

Grounded-SAM repository:
Grounded-Segment-Anything

Exact tested commit:
a4d76a2b55e348943cba4cd57d7553c354296223

GSA configuration:
- scene: room0
- class_set: none
- stride: 5
- 400 frames

Result:
- 400 detection files
- 400 visualization files
- classes: ['item']
- Full GSA run completed successfully
- No need to rerun

Important:
RAM/Tag2Text checkpoint/model mismatch was discovered, but these models are NOT required for class_set=none.
Do not patch or rerun them unless a later experiment explicitly requires RAM/Tag2Text.

---

## ConceptGraphs Mapping

First attempt failed because the repository's default configuration specifies:
match_method=sep_thresh

But the actual checked-out mapping implementation only supports:
match_method=sim_sum

The official README also uses:
match_method=sim_sum

Second mapping run used:
- scene_id=room0
- stride=5
- image_height=680
- image_width=1200
- gsa_variant=none
- match_method=sim_sum
- device=cuda
- save_pcd=true

Result:
- 400/400 frames completed
- Runtime: 10 minutes 43 seconds
- Full point cloud saved
- Post-processed point cloud saved
- Before filtering: 36 objects
- After filtering: 36 objects
- Before merging: 36 objects
- After merging: 20 objects

Final ConceptGraphs artifacts:
outputs/conceptgraphs_repro/room0/

Files:
- full_pcd_none_exp.pkl.gz (~38 MB)
- full_pcd_none_exp_post.pkl.gz (~35 MB)

Archive verification:
PASS

---

## Current Research Status

ConceptGraphs reproduction is complete for room0.

Open-Fusion reproduction is complete for office0 and room0.

The next research phase is Phase 5: Own Pipeline.

However, the project handoff/history does NOT contain a concrete technical specification for the proposed own algorithm.

Do NOT invent or falsely claim that an own algorithm was previously defined.

Current decision:
- Own pipeline design will be decided later.
- No own-pipeline implementation has been executed.
- outputs/my_pipeline/ is currently empty.

Potential future direction discussed (NOT YET FINALIZED):
A simple object-level open-vocabulary 3D mapping pipeline using:
RGB-D + poses
→ segmentation
→ CLIP/OpenCLIP features
→ 2D-to-3D lifting
→ object association
→ semantic feature fusion
→ natural-language object retrieval

Possible fusion comparison was discussed, but this is only a proposal and has NOT been approved or executed:
- latest observation
- cumulative mean
- confidence-weighted mean

Do NOT treat this proposed design as an experimental result or previously established project specification.

---

## Important Reproducibility Rules

- Never fabricate experimental results.
- Never claim an experiment succeeded until output confirms it.
- Do not rerun completed expensive experiments unnecessarily.
- Keep reproduction experiments separate from the own pipeline.
- For ablations, vary only the intended experimental variable.
- Preserve exact repository commits and configuration choices.
- Flag uncertainty rather than guessing.
- Do not reset intentional repository modifications without checking first.
- Current ConceptGraphs replica.yaml contains an intentional local modification.
- Current Grounded-SAM segment_anything/linter.sh has an unrelated local modification; do not reset it.
- Use isolated CUDA 11.8 at /content/cuda-11.8 for ConceptGraphs CUDA extensions.
- Do not switch ConceptGraphs to system CUDA 12.8.
- Do not downgrade/replace PyTorch 2.0.1+cu118.

---

## Immediate Next Step

No experiment should be started yet.

When continuing:
1. Decide/define the own pipeline.
2. Implement it in a dedicated location.
3. Test it on room0 first.
4. Preserve outputs under outputs/my_pipeline/.
5. Only then proceed to fusion ablation, evaluation, and baselines.

