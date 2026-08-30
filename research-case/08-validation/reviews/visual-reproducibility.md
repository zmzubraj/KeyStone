# Developmental visual and reproducibility review

Status: `DRAFT / AI-ASSISTED / NOT INDEPENDENT VERIFICATION`

## Verdict

The package has strong source traceability: quantitative figures are linked to
versioned CSV and generator code, diagrams retain Mermaid source, tables remain
editable, and the manuscript source manifest records hashes. These are good
internal reproducibility foundations, not publication QA or independent
reproduction.

## Findings

- The current `C003` claim-to-figure contract names `F1-F8`, whereas the visual
  ledger and rendered manuscript currently bind only `F1-F5`. The manuscript
  correctly calls `F6-F8` future outputs, but the matrix must not be read as
  present support. Those figures require canonical result ledgers and lineage,
  or the final claim-to-figure contract must be narrowed.
- The canonical draft `05-analysis/results/negative-findings.csv` now binds the
  selective-withholding limitation rows to their frozen source and lineage.
  It remains unauthorized, non-independent, simulated, and capped at `V0
  ASSERTED`; neither it nor the editable T8 table substitutes for confirmatory
  evidence or the still-future F6-F8 outputs.
- The canonical draft `05-analysis/results/robustness-and-boundaries.csv` now
  binds all frozen IID and matched-policy sampling cells to their source hashes,
  experiment IDs, seeds, and trial counts. It deliberately excludes the
  evidence-entangled correlated-domain family plus Markov,
  selective-withholding, and deadline rows. This is a draft lineage surface,
  not final figure support or confirmatory robustness evidence.
- `06-visuals/visual-ledger.csv` marks every figure and diagram as draft and
  records automated proxy warnings with contextual CVD, assistive-technology,
  print, human, and venue review pending.
- Canonical quantitative format is SVG; PNG files are derivative previews and
  must not silently replace vector submission assets.
- Final-size legibility at the intended column width is not approved, and the
  derivative PNG proxy is below a 300-PPI print threshold.
- Captions generally preserve simulation/model boundaries, but final venue-
  specific panel ordering, abbreviations, units, denominators, and source-data
  links still require rendered-page review.
- Same-host isolated-copy reproduction is mechanical evidence only. No external
  clean-machine rerun, independent environment reconstruction, or hermetic
  submission build is final.
- Deadline-bearing workflow diagrams are protocol maps, not evidence of observed
  transport or deadline performance; their final captions must say so directly.

## Required resolution

After results freeze, regenerate all figures and T1-T8 tables from canonical
data, rehash the source manifest, perform grayscale/CVD/final-size and screen-
reader checks, inspect every rendered PDF page, and obtain an independently
executed reproduction report. Preserve Mermaid and plotting sources and log all
intentional visual transformations. This unsigned review promotes no
reproducibility, visual, or submission gate.
