# Open Vocabulary 3D Scene Mapping for Natural Language Object Localization

Backup of the Google Drive project folder for this research project (Replica scenes,
OpenFusion / ConceptGraphs reproductions, and a fusion-condition experiment).
Everything here was copied from the Drive folder; this file summarises only what the
backed-up notes, configs and result files actually say.

## What was done (from the project notes and result files)

Notes: `drive_extras/logs/session_checkpoints/PROJECT_PROGRESS.md` and
`PROJECT_PROGRESS_LATEST.md` (both dated 2026-09-13).

1. **Environment**: Colab + Drive, Python 3.10.13, PyTorch 2.0.1+cu118, CUDA 11.8,
   NVIDIA A100 80GB, PyTorch3D 0.7.4, Open3D 0.17.0, GradSLAM, ChamferDist.
   Full lists: `drive_extras/logs/session_checkpoints/` (`conceptgraph_environment.yml`,
   `conceptgraph_pip_freeze.txt`, `environment_variables.txt`, `git_state.txt`).
2. **Replica data** prepared in OpenFusion and ConceptGraphs layouts (not included, see below).
3. **OpenFusion reproduction** (UARK-AICV/OpenFusion, commit `86bdc1ab...`, vlfusion with SEEM):
   full 2000-frame runs on Replica `office0` (about 16.5 FPS) and `room0` (about 12.1 FPS), exit code 0.
   Outputs: `drive_extras/outputs/openfusion_repro/{office0,room0}/` (`run.log`,
   `reproduction_metadata.txt`, `semantic_pc.ply`, `vlfusion.npz` as split chunks).
4. **ConceptGraphs reproduction** on `room0` (commit `93277a02...`, Grounded-SAM commit `a4d76a2b...`,
   stride 5, 400 frames, `class_set=none`, `match_method=sim_sum`): 36 objects, 20 after merging.
   Outputs: `drive_extras/outputs/conceptgraphs_repro/room0/*.pkl.gz`.
5. **Fusion-condition experiment (F1, F2, F3)** on `office0`, `office2`, `room0`, completed
   2026-09-17 according to `production_backup/master_state.json`. Setup from
   `production_backup/results/final/final_metrics_summary.json` and
   `session_checkpoint/production_config.json`: voxel size 0.05 m, frame stride 10,
   SAM ViT-H masks, OpenCLIP ViT-L-14 (`laion2b_s32b_b82k`) features (768-d), zero-shot
   classification with the prompt "a photo of a <class name>", scored against Replica semantic
   ground truth (101 classes).

### Headline results (`drive_extras/production_backup/results/final/headline_results.csv`)

| scene | condition | voxels | accuracy | mIoU |
|---|---|---|---|---|
| office0 | F1 | 36793 | 0.1550 | 0.0617 |
| office0 | F2 | 36793 | 0.1578 | 0.0626 |
| office0 | F3 | 36793 | 0.2343 | 0.0561 |
| office2 | F1 | 52057 | 0.3944 | 0.0570 |
| office2 | F2 | 52057 | 0.3961 | 0.0575 |
| office2 | F3 | 52057 | 0.4061 | 0.0527 |
| room0 | F1 | 62641 | 0.2659 | 0.0780 |
| room0 | F2 | 62641 | 0.2670 | 0.0789 |
| room0 | F3 | 62641 | 0.3254 | 0.0724 |

Mean over the three scenes (`aggregate_statistics.json`): accuracy F1 0.272, F2 0.274, F3 0.322;
mIoU F1 0.0656, F2 0.0663, F3 0.0604. Figures: `accuracy_comparison.png`, `miou_comparison.png`.

## Caveats

- **F1/F2/F3 are not defined in any backed-up file.** They appear only as condition names in the
  configs, results and code. The 2026-09-13 notes float "latest observation, cumulative mean,
  confidence-weighted mean" as an unapproved proposal; do not assume that is the mapping.
  The backed-up `production_worker.py` (`drive_extras/production_backup/session_checkpoint/code/`
  and `drive_extras/contrib/code/`) is only the per-frame extraction stage: it writes the
  observation cache (`cache/<scene>/frames/*.npz`) and states that it "does NOT compute final
  RQ1/RQ2 metrics". The fusion and evaluation code that produced F1/F2/F3 is not among the files
  found on Drive, so if it exists elsewhere (for example a Colab notebook), it is not backed up here.
- The 2026-09-13 notes say the own pipeline had not started; the F1/F2/F3 results are dated
  later (2026-09-17), so the notes predate that work.
- The notes state that RAM/Tag2Text checkpoints mismatched but are not needed for `class_set=none`.

## Repository layout

- `code/`: the seven code repos from the Drive folder (chamferdist, ConceptGraphs, gradslam,
  Grounded-Segment-Anything, OpenFusion, pytorch3d, Recognize_Anything-Tag2Text). Each repo's original
  `.git` folder is kept as `_upstream_git/` (renamed so git does not treat it as a submodule);
  large pack files are split, see `drive_extras/REASSEMBLE.md`.
- `drive_extras/logs`, `production_backup`, `contrib`, `outputs`: the non-code folders from Drive.
- `drive_extras/REASSEMBLE.md`, `SPLIT_FILES_SHA256.txt`: how to rebuild files split for GitHub's 100MB limit.
- `DRIVE_MANIFEST.csv`: every file on the Drive folder and its status here.
- `EXCLUDED_FROM_BACKUP.md`: what is not in this repo, and why.
