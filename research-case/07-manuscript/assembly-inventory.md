# Manuscript Assembly Inventory

System: `KEYSTONE-MPP-F1`  
Artifact status: `DRAFT / PRE-MANUSCRIPT / PRE-AUTHORIZATION`  
Current serial gate: `INTAKE`  
Novelty: `UNRESOLVED`  
Feasibility: `UNASSESSED`  
Solution viability: `ASSERTED_ONLY`  
Acceptance readiness: `NOT_ASSESSABLE`

This inventory binds the current manuscript shell to its draft claim, table, figure, and diagram assets. It is a deterministic assembly aid only. It does not authorize confirmatory execution, external transfer, novelty clearance, feasibility promotion, or submission.

Final author order, corresponding-author designation, and exact affiliation wording remain deferred.

## Coverage summary

- Claim anchors in manuscript/matrix/graph: **3**
- Table identifiers referenced in manuscript: **8**
- Diagram identifiers with rendered assets: **8**
- Quantitative figures with rendered assets: **5**
- Manuscript-local image references: **13**
- Source-manifest entries verified by the alignment checker: **114**

Referenced figure identifiers without rendered manuscript assets: `F6`, `F7`, `F8`.

## Future-figure boundary

The current canonical INTAKE manuscript may reference `F6`, `F7`, and `F8` only as future confirmatory outputs. They must remain absent from the rendered manuscript asset set and the figure manifest until `REM-003` and `REM-004` are closed and canonical lineage exists.

## Claim map

| Claim | Draft status | Table targets | Figure targets | Diagram targets | Blocked by | Allowed wording |
| --- | --- | --- | --- | --- | --- | --- |
| `C001` | `BLOCKED` | `T1`, `T4` | `F1` | `D2` | `NOVELTY_UNRESOLVED; canonical counterexample manuscript artifact and signed independent closure absent` | `This paper studies|KEYSTONE defines|under the stated static catastrophic model` |
| `C002` | `AT_RISK` | `T3`, `T7` | `none` | `D1`, `D3`, `D4`, `D5`, `D8` | `Accountable authority and confirmatory environment are open; independent reproduction and external review are missing` | `internal prototype evidence shows|local reproducibility evidence records` |
| `C003` | `AT_RISK` | `T2`, `T3`, `T4`, `T5`, `T6`, `T7`, `T8` | `F1`, `F2`, `F3`, `F4`, `F5`, `F6`, `F7`, `F8` | `D1`, `D2`, `D3`, `D4`, `D5`, `D6`, `D7`, `D8` | `RID-C003-DEADLINE-001 absent; canonical robustness-and-boundaries.csv and negative-findings.csv are draft/preauthorization only; no authorized confirmatory rerun, independent reproduction, or external validation; F6-F8 remain future outputs` | `bounded internal evidence indicates|within the declared model|conditional on synchrony assumptions|selective withholding remains a limitation` |

## Table inventory

| Table | Draft role | Output binding |
| --- | --- | --- |
| `T1` | bounded strongest-prior-art matrix only; not novelty clearance | `t1_t8_package.tex` |
| `T2` | design comparator registry only; no measured superiority claim | `t2_proposed_vs_baselines.csv` |
| `T3` | frozen local conditions plus explicit missing distributed deadline profile | `t3_experimental_conditions.csv` |
| `T4` | preauthorization simulated result display only; numeric values remain source-bound and claim-capped | `t4_primary_results.csv` |
| `T5` | planned mechanism-isolation registry only; all rows missing and unexecuted | `t5_ablation_mechanism.csv` |
| `T6` | canonical robustness ledger plus separately classified exact and exploratory checks | `t6_robustness_boundaries.csv` |
| `T7` | local timing and gas observations only; distributed, operator, network, and external evidence blocked | `t7_real_world_feasibility.csv` |
| `T8` | negative findings and unresolved risks ledger with selective withholding preserved | `t8_negative_findings_risks.csv` |

## Figure inventory

| Figure | Status | Rendered SVG | Derivative PNG | Source data |
| --- | --- | --- | --- | --- |
| `F1` | `PRELIMINARY_PREAUTHORIZATION` | `../../prototype/results/figures/figure_1_theoretical_detection_bound.svg` | `prototype/results/figures/figure_1_theoretical_detection_bound.png` | `prototype/results/theoretical_bound.csv` |
| `F2` | `PRELIMINARY_PREAUTHORIZATION` | `../../prototype/results/figures/figure_2_iid_failure_sweep.svg` | `prototype/results/figures/figure_2_iid_failure_sweep.png` | `prototype/results/iid_failure_sweep.csv` |
| `F3` | `PRELIMINARY_PREAUTHORIZATION` | `../../prototype/results/figures/figure_3_domain_diversity.svg` | `prototype/results/figures/figure_3_domain_diversity.png` | `prototype/results/domain_diversity.csv` |
| `F4` | `PRELIMINARY_LIMITATION` | `../../prototype/results/figures/figure_4_selective_withholding_gap.svg` | `prototype/results/figures/figure_4_selective_withholding_gap.png` | `prototype/results/selective_withholding.csv` |
| `F5` | `PRELIMINARY_PREAUTHORIZATION` | `../../prototype/results/figures/figure_5_sampling_strategy.svg` | `prototype/results/figures/figure_5_sampling_strategy.png` | `prototype/results/sampling_strategy.csv` |

## Diagram inventory

| Diagram | Rendered SVG | Editable source | Alternate source |
| --- | --- | --- | --- |
| `D1` | `../../diagrams/01_system_architecture.svg` | `../../diagrams/01_system_architecture.mmd` | `../../diagrams/01_system_architecture.dot` |
| `D2` | `../../diagrams/02_property_separation.svg` | `../../diagrams/02_property_separation.mmd` | `../../diagrams/02_property_separation.dot` |
| `D3` | `../../diagrams/03_audit_sequence.svg` | `../../diagrams/03_audit_sequence.mmd` | `../../diagrams/03_audit_sequence.dot` |
| `D4` | `../../diagrams/04_dispute_sequence.svg` | `../../diagrams/04_dispute_sequence.mmd` | `../../diagrams/04_dispute_sequence.dot` |
| `D5` | `../../diagrams/05_state_machines.svg` | `../../diagrams/05_state_machines.mmd` | `../../diagrams/05_state_machines.dot` |
| `D6` | `../../diagrams/06_threat_model.svg` | `../../diagrams/06_threat_model.mmd` | `../../diagrams/06_threat_model.dot` |
| `D7` | `../../diagrams/07_sampling_domains.svg` | `../../diagrams/07_sampling_domains.mmd` | `../../diagrams/07_sampling_domains.dot` |
| `D8` | `../../diagrams/08_experiment_pipeline.svg` | `../../diagrams/08_experiment_pipeline.mmd` | `../../diagrams/08_experiment_pipeline.dot` |

## Blocking evidence

| Blocking item | Source |
| --- | --- |
| `RID-C003-DEADLINE-001` | `paper/tables/t1_t8_manifest.json` |
| `independent reproduction` | `paper/tables/t1_t8_manifest.json` |
| `external validation` | `paper/tables/t1_t8_manifest.json` |
| `NOVELTY_UNRESOLVED; canonical counterexample manuscript artifact and signed independent closure absent` | `research-case/07-manuscript/claim-evidence-matrix.csv` |
| `Accountable authority and confirmatory environment are open; independent reproduction and external review are missing` | `research-case/07-manuscript/claim-evidence-matrix.csv` |
| `RID-C003-DEADLINE-001 absent; canonical robustness-and-boundaries.csv and negative-findings.csv are draft/preauthorization only; no authorized confirmatory rerun, independent reproduction, or external validation; F6-F8 remain future outputs` | `research-case/07-manuscript/claim-evidence-matrix.csv` |
