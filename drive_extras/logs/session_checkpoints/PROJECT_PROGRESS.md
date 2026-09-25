# Research Project Checkpoint — 2026-09-13

## Current milestone
ConceptGraphs reproduction is in progress.
Open-Fusion reproduction is complete.

## Completed
- Open-Fusion reproduction completed for office0 and room0.
- Replica data prepared in Open-Fusion and ConceptGraphs-compatible layouts.
- ConceptGraphs RGB sanity reconstruction completed for room0.
- Grounded-SAM exact repository checkout prepared.
- Grounded-SAM dependencies and checkpoints prepared.
- Grounded-SAM smoke test completed successfully.
- Full ConceptGraphs GSA generation completed successfully for room0.

## ConceptGraphs GSA result
- Scene: room0
- class_set: none
- stride: 5
- Processed frames: 400
- Detection files: 400
- Visualization files: 400
- Classes: ['item']
- First detection: frame000000.pkl.gz
- Last detection: frame001995.pkl.gz
- Runtime: 44:52
- Status: COMPLETE

## Important paths
Project:
 /content/drive/MyDrive/research_project

ConceptGraphs:
 /content/drive/MyDrive/research_project/code/ConceptGraphs

ConceptGraphs Replica:
 /content/drive/MyDrive/research_project/datasets/replica_conceptgraphs

Grounded-SAM:
 /content/drive/MyDrive/research_project/code/Grounded-Segment-Anything

ConceptGraphs environment:
 /content/miniconda3/envs/conceptgraph

GSA outputs:
 /content/drive/MyDrive/research_project/datasets/replica_conceptgraphs/room0/gsa_detections_none
 /content/drive/MyDrive/research_project/datasets/replica_conceptgraphs/room0/gsa_vis_none
 /content/drive/MyDrive/research_project/datasets/replica_conceptgraphs/room0/gsa_classes_none.json

## Environment
- Python 3.10.13
- PyTorch 2.0.1+cu118
- torchvision 0.15.2+cu118
- NumPy 1.24.3
- CUDA toolkit: /content/cuda-11.8
- GPU: NVIDIA A100-SXM4-80GB
- Open3D 0.17.0
- GradSLAM 0.1.0
- PyTorch3D 0.7.4
- ChamferDist 1.0.3
- Hydra 1.3.2
- OmegaConf 2.3.1
- supervision 0.14.0
- transformers 4.30.2
- open_clip_torch 3.3.0
- fairscale 0.4.13

## Important compatibility findings
- Use CUDA 11.8 at /content/cuda-11.8 for ConceptGraphs CUDA extensions.
- Use GCC/G++ 11.
- Do not use /usr/local/cuda (CUDA 12.8).
- supervision 0.14.0 is required by the ConceptGraphs code path used here.
- transformers 4.30.2 is used with PyTorch 2.0.1.
- RAM/Tag2Text checkpoint/model-loader mismatch was identified, but it is irrelevant to the current official class_set=none reproduction path.

## Last mapping attempt
The first mapping command incorrectly used argparse-style --arguments.
It failed before mapping started.

Hydra was then installed and verified:
- Hydra 1.3.2
- OmegaConf 2.3.1
- HYDRA IMPORT: PASS

The actual cfslam_pipeline_batch.py interface is Hydra key=value overrides.

## EXACT NEXT COMMAND
This has NOT yet been run:

ENV=/content/miniconda3/envs/conceptgraph
REPO=/content/drive/MyDrive/research_project/code/ConceptGraphs
REPLICA_ROOT=/content/drive/MyDrive/research_project/datasets/replica_conceptgraphs
CONFIG=$REPO/conceptgraph/dataset/dataconfigs/replica/replica.yaml

export CUDA_HOME=/content/cuda-11.8
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}
export CC=/usr/bin/gcc-11
export CXX=/usr/bin/g++-11

cd "$REPO"

"$ENV/bin/python"   "$REPO/conceptgraph/slam/cfslam_pipeline_batch.py"   dataset_root="$REPLICA_ROOT"   dataset_config="$CONFIG"   scene_id=room0   start=0   end=-1   stride=5   image_height=680   image_width=1200   gsa_variant=none   device=cuda   save_pcd=true

## Current project state
- Phase 0: complete
- Phase 1: complete
- Phase 2: complete
- Open-Fusion reproduction: complete
- ConceptGraphs RGB sanity reconstruction: complete
- ConceptGraphs GSA generation: complete for room0
- ConceptGraphs mapping: NOT STARTED
- Own pipeline: NOT STARTED
- Fusion ablation: NOT STARTED
- Closed-vocabulary baseline: NOT STARTED
- Evaluation/results: NOT STARTED

## Important research rule
Do not fabricate experimental results.
Runtime, file counts, point counts, or state sizes are artifact properties, not quality results.
