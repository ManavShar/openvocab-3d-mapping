# Reassembling split files

GitHub rejects files over 100MB, so files larger than that were cut into
90 MiB chunks named `<original name>.part000`, `.part001`, ... in the same
folder as the original path. To rebuild one:

    cat path/to/file.npz.part* > path/to/file.npz        # Linux / macOS / Git Bash
    copy /b path\to\file.npz.part000+path\to\file.npz.part001 path\to\file.npz   # Windows cmd (list all chunks in order)

Then verify against `SPLIT_FILES_SHA256.txt` in this folder:

    sha256sum path/to/file.npz

Identical files that existed in several Drive folders (for example the fusion
results under `production_backup/results/final`, `production_backup/results`
and `production_backup/session_checkpoint/results`) are stored once by git; their
chunks share the same content.

Files split this way: the fusion result arrays `F1/F2/F3.npz` under
`production_backup/`, `outputs/openfusion_repro/*/vlfusion.npz`, and the upstream
git packs under `code/OpenFusion/_upstream_git/` and
`code/Grounded-Segment-Anything/_upstream_git/`.
