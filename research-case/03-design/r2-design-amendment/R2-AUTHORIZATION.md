# KEYSTONE R2 authorization record

Date: 2026-10-21. Accountable human: the author.

The author reviewed `R2-DESIGN-AMENDMENT-DRAFT.md` and approved decisions D1 to D6 as recommended, in the working session of 2026-10-21, with the instruction to freeze the design and begin.

Approved decisions:
- D1: ristretto255 via `rbcl` after a static supply-chain review; fall back to a ctypes wrapper over libsodium if the review fails.
- D2: batched verification as a secondary variant.
- D3: keep ffdhe2048/3072 as the like-for-like baseline with the W11 fixes.
- D4: include the domain-shock extension in W1.
- D5: primary testbed deadline frozen as a formula, computed before the testbed runs.
- D6: add the W1 theorem to the paper and base Definition 7 on PAC+.

This record does not change the program state: INTAKE with novelty UNRESOLVED.
