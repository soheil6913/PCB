# Numerical evidence toolchain

Validated in the isolated environment used for P2.4-D-6:

- Python: 3.12.3
- gmpy2: 2.3.2
- MPFR: 4.2.2 (`gmpy2.mpfr_version()`)
- GMP: 6.3.0 (`gmpy2.mp_version()`)
- Node.js: v22.23.4
- project `tsx`: 4.20.6 from the separately supplied reference source worktree
- reference commit: `941262899a46e54cbf1a94a4da6dd528b8d36780`

The runner has no hardcoded checkout fallback. These environment variables are required:

- `PCB_SOURCE_WORKTREE`: absolute or resolvable path to the reference source checkout; it must contain `shared/engineering.ts`.
- `TSX_BIN`: explicit path to the `tsx` executable used to import the reference TypeScript module.
- `PCB_REFERENCE_COMMIT`: must equal the pinned reference commit above.

Reproduction from a clean checkout of this evidence branch:

```bash
python3.12 -m venv /tmp/p24d6-venv
/tmp/p24d6-venv/bin/pip install --requirement tools/numerical-evidence/requirements.txt
PCB_SOURCE_WORKTREE=/path/to/reference/source \
TSX_BIN=/path/to/reference/source/node_modules/.bin/tsx \
PCB_REFERENCE_COMMIT=941262899a46e54cbf1a94a4da6dd528b8d36780 \
/tmp/p24d6-venv/bin/python tools/numerical-evidence/run_vectors.py \
  > /tmp/p24d6-results.json
```

The runner validates the source file and executable before capture and records the resolved source path and reference commit in JSON. The package version is pinned, but a package hash and architecture-specific wheel lock are not included; CI provisioning remains a separate reproducibility gap. Existing project CI workflows are unchanged.
