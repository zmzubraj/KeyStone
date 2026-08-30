#!/usr/bin/env python3
"""Render D1 and D5-D8 as deterministic, source-bound local derivatives.

Canonical Mermaid sources remain authoritative.  The SVGs are deliberately
simple publication derivatives; the PNGs are local Chrome previews.  Neither
format is scientific evidence or independent verification.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import struct
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
RENDERER_PATH = Path(__file__).resolve()
DEFAULT_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
DEFAULT_RECEIPT = ROOT / "diagrams" / "dense_diagrams.render.json"


class DiagramSpec(NamedTuple):
    code: str
    slug: str
    title: str
    description: str
    width: int
    height: int
    source_sha256: str
    semantic_tokens: tuple[str, ...]
    output_tokens: tuple[str, ...]

    @property
    def source(self) -> Path:
        return ROOT / "diagrams" / f"{int(self.code[1:]):02d}_{self.slug}.mmd"

    @property
    def svg(self) -> Path:
        return self.source.with_suffix(".svg")

    @property
    def png(self) -> Path:
        return self.source.with_suffix(".png")


SPECS = {
    "D1": DiagramSpec(
        "D1", "system_architecture", "KEYSTONE system architecture",
        "Architecture diagram separating ciphertext availability, policy and bulletin-board coordination, authorized dispute release, threshold combination, private re-execution, and final dispute verdict generation.",
        1600, 1320, "97db93e7fdbd27084d42e18a51363d6ec60aef54e1d449d301bc8502f3dcce08",
        (
            "ciphertext record", "K_r encapsulated under epoch PK_e", "sampled canary challenge",
            "partial + DLEQ proof", "valid / invalid / timeout evidence", "authorization + deadline",
            "confidential release request", "at least t verified partials", "recovered record key",
            "Private Re-execution", "Dispute Verdict",
        ),
        ("Ciphertext DA Layer", "Threshold Custodian", "Authorized Verifier", "Private Re-execution", "Dispute Verdict"),
    ),
    "D5": DiagramSpec(
        "D5", "state_machines", "Epoch, audit, and dispute state machines",
        "State-machine view of the KEYSTONE epoch lifecycle together with the audit and dispute lifecycles, showing the allowed transitions rather than implying stronger guarantees than the protocol defines.",
        1600, 1440, "ffe65f9f953c11270c4e661f108eacec56e0bf430a80c89f866a94a9affd8dc0",
        (
            "CREATED --> ACTIVE: roster + commitments", "ACTIVE --> REFRESHING: scheduled refresh",
            "REFRESHING --> ACTIVE: valid refreshed shares", "ACTIVE --> RETIRED: challenge window closed",
            "COMMITTED --> SAMPLED: beacon", "SAMPLED --> OPEN: canary posted",
            "OPEN --> PASSED: at least q valid by deadline", "OPEN --> FAILED: invalid or missing at deadline",
            "REQUESTED --> AUTHORIZED: policy accepts", "AUTHORIZED --> COLLECTING",
            "COLLECTING --> OPENED: at least t valid partials", "COLLECTING --> EXPIRED: deadline",
            "OPENED --> RESOLVED: verdict",
        ),
        ("CREATED", "REFRESHING", "RETIRED", "COMMITTED", "PASSED", "FAILED", "REQUESTED", "OPENED", "EXPIRED", "RESOLVED"),
    ),
    "D6": DiagramSpec(
        "D6", "threat_model", "Threat model, controls, and residual risk",
        "Threat-model diagram mapping adversary or fault classes to the controls the prototype applies and to the residual risks that remain outside the paper's claim boundary.",
        1600, 1390, "7494a0ccf3d418229c66c381ad68eb5c892b394d0e04231cb44439c37122d0f0",
        (
            "Invalid partial", "Feldman plus DLEQ verification", "Crypto soundness assumption",
            "Non-response or churn", "Public deadline and response commitment", "Partial synchrony assumption",
            "Equivocation", "Context-bound signed commitments", "Identity correctness",
            "Correlated outage", "Domain diversity and stratified sampling", "Domain labels may be dishonest",
            "Selective withholding", "Counterexample experiment and optional hidden request class", "Audits do not prove future cooperation",
            "Early key-release collusion", "Threshold, rotation, policy gate", "Fewer than t collude before authorization",
        ),
        ("Invalid partial", "Non-response or churn", "Selective withholding", "Audits do not prove", "future cooperation", "Fewer than t collude"),
    ),
    "D7": DiagramSpec(
        "D7", "sampling_domains", "Uniform and domain-stratified sampling under domain outage",
        "Illustration of a 32-member committee partitioned across four fault domains with one domain offline, contrasting uniform sampling with domain-stratified sampling for correlated-failure detection.",
        1600, 1080, "d1d1c6ca8a5898971505901e95a9ef5dcd75424db906c583c29967cd45b09571",
        (
            "Domain A: 8 online", "Domain B: 8 online", "Domain C: 8 offline", "Domain D: 8 online",
            "Uniform sample s=8: may miss or under-sample a failed domain",
            "Stratified sample s=8: two samples per domain, complete outage observed",
            "A --> U", "D --> U", "A --> S", "B --> S", "C --> S", "D --> S",
        ),
        ("Domain A", "Domain B", "Domain C", "OFFLINE", "Uniform sample", "Stratified sample", "complete outage observed"),
    ),
    "D8": DiagramSpec(
        "D8", "experiment_pipeline", "Reproducible minimum publishable prototype pipeline",
        "Pipeline diagram linking frozen configuration, adversarial simulation, metrics, figures, and paper-ready evidence so the prototype outputs remain traceable to the declared experimental inputs.",
        1600, 1260, "9c49604423fef3341b0ab25be9153a03aef9b7a0dfe14dbb4e22a7488d1406d6",
        (
            "Frozen config: n,t,s,q,domains,seeds", "Crypto unit tests", "End-to-end audit and dispute demo",
            "Adversarial simulator", "Microbenchmarks", "Versioned CSV/JSON and manifest",
            "Publication figures", "Claim-evidence matrix", "MPP paper", "Publication success gates",
            "C[Frozen config: n,t,s,q,domains,seeds] --> U[Crypto unit tests]",
            "C --> D", "C --> S", "C --> B", "U --> R", "D --> R", "S --> R", "B --> R",
            "R --> F", "R --> M", "F --> P", "M --> P", "P --> G",
        ),
        ("Frozen config", "Crypto unit tests", "Adversarial simulator", "Versioned CSV/JSON", "Claim-evidence matrix", "Publication success gates"),
    ),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def validate_source(spec: DiagramSpec, source: str) -> None:
    for token in spec.semantic_tokens:
        if token not in source:
            raise ValueError(f"{spec.code} missing semantic anchor: {token}")
    digest = sha256_bytes(source.encode("utf-8"))
    if digest != spec.source_sha256:
        raise ValueError(f"{spec.code} source drift: expected {spec.source_sha256}, got {digest}")


def _text(x: int, y: int, lines: tuple[str, ...], *, css: str = "body", anchor: str = "middle") -> str:
    sizes = {"title": 38, "subtitle": 24, "heading": 28, "body": 24, "edge-label": 24}
    escaped = [html.escape(line) for line in lines]
    spans = [f'<tspan x="{x}" dy="0">{escaped[0]}</tspan>']
    spans.extend(f'<tspan x="{x}" dy="30">{line}</tspan>' for line in escaped[1:])
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{css}" '
        f'font-size="{sizes[css]}px">' + "".join(spans) + "</text>"
    )


def _node(
    x: int,
    y: int,
    width: int,
    height: int,
    lines: tuple[str, ...],
    css: str = "node",
    *,
    aria_label: str | None = None,
) -> str:
    text_y = y + height // 2 - (len(lines) - 1) * 15 + 8
    encoded_label = html.escape(aria_label, quote=True).replace("-", "&#45;") if aria_label else ""
    accessible_name = f' aria-label="{encoded_label}"' if encoded_label else ""
    return (
        f'<g{accessible_name}><rect x="{x}" y="{y}" width="{width}" height="{height}" rx="16" class="{css}"/>'
        + _text(x + width // 2, text_y, lines)
        + "</g>"
    )


def _edge(x1: int, y1: int, x2: int, y2: int, *, dashed: bool = False, bidirectional: bool = False) -> str:
    css = "edge dashed" if dashed else "edge"
    marker_start = ' marker-start="url(#arrow)"' if bidirectional else ""
    marker_end = "" if bidirectional else ' marker-end="url(#arrow)"'
    return f'<path d="M{x1},{y1} L{x2},{y2}" class="{css}"{marker_start}{marker_end}/>'


def _line(x1: int, y1: int, x2: int, y2: int, *, dashed: bool = False) -> str:
    css = "edge dashed" if dashed else "edge"
    return f'<path d="M{x1},{y1} L{x2},{y2}" class="{css}"/>'


def _path(points: tuple[tuple[int, int], ...], *, dashed: bool = False) -> str:
    css = "edge dashed" if dashed else "edge"
    commands = " ".join(("M" if index == 0 else "L") + f"{x},{y}" for index, (x, y) in enumerate(points))
    return f'<path d="{commands}" class="{css}" marker-end="url(#arrow)"/>'


def _label(x: int, y: int, lines: tuple[str, ...]) -> str:
    width = max(len(line) for line in lines) * 13 + 28
    height = len(lines) * 30 + 16
    return (
        f'<g><rect x="{x - width // 2}" y="{y - 25}" width="{width}" height="{height}" rx="8" class="label-bg"/>'
        + _text(x, y, lines, css="edge-label")
        + "</g>"
    )


def _base(spec: DiagramSpec) -> list[str]:
    ident = spec.code.lower()
    marker_shape = (
        '<polygon fill="#555555" points="0,0 0,8 11,4"/>'
        if spec.code == "D1"
        else '<path d="M0,0 L0,8 L11,4 z" fill="#24364b"/>'
    )
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{spec.width}" height="{spec.height}" viewBox="0 0 {spec.width} {spec.height}" role="img" aria-labelledby="{ident}-title {ident}-desc">',
        f'<title id="{ident}-title">{html.escape(spec.code + ". " + spec.title)}</title>',
        f'<desc id="{ident}-desc">{html.escape(spec.description, quote=False)}</desc>',
        f'<metadata>canonical_source={_display_path(spec.source)};sha256={spec.source_sha256};status=PREAUTHORIZATION_VISUAL_DERIVATIVE;evidence=NOT_SCIENTIFIC_EVIDENCE;independence=SAME_WORKSPACE_NOT_INDEPENDENT</metadata>',
        f'<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto-start-reverse">{marker_shape}</marker></defs>',
        '<style>.bg{fill:#ffffff}.title{font-family:Helvetica,Arial,sans-serif;font-weight:700;fill:#102a43}.subtitle,.heading{font-family:Helvetica,Arial,sans-serif;font-weight:600;fill:#334e68}.body,.edge-label{font-family:Helvetica,Arial,sans-serif;font-weight:500;fill:#102a43}.node{fill:#e8f1fb;stroke:#1463a5;stroke-width:3}.control{fill:#edf7ed;stroke:#276738;stroke-width:3}.boundary{fill:#fff8dc;stroke:#8a5a00;stroke-width:4;stroke-dasharray:11 7}.offline{fill:#fff1f0;stroke:#a32620;stroke-width:4;stroke-dasharray:11 7}.terminal{fill:#e7f7f5;stroke:#006d6f;stroke-width:4}.edge{fill:none;stroke:#24364b;stroke-width:3}.dashed{stroke-dasharray:10 7}.label-bg{fill:#ffffff;stroke:#c5d2df;stroke-width:1}.lane{fill:#f7fafc;stroke:#627d98;stroke-width:2;stroke-dasharray:12 7}.start{fill:#24364b;stroke:#ffffff;stroke-width:3}</style>',
        f'<rect width="{spec.width}" height="{spec.height}" class="bg"/>',
        _text(spec.width // 2, 56, (f"{spec.code}. {spec.title}",), css="title"),
        _text(spec.width // 2, 96, ("Canonical Mermaid source-bound preauthorization derivative",), css="subtitle"),
    ]


def _render_d1(parts: list[str]) -> None:
    nodes = {
        "B": (40, 165, 300, 100, ("Unpredictable Beacon",), "node"),
        "P": (450, 165, 300, 100, ("Policy / Bulletin Board",), "control"),
        "C": (850, 165, 300, 110, ("Threshold Custodian", "Committee"), "control"),
        "A": (1250, 165, 310, 100, ("Readiness Audit Verifier",), "node"),
        "W": (40, 480, 300, 120, ("Inference Worker", "AEAD-encrypt record", "with K_r"), "node"),
        "DA": (450, 490, 300, 100, ("Ciphertext DA Layer",), "node"),
        "T": (850, 490, 300, 100, ("Threshold Combiner",), "control"),
        "V": (450, 790, 300, 100, ("Authorized Verifier Set",), "node"),
        "R": (850, 790, 300, 100, ("Private Re-execution",), "terminal"),
        "O": (1250, 1080, 310, 100, ("Dispute Verdict",), "terminal"),
    }
    for node_id, (x, y, w, h, lines, css) in nodes.items():
        aria_label = {
            "C": "Threshold Custodian Committee",
            "W": "AEAD-encrypt record with Kᵣ",
        }.get(node_id)
        parts.append(_node(x, y, w, h, lines, css, aria_label=aria_label))
    parts += [
        _edge(340, 215, 450, 215),
        _edge(750, 215, 850, 215), _label(800, 315, ("sampled canary challenge",)),
        _edge(1150, 215, 1250, 215), _label(1200, 315, ("partial + DLEQ proof",)),
        _path(((1405,265),(1405,360),(600,360),(600,265))), _label(1000, 385, ("valid / invalid / timeout evidence",)),
        _edge(340, 540, 450, 540), _label(395, 650, ("ciphertext record",)),
        _path(((190,480),(190,400),(1000,400),(1000,275)), dashed=True), _label(470, 445, ("K_r encapsulated under epoch PK_e",)),
        _edge(750, 540, 850, 540),
        _path(((560,265),(560,680),(560,790))), _label(465, 700, ("authorization + deadline",)),
        _path(((750,840),(800,840),(800,220),(850,220))), _label(820, 755, ("confidential release request",)),
        _edge(1000, 275, 1000, 490), _label(1250, 455, ("at least t verified partials",)),
        _edge(1000, 590, 1000, 790), _label(1300, 700, ("recovered record key",)),
        _edge(640,590,640,790),
        _edge(750,590,850,790),
        _edge(1150,840,1250,1130),
        _path(((750,215),(780,215),(780,1040),(1250,1130))),
        _label(800, 1265, ("Separation boundary: audit evidence and ciphertext availability do not certify future DKA.",)),
    ]


def _render_d5(parts: list[str]) -> None:
    lanes = ((45, "EPOCH"), (560, "AUDIT"), (1075, "DISPUTE"))
    for x, name in lanes:
        parts.append(f'<rect x="{x}" y="135" width="480" height="1240" rx="18" class="lane"/>')
        parts.append(_text(x + 240, 185, (name,), css="heading"))
    def state(x: int, y: int, label: str, css: str = "node", width: int = 310) -> None:
        parts.append(_node(x, y, width, 80, (label,), css))
    # Epoch
    parts.append('<circle cx="285" cy="240" r="15" class="start"/>')
    state(130, 300, "CREATED"); state(130, 500, "ACTIVE", "control"); state(130, 720, "REFRESHING"); state(130, 1080, "RETIRED", "terminal")
    parts += [_edge(285,255,285,300), _edge(285,380,285,500), _label(285,430,("roster + commitments",)),
              _edge(285,580,285,720), _label(285,640,("scheduled refresh",)),
              _edge(130,760,80,540), _edge(80,540,130,540), _label(270,850,("valid refreshed shares",)),
              _edge(285,580,285,1080), _label(350,965,("challenge window closed",))]
    # Audit
    parts.append('<circle cx="800" cy="240" r="15" class="start"/>')
    state(645,300,"COMMITTED"); state(645,470,"SAMPLED"); state(645,640,"OPEN","control"); state(590,1010,"PASSED","terminal",210); state(820,1010,"FAILED","offline",200)
    parts += [_edge(800,255,800,300), _edge(800,380,800,470), _label(870,430,("beacon",)),
              _edge(800,550,800,640), _label(910,600,("canary posted",)),
              _edge(760,720,695,1010), _label(670,840,("at least q valid", "by deadline")),
              _edge(840,720,920,1010,dashed=True), _label(930,840,("invalid or missing", "at deadline"))]
    # Dispute
    parts.append('<circle cx="1315" cy="240" r="15" class="start"/>')
    state(1160,300,"REQUESTED"); state(1160,450,"AUTHORIZED","control"); state(1160,600,"COLLECTING"); state(1100,900,"OPENED","terminal",200); state(1330,900,"EXPIRED","offline",200); state(1160,1150,"RESOLVED","terminal")
    parts += [_edge(1315,255,1315,300), _edge(1315,380,1315,450), _label(1420,420,("policy accepts",)),
              _edge(1315,530,1315,600),
              _edge(1270,680,1200,900), _label(1190,790,("at least t valid", "partials")),
              _edge(1360,680,1430,900,dashed=True), _label(1460,790,("deadline",)),
              _edge(1200,980,1315,1150), _label(1340,1080,("verdict",))]


def _render_d6(parts: list[str]) -> None:
    parts += [_text(230,150,("THREAT / FAULT",),css="heading"), _text(800,150,("CONTROL",),css="heading"), _text(1370,150,("RESIDUAL ASSUMPTION / LIMIT",),css="heading")]
    rows = (
        (("Invalid partial",), ("Feldman plus DLEQ", "verification"), ("Crypto soundness", "assumption")),
        (("Non-response or churn",), ("Public deadline and", "response commitment"), ("Partial synchrony", "assumption")),
        (("Equivocation",), ("Context-bound signed", "commitments"), ("Identity correctness",)),
        (("Correlated outage",), ("Domain diversity and", "stratified sampling"), ("Domain labels may", "be dishonest")),
        (("Selective withholding",), ("Counterexample experiment and", "optional hidden request class"), ("Audits do not prove", "future cooperation")),
        (("Early key-release", "collusion"), ("Threshold, rotation,", "policy gate"), ("Fewer than t collude", "before authorization")),
    )
    for index, (threat, control, residual) in enumerate(rows):
        y = 195 + index * 190
        parts += [_node(40,y,380,120,threat,"offline"), _node(600,y,400,120,control,"control"), _node(1180,y,380,120,residual,"boundary")]
        parts += [_edge(420,y+60,600,y+60), _edge(1000,y+60,1180,y+60,dashed=True)]
    parts.append(_label(800, 1360, ("Dashed boundary arrows denote residual assumptions or limitations, not certified mitigations.",)))


def _render_d7(parts: list[str]) -> None:
    domains = (
        (55, ("Domain A", "8 online"), "control"), (445, ("Domain B", "8 online"), "control"),
        (835, ("Domain C", "8 OFFLINE"), "offline"), (1225, ("Domain D", "8 online"), "control"),
    )
    for x, lines, css in domains:
        parts.append(_node(x,180,320,120,lines,css))
    parts += [_line(375,240,445,240), _line(765,240,835,240), _line(1155,240,1225,240)]
    parts += [_node(120,560,580,170,("Uniform sample s=8", "may miss or under-sample", "a failed domain"),"node"),
              _node(900,560,580,170,("Stratified sample s=8", "two samples per domain", "complete outage observed"),"terminal")]
    parts += [_edge(215,300,310,560), _edge(1385,300,510,560),
              _edge(215,300,1000,560), _edge(605,300,1100,560), _edge(995,300,1200,560,dashed=True), _edge(1385,300,1300,560)]
    parts += [_label(400,850,("Uniform: fault-domain coverage is not guaranteed.",)),
              _label(1200,850,("Stratified: every declared domain is sampled.",)),
              _label(800,1015,("Declared domain labels remain an assumption; color is reinforced by OFFLINE text and dashed border.",))]


def _render_d8(parts: list[str]) -> None:
    parts.append(_node(525,150,550,100,("Frozen config: n, t, s, q,", "domains, seeds"),"control"))
    branches = ((40,("Crypto unit tests",)), (430,("End-to-end audit", "and dispute demo")), (820,("Adversarial simulator",)), (1210,("Microbenchmarks",)))
    for x, lines in branches:
        parts.append(_node(x,380,350,110,lines,"node"))
        parts.append(_edge(800,250,x+175,380))
    parts.append(_node(525,650,550,110,("Versioned CSV/JSON", "and manifest"),"control"))
    for x, _ in branches:
        parts.append(_edge(x+175,490,800,650))
    parts += [_node(250,880,430,100,("Publication figures",),"node"), _node(920,880,430,100,("Claim-evidence matrix",),"node"),
              _edge(700,760,465,880), _edge(900,760,1135,880),
              _node(585,1060,430,90,("MPP paper",),"terminal"), _edge(465,980,720,1060), _edge(1135,980,880,1060),
              _node(585,1190,430,60,("Publication success gates",),"boundary"), _edge(800,1150,800,1190)]


RENDERERS = {"D1": _render_d1, "D5": _render_d5, "D6": _render_d6, "D7": _render_d7, "D8": _render_d8}


def render_svg(spec: DiagramSpec, source: str) -> str:
    validate_source(spec, source)
    parts = _base(spec)
    RENDERERS[spec.code](parts)
    parts += ["</svg>", ""]
    return "\n".join(parts)


def write_svg(spec: DiagramSpec, source: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = render_svg(spec, source)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output.parent, delete=False) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    temporary.replace(output)


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("Chrome output is not a valid PNG")
    return struct.unpack(">II", data[16:24])


def render_png(svg: Path, output: Path, chrome: Path, width: int, height: int) -> None:
    if not chrome.is_file():
        raise FileNotFoundError(f"reviewed local Chrome not found: {chrome}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix="keystone-dense-chrome-") as profile:
        command = [
            str(chrome), "--headless=new", "--disable-gpu", "--disable-background-networking",
            "--disable-component-update", "--disable-default-apps", "--disable-sync", "--hide-scrollbars",
            "--force-device-scale-factor=1", f"--window-size={width},{height}", f"--user-data-dir={profile}",
            f"--screenshot={output.resolve()}", svg.resolve().as_uri(),
        ]
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 30
        captured = False
        while time.monotonic() < deadline:
            if output.is_file():
                try:
                    captured = png_dimensions(output) == (width, height)
                except (OSError, ValueError, struct.error):
                    captured = False
                if captured:
                    break
            if process.poll() is not None:
                break
            time.sleep(0.1)
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if not captured:
            raise RuntimeError(f"local Chrome did not produce a complete PNG (returncode={process.returncode})")
    if png_dimensions(output) != (width, height):
        raise ValueError(f"unexpected PNG dimensions: {png_dimensions(output)}")


def build_receipt(
    sources: dict[str, Path], outputs: dict[str, tuple[Path, Path]], *, chrome_version: str, generated_at: str
) -> dict[str, object]:
    assets = {}
    for code, spec in SPECS.items():
        source_path = sources[code]
        svg_path, png_path = outputs[code]
        validate_source(spec, source_path.read_text(encoding="utf-8"))
        assets[code] = {
            "source": {"path": _display_path(source_path), "sha256": sha256_bytes(source_path.read_bytes())},
            "svg": {"path": _display_path(svg_path), "sha256": sha256_bytes(svg_path.read_bytes())},
            "png": {"path": _display_path(png_path), "sha256": sha256_bytes(png_path.read_bytes()), "dimensions": list(png_dimensions(png_path))},
        }
    return {
        "schema_id": "KEYSTONE_DENSE_DIAGRAM_RENDER_RECEIPT", "schema_version": 1,
        "status": "PREAUTHORIZATION_VISUAL_DERIVATIVE", "evidence_classification": "NOT_SCIENTIFIC_EVIDENCE",
        "independence": "SAME_WORKSPACE_NOT_INDEPENDENT", "generated_at": generated_at,
        "canonical_authority": "Mermaid sources only; rendered files are derivatives",
        "inventory": list(SPECS),
        "renderer": {"path": _display_path(RENDERER_PATH), "sha256": sha256_bytes(RENDERER_PATH.read_bytes()),
                     "mode": "deterministic standard-library SVG plus reviewed local Chrome PNG capture",
                     "network": "DISABLED_BY_COMMAND_AND_LOCAL_FILE_INPUT", "chrome_version": chrome_version},
        "assets": assets,
        "visual_qa": {"typography": "AUTOMATED_180MM_PROXY_PENDING_OR_SEPARATELY_RECORDED",
                      "human_visual_review": "PENDING", "scientific_claim_validation": "NOT_PERFORMED"},
    }


def write_receipt(receipt: dict[str, object], output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile("wb", dir=output.parent, delete=False) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    temporary.replace(output)
    digest = sha256_bytes(payload)
    output.with_suffix(output.suffix + ".sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return digest


def check_bundle(sources: dict[str, Path], outputs: dict[str, tuple[Path, Path]], receipt_path: Path) -> bool:
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("schema_id") != "KEYSTONE_DENSE_DIAGRAM_RENDER_RECEIPT":
            return False
        if tuple(receipt.get("inventory", ())) != tuple(SPECS):
            return False
        if receipt.get("renderer", {}).get("sha256") != sha256_bytes(RENDERER_PATH.read_bytes()):
            return False
        if receipt.get("status") != "PREAUTHORIZATION_VISUAL_DERIVATIVE":
            return False
        for code, spec in SPECS.items():
            source_path = sources[code]
            svg_path, png_path = outputs[code]
            source = source_path.read_text(encoding="utf-8")
            validate_source(spec, source)
            if svg_path.read_text(encoding="utf-8") != render_svg(spec, source):
                return False
            if png_dimensions(png_path) != (spec.width, spec.height):
                return False
            asset = receipt.get("assets", {}).get(code, {})
            if asset.get("source", {}).get("sha256") != sha256_bytes(source_path.read_bytes()):
                return False
            if asset.get("svg", {}).get("sha256") != sha256_bytes(svg_path.read_bytes()):
                return False
            if asset.get("png", {}).get("sha256") != sha256_bytes(png_path.read_bytes()):
                return False
        sidecar = receipt_path.with_suffix(receipt_path.suffix + ".sha256")
        expected = f"{sha256_bytes(receipt_path.read_bytes())}  {receipt_path.name}\n"
        return sidecar.read_text(encoding="utf-8") == expected
    except (FileNotFoundError, KeyError, OSError, ValueError, json.JSONDecodeError, struct.error):
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chrome", type=Path, default=DEFAULT_CHROME)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sources = {code: spec.source for code, spec in SPECS.items()}
    outputs = {code: (spec.svg, spec.png) for code, spec in SPECS.items()}
    if args.check:
        if not check_bundle(sources, outputs, args.receipt):
            print("FAIL: dense diagram source, renderer, output, or receipt drift")
            return 1
        print("PASS: D1/D5-D8 source, renderer, SVG, PNG, receipt, and sidecar hashes match")
        return 0
    for code, spec in SPECS.items():
        source = spec.source.read_text(encoding="utf-8")
        write_svg(spec, source, spec.svg)
        render_png(spec.svg, spec.png, args.chrome, spec.width, spec.height)
        print(f"Wrote {code}: {spec.svg} and {spec.png} ({spec.width}x{spec.height})")
    version = subprocess.run([str(args.chrome), "--version"], check=True, capture_output=True, text=True, timeout=10).stdout.strip()
    receipt = build_receipt(sources, outputs, chrome_version=version,
                            generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    digest = write_receipt(receipt, args.receipt)
    print(f"Wrote {args.receipt} ({digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
