# Excluded from this backup

This repo backs up the `code/` directory from the project's Google Drive
folder (https://drive.google.com/drive/folders/1nFUDnOMdnBGV-g-H6MKEfSSq_1DqyKVp).
The following were intentionally left out and remain on Drive only.

## Non-code Drive folders (not downloaded)

The Drive folder root also contains these top-level items, none of which
were pulled into this backup:

- `datasets/` — raw Replica benchmark dataset (replica, replica_conceptgraphs,
  replica_semantic_gt, replica_v1_0 as a 17-part tar.gz), likely 100GB+
- `outputs/` — experiment run outputs (conceptgraphs_repro, my_pipeline,
  openfusion_repro)
- `production_backup/` — a separate run snapshot (cache, results,
  session_checkpoint, manifest JSONs)
- `logs/` — run logs (session_checkpoints, colab_environment.json)
- `contrib/` — a separate cache/code/logs/results tree

`checkpoints/` (openclip, sam, seem) was also on the Drive root but its
subfolders were empty — no files to back up there.

Within `code/OpenFusion/`, three embedded dataset copies were also skipped:
`replica_office0/`, `replica_room0/`, and `sample/replica/` (frame-by-frame
image sequences from the Replica benchmark, duplicated from `datasets/`).

## Model checkpoint files too large for GitHub

GitHub enforces a hard 2GB-per-file limit on Git LFS objects (separate from
and stricter than the LFS storage quota). These files exceed it and are
excluded via `.gitignore`:

| File | Size | Original path |
|---|---|---|
| `ram_swin_large_14m.pth` | 5.3GB | `code/Grounded-Segment-Anything/Tag2Text/` |
| `tag2text_swin_14m.pth` | 4.2GB | `code/Grounded-Segment-Anything/Tag2Text/` |
| `sam_vit_h_4b8939.pth` | 2.4GB | `code/Grounded-Segment-Anything/` |

These are standard pretrained weights for RAM (Recognize Anything Model),
Tag2Text, and SAM (ViT-H) respectively, and can be re-downloaded from their
original model hubs, or fetched again from the source Drive folder if still
shared.

## Model checkpoint files included via Git LFS

These fit under the 2GB limit and are tracked normally via Git LFS:

- `code/Grounded-Segment-Anything/groundingdino_swint_ogc.pth` (662MB)
- `code/OpenFusion/openfusion/zoo/xdecoder_seem/checkpoints/seem_focall_v1.pt` (1.3GB)
- `code/OpenFusion/assets/output.gif` (72MB, demo asset, LFS for convenience)

## Upstream `.git` history

Each of the 7 repos under `code/` was uploaded to Drive with its own
embedded `.git` folder (the upstream project's commit history, not this
project's own history). These were deleted before this backup's git init,
since nested `.git` folders would otherwise be tracked as broken submodule
references rather than the actual files being backed up.
