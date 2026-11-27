# Numerical evidence toolchain

Validated in the isolated temporary environment used for P2.4-D-5:

- Python: 3.12.3
- gmpy2: 2.3.2
- MPFR: 4.2.2 (`gmpy2.mpfr_version()`)
- GMP: 6.3.0 (`gmpy2.mp_version()`)
- Node.js: v22.23.4
- project `tsx`: 4.20.6 from the source worktree

Reproduction outside project dependencies:

```bash
python3.12 -m venv /tmp/p24d5-venv
/tmp/p24d5-venv/bin/pip install --requirement tools/numerical-evidence/requirements.txt
/tmp/p24d5-venv/bin/python tools/numerical-evidence/run_vectors.py > /tmp/p24d5-results.json
```

Set `PCB_SOURCE_WORKTREE` and `TSX_BIN` when the reference source is elsewhere. The package wheel/hash is not pinned in this repository; CI provisioning remains an open reproducibility gap.
