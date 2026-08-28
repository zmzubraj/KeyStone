# Diagram Catalogue

## D1 — System architecture

**Files:** `diagrams/01_system_architecture.*`  
**Paper use:** Figure 1.  
**Purpose:** separate ciphertext DA, readiness audit, authorization, threshold release, and re-execution.

## D2 — Property separation/lattice

**Files:** `diagrams/02_property_separation.*`  
**Paper use:** early model figure.  
**Purpose:** show CA, VSR, AKR, AD, DDL, PAC and their composition into DKA.

## D3 — Audit sequence

**Files:** `diagrams/03_audit_sequence.*`  
**Paper use:** protocol section.  
**Purpose:** commit → beacon → sample → canary → partial/proof → deadline → result/evidence.

## D4 — Dispute sequence

**Files:** `diagrams/04_dispute_sequence.*`  
**Paper use:** protocol section.  
**Purpose:** challenge authorization, confidential partial release, threshold combination, re-execution, verdict.

## D5 — State machines

**Files:** `diagrams/05_state_machines.*`  
**Paper/artifact use:** implementation appendix.  
**Purpose:** epoch, audit, and dispute lifecycle transitions.

## D6 — Threat model

**Files:** `diagrams/06_threat_model.*`  
**Purpose:** map adversary classes to controls and residual risks.

## D7 — Sampling and failure domains

**Files:** `diagrams/07_sampling_domains.*`  
**Purpose:** compare uniform and domain-stratified sampling under a complete domain outage.

## D8 — Experiment pipeline

**Files:** `diagrams/08_experiment_pipeline.*`  
**Purpose:** show frozen configs, simulation, metrics, figures, and paper evidence.

## Editing guidance

- `.dot` is the authoritative rendered source.
- `.mmd` is supplied for Mermaid-based documentation tools.
- `.svg` is preferred for papers and slides.
- `.png` is convenient for previews.
- Captions should state assumptions rather than implying unconditional guarantees.
