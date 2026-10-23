#!/usr/bin/env bash
# Build the JCS submission bundle: a flattened, standalone LaTeX source zip that
# is proven to compile on its own, plus the anonymized artifact zip.
# Usage: paper/jcs/make_submission.sh <anonymized-artifact-dir>
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ARTIFACT_DIR="${1:?usage: make_submission.sh <anonymized-artifact-dir>}"
OUT="$HERE/submission"
STAGE="$(mktemp -d)"
SRC="$STAGE/KEYSTONE_JCS_source"
mkdir -p "$SRC/tables" "$SRC/figures"

# 1. Flatten: copy sources and rewrite ../r1 paths to local folders.
cp "$HERE/KEYSTONE_JCS.tex" "$HERE/sagej.cls" "$HERE/endnotes.sty" "$HERE/references.bib" "$SRC/"
cp "$HERE"/../r1/tables/*.tex "$SRC/tables/"
cp "$HERE"/tables/*.tex "$SRC/tables/"          # JCS-specific derived tables override
cp "$HERE"/../r1/figures/*.pdf "$SRC/figures/"
cp "$HERE"/figures/*.pdf "$SRC/figures/"          # JCS-specific derived figures override
sed -i '' -e 's#\.\./r1/##g' "$SRC/KEYSTONE_JCS.tex"
if grep -q '\.\./r1' "$SRC/KEYSTONE_JCS.tex"; then echo "unflattened path left" >&2; exit 1; fi

# 2. Prove the flattened source compiles standalone, then keep the .bbl for Sage.
(cd "$SRC" && latexmk -pdf -interaction=nonstopmode -halt-on-error KEYSTONE_JCS.tex >/dev/null)
cmp -s <(pdftotext "$SRC/KEYSTONE_JCS.pdf" -) <(pdftotext "$HERE/KEYSTONE_JCS.pdf" -) \
  && echo "standalone build text identical to main build" \
  || { echo "standalone build differs from main build" >&2; exit 1; }
(cd "$SRC" && latexmk -c >/dev/null && rm -f KEYSTONE_JCS.pdf)

# 3. Zip source and artifact (artifact without Python caches or OS files).
rm -f "$OUT/KEYSTONE_JCS_source.zip" "$OUT/KEYSTONE_artifact_anonymized.zip"
(cd "$STAGE" && zip -qr "$OUT/KEYSTONE_JCS_source.zip" KEYSTONE_JCS_source)
find "$ARTIFACT_DIR" \( -name __pycache__ -o -name .pytest_cache \) -type d -prune -exec rm -rf {} +
find "$ARTIFACT_DIR" -name .DS_Store -delete
(cd "$(dirname "$ARTIFACT_DIR")" && zip -qr "$OUT/KEYSTONE_artifact_anonymized.zip" "$(basename "$ARTIFACT_DIR")")
cp "$HERE/KEYSTONE_JCS.pdf" "$OUT/KEYSTONE_JCS_anonymized.pdf"

# 4. Supplementary material (full proofs, moved figures and tables), anonymized.
(cd "$HERE/supplement" && latexmk -pdf -interaction=nonstopmode -halt-on-error KEYSTONE_supplement.tex >/dev/null)
cp "$HERE/supplement/KEYSTONE_supplement.pdf" "$OUT/KEYSTONE_supplement_anonymized.pdf"
rm -rf "$STAGE"
ls -la "$OUT"
