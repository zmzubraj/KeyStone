# D1 supply-chain review: `rbcl` (static, nothing installed or executed)

Date: 2026-10-21. Scope: decision D1 of `r2-design-freeze.json`. Method: metadata from the PyPI JSON API; files downloaded into an isolated scratch directory and checked against PyPI's published SHA-256 digests; static reading of all Python sources; extraction and static inspection (`file`, `otool -L`, `nm`, `strings`) of the embedded native library. No package was installed and no code from the packages was run.

## Packages reviewed

| Package | Version | File | SHA-256 (PyPI) | Notes |
|---|---|---|---|---|
| rbcl | 1.1.2 (2025-12-05) | `rbcl-1.1.2-cp313-abi3-macosx_11_0_arm64.whl` | matched | MIT, Nth Party; requires `barriers~=1.1` |
| rbcl | 1.1.2 | `rbcl-1.1.2.tar.gz` (sdist) | matched | build script only |
| barriers | 1.2.0 (2023-10-28) | `barriers-1.2.0-py3-none-any.whl` | matched | 596 lines; latest 2.0.0 is outside `~=1.1` |

## Findings

1. **Embedded native library.** `rbcl/_sodium.py` holds a hex-encoded Mach-O arm64 dylib (387,456 bytes, SHA-256 `87e460d62a4b1291058f3b97c72fd9d4ead1492023a4237cd5fe68ae8ef7a21b`). At import it is written to a new temporary file (never deleted) and loaded with `ctypes.cdll.LoadLibrary`.
2. **The binary is libsodium and nothing else.** Static inspection:
   - It links only `libSystem`.
   - It exports 609 symbols, all `crypto_*`, `sodium_*` or `randombytes_*`.
   - It imports only libc memory, file, thread, time and random-device functions. No sockets, no `exec*`, no `dlopen`, no environment reads.
   - No suspicious strings (URLs, shells, wallets, keychains, tokens).
   - The version string is **libsodium 1.0.18** (2019).
3. **Build script.** `_sodium_build.py` downloads libsodium from the official GitHub releases and runs `make`. It runs only when building from the sdist. Installing the pre-built wheel does not execute it.
4. **Validation stripping.** `rbcl.py` sets `VALIDATION_ENABLED = 'site-packages' not in <path>`. The `barriers` decorator then recompiles marked functions without their validation statement. In a normal installation, `crypto_scalarmult_ristretto255_allow_scalar_zero` therefore skips its point-validity check.
5. **`barriers` `exec`.** One `exec(compile(ast, ...))` that re-executes the decorated library function's own source with marked statements removed. No external input is executed.
6. **Known advisory.** CVE-2025-69277 concerns `crypto_core_ed25519_is_valid_point` and is fixed in libsodium 1.0.20 (January 2026). 1.0.18 is very likely in the affected range. The advisory concerns the ed25519 API, not the ristretto255 functions KEYSTONE needs. This scoping is our inference from the advisory text.
7. **Scalar semantics.** rbcl's docstring describes scalar "clamping" for `crypto_scalarmult_ristretto255`. Bit clamping of low bits would break Shamir and Lagrange arithmetic, so this must be ruled out by tests.

## Verdict: CONDITIONAL PASS

Option A (`rbcl`) may be used under all of these conditions:

1. Install from the wheel only (no sdist build), pinned to `rbcl==1.1.2` and `barriers==1.2.0` with hashes in `uv.lock`.
2. A test asserts the SHA-256 of the embedded library above, so an upgrade or tampering fails loudly.
3. KEYSTONE validates every received point itself with `crypto_core_ristretto255_is_valid_point` and does not rely on rbcl's internal checks.
4. Only the ristretto255, scalar and `randombytes` APIs are used. No ed25519 function is called.
5. Correctness tests run before any measurement: scalar-multiplication linearity (`(a+b)P = aP + bP`, `(ab)P = a(bP)` for random full-range scalars) and Lagrange reconstruction. If clamping is observed, rbcl is rejected and option B is used.
6. Benchmark and testbed harnesses delete the temporary library files rbcl creates, or run in a dedicated temporary directory.

## Residual risk

The native binary was built by a third party and cannot be reproduced bit for bit here, so this review is static only. Its libsodium version (1.0.18) is older than the current release. Option B (a ctypes wrapper over a current libsodium from a system package manager) removes both points at the cost of a machine-level installation, and remains the fallback.

## Post-install correctness results (2026-10-21)

Installed from the pinned wheel into the separate R2 environment `prototype/r2/` (its `uv.lock` hashes equal the reviewed files; embedded library SHA-256 equal to the value above). See deviation-log entry 2 for why R2 has its own environment. `prototype/r2/tests/test_r2_ristretto.py` (40 tests) passes. Two findings while writing it:

- **Identity accepted by libsodium.** `crypto_core_ristretto255_is_valid_point` accepts the all-zero encoding of the identity element. KEYSTONE's `validate_point` now rejects it explicitly, so an identity partial, canary or public share is never accepted.
- **Loader lookup.** `rbcl._sodium` as an attribute is the loaded `ctypes` library, not the loader module, so the first version of the temp-file cleanup silently did nothing. The module is now taken from `sys.modules`, and a test asserts the temporary library is gone.

No scalar clamping was observed: small multiples and full-range linearity hold, and Lagrange reconstruction with 22 of 32 partials recovers `xP` while 21 do not.
