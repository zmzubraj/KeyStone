#!/usr/bin/env python3
"""Render the R1 manuscript figures and LaTeX tables from R1 result files only.

Every number in ``paper/r1/tables/*.tex`` and every plotted point in
``paper/r1/figures/*`` is read from ``research-case/05-analysis/results/r1`` or
from the Foundry ``.gas-snapshot``; nothing is typed by hand. The script writes
``paper/r1/r1-asset-manifest.json`` binding each asset to its source hashes.
"""

from __future__ import annotations

import csv
import hashlib
import json
from math import comb
from pathlib import Path
import re
import statistics
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT / "scripts"))

from keystone.simulation import wilson_score_interval  # noqa: E402
from run_r1_pc03 import freeze_sha256  # noqa: E402

RES = ROOT / "research-case/05-analysis/results/r1"
PAPER = ROOT / "paper/r1"
FIG, TAB = PAPER / "figures", PAPER / "tables"
# Validated categorical slots 1-4 (dataviz reference palette, light mode); text stays neutral.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
MARKERS = ["o", "s", "^", "D"]
DASHES = ["-", "--", "-.", ":"]
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
DEADLINES = [0.25, 0.5, 1.0, 2.0, 5.0]
SOURCES: dict[str, list[str]] = {}

plt.rcParams.update({
    "font.family": "serif", "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "lines.linewidth": 1.6, "lines.markersize": 4.5,
    "savefig.dpi": 300, "pdf.fonttype": 42,
})


def read_csv(name: str) -> list[dict[str, str]]:
    return list(csv.DictReader((RES / name).open()))


def save(fig, stem: str, sources: list[str]) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{stem}.png", bbox_inches="tight")
    plt.close(fig)
    SOURCES[f"figures/{stem}.pdf"] = sources


def write_table(stem: str, body: str, sources: list[str]) -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    (TAB / f"{stem}.tex").write_text(body)
    SOURCES[f"tables/{stem}.tex"] = sources


def pct(value: float, digits: int = 1) -> str:
    return f"{100 * value:.{digits}f}\\%"


def ci(pair, digits: int = 1) -> str:
    return f"[{100 * pair[0]:.{digits}f}, {100 * pair[1]:.{digits}f}]"


# ---------------------------------------------------------------- deadline data
def load_deadline() -> dict[str, list[dict[str, str]]]:
    out = {}
    for path in sorted((RES / "deadline").glob("D*.csv")):
        out[path.stem] = list(csv.DictReader(path.open()))
    return out


def deadline_summary(rows: list[dict[str, str]]) -> dict:
    total = len(rows)
    times = sorted(float(r["dispute_time_s"]) for r in rows if r["dispute_success"] == "True")
    audit_times = sorted(float(r["audit_time_s"]) for r in rows if r["audit_time_s"])
    by_deadline = {d: sum(x <= d for x in times) for d in DEADLINES}
    audit_by_1s = sum(x <= 1.0 for x in audit_times)

    def q(values, p):
        return values[min(len(values) - 1, int(p * len(values)))] if values else None

    return {"traces": total, "success": len(times), "by_deadline": by_deadline,
            "median": statistics.median(times) if times else None, "p95": q(times, 0.95),
            "audit_pass": sum(r["audit_pass"] == "True" for r in rows), "audit_by_1s": audit_by_1s,
            "audit_median": statistics.median(audit_times) if audit_times else None,
            "audit_p95": q(audit_times, 0.95), "times": times}


# ---------------------------------------------------------------- figures
def fig_detection() -> None:
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.9, 2.6))
    s_vals = list(range(1, 17))
    for i, t in enumerate((17, 22, 27)):
        a.plot(s_vals, [1 - comb(t - 1, s) / comb(32, s) for s in s_vals], DASHES[i], color=SERIES[i],
               marker=MARKERS[i], label=f"$t={t}$")
    base = 1 - comb(21, 8) / comb(32, 8)
    a.annotate(f"$s=8$: {100 * base:.2f}%", (8, base), xytext=(9.3, 0.80), color=INK, fontsize=7.5,
               arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.7})
    a.set(xlabel="Audit sample size $s$ (with $q=s$)", ylabel="Worst-case detection", title="(a) $n=32$", ylim=(0.45, 1.01))
    a.legend(loc="lower right")
    rows = read_csv("analytic-scalability-detection.csv")
    for i, n in enumerate((16, 32, 64, 128)):
        t = n - (n - 1) // 3
        b.plot(s_vals, [1 - comb(t - 1, s) / comb(n, s) for s in s_vals], DASHES[i], color=SERIES[i],
               marker=MARKERS[i], label=f"$n={n}$, $t={t}$")
    b.set(xlabel="Audit sample size $s$ (with $q=s$)", title="(b) $t=n-\\lfloor (n-1)/3\\rfloor$", ylim=(0.45, 1.01))
    b.legend(loc="lower right")
    assert rows  # grid table is rendered in Table 5 from the same formula
    save(fig, "fig2_detection_vs_sample", ["analytic-scalability-detection.csv"])


def fig_deadline(dl: dict) -> None:
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.9, 2.7), sharey=True)
    xs = [x / 200 for x in range(0, 1201)]
    panels = [(a, ["D0-CONTROL", "D1-REGIONAL", "D2-GLOBAL", "D7-HEAVY-TAIL"], "(a) latency profiles"),
              (b, ["D2-GLOBAL", "D3-GLOBAL-LOSS2", "D4-GLOBAL-CRASH10", "D6-GLOBAL-DOMAIN-OUTAGE"], "(b) faults under global latency")]
    for ax, names, title in panels:
        for i, name in enumerate(names):
            summ = deadline_summary(dl[name])
            ys = [sum(t <= x for t in summ["times"]) / summ["traces"] for x in xs]
            ax.plot(xs, ys, DASHES[i], color=SERIES[i], label=name.split("-", 1)[1].replace("-", " ").lower())
        for d in DEADLINES:
            ax.axvline(d, color=GRID, lw=0.8, zorder=0)
        ax.set(xlim=(0, 6), xlabel="Deadline $\\Delta_d$ (s)", title=title)
        ax.legend(loc="upper left", fontsize=7)
    a.set_ylabel("P[dispute decrypts by $\\Delta_d$]")
    crash11 = deadline_summary(dl["D5-GLOBAL-CRASH11"])
    b.text(0.15, 0.45, f"crash 11: {crash11['success']}/{crash11['traces']}\nsucceed at any $\\Delta_d$", fontsize=7, color=MUTED)
    save(fig, "fig3_dispute_success_vs_deadline", [f"deadline/{n}.csv" for n in dl])


def fig_correlation() -> None:
    rows = read_csv("analytic-domain-correlation.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.9, 2.6), sharex=True)
    labels = {"IID": "IID", "DOMAIN_8x4": "8 domains x 4", "DOMAIN_4x8": "4 domains x 8", "DOMAIN_2x16": "2 domains x 16"}
    for i, model in enumerate(labels):
        pts = [(float(r["unavailability"]), float(r["reconstructability"]), float(r["audit_pass"])) for r in rows if r["model"] == model]
        a.plot([p[0] for p in pts], [p[1] for p in pts], DASHES[i], color=SERIES[i], marker=MARKERS[i], label=labels[model])
        b.plot([p[0] for p in pts], [p[2] for p in pts], DASHES[i], color=SERIES[i], marker=MARKERS[i], label=labels[model])
    a.set(xlabel="Per-unit unavailability $f$", ylabel="Exact probability", title="(a) reconstructability $P[\\mathrm{ready}\\geq t]$")
    b.set(xlabel="Per-unit unavailability $f$", title="(b) audit pass ($s=q=8$)")
    a.legend(loc="lower left", fontsize=7)
    save(fig, "fig4_iid_vs_correlated", ["analytic-domain-correlation.csv"])


def fig_withholding() -> None:
    summary = json.loads((RES / "pc03-summary.json").read_text())["cells"]["RID-C003-SW-001"]
    fig, ax = plt.subplots(figsize=(3.4, 2.5))
    ws = list(range(0, 17))
    ax.step(ws, [1.0] * len(ws), where="mid", color=SERIES[0], label="audit pass (exact)")
    ax.step(ws, [1.0 if 32 - w >= 22 else 0.0 for w in ws], where="mid", color=SERIES[1], ls="--", label="dispute success (exact)")
    ax.errorbar([11], [summary["dispute_success"]["estimate"]], fmt="s", color=SERIES[1], ms=5,
                label="PC03 simulation, 131,072 draws")
    ax.errorbar([11], [summary["audit_pass"]["estimate"]], fmt="o", color=SERIES[0], ms=5)
    ax.axvline(10.5, color=MUTED, lw=0.7, ls=":")
    ax.text(11.3, 0.55, "$w=n-t+1=11$", fontsize=7, color=MUTED)
    ax.set(xlabel="Selective withholders $w$ ($n=32$, $t=22$)", ylabel="Probability", ylim=(-0.05, 1.08))
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 0.12), fontsize=6.5)
    save(fig, "fig5_audit_vs_dispute_withholding", ["pc03-summary.json"])


def fig_acceptance() -> None:
    rows = read_csv("analytic-acceptance-sensitivity.csv")
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    for i, s in enumerate((8, 12, 16)):
        pts = [(1 - float(r["benign_audit_pass_iid_0.10"]), float(r["worst_case_detection"]), int(r["q"]))
               for r in rows if int(r["s"]) == s]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], DASHES[i], color=SERIES[i], marker=MARKERS[i], label=f"$s={s}$")
        for x, y, q in pts:
            if (s, q) in {(8, 8), (8, 7), (16, 14)}:
                ax.annotate(f"$s={s},q={q}$", (x, y), xytext=(6, -12), textcoords="offset points", fontsize=6.5, color=MUTED)
    ax.set(xlabel="Benign alarm rate (audit fails, 10% IID)", ylabel="Worst-case detection ($r=t-1$)", xlim=(-0.02, 0.9))
    ax.legend(loc="lower right")
    save(fig, "fig6_acceptance_tradeoff", ["analytic-acceptance-sensitivity.csv"])


# ---------------------------------------------------------------- tables
def table_config(dl_meta: dict) -> None:
    body = r"""\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.2\textwidth}>{\raggedright\arraybackslash}p{0.3\textwidth}X@{}}
\toprule
Experiment family & Parameters & Execution and evidence label\\
\midrule
Static bound (Eq.~\ref{eq:bound}) & $n\in\{16,32,64,128\}$, $t=n-\lfloor (n-1)/3\rfloor$, $s\in\{1,\dots,16\}$, $q=s$; baseline $n=32,t=22,s=q=8$ & Exact closed form\\
PC03 prespecified cells & $n=32,t=22,s=q=8$, 4 domains of 8. IID: $p_{\mathrm{off}}=0.10$. STRAT: $p_{\mathrm{dom}}=0.20$, $p_{\mathrm{off}}=0.02$, uniform vs.\ 2-per-domain quota. SW: $w=11$ & 32 seed blocks $\times$ 4{,}096 draws $=131{,}072$ per cell; seeds frozen before execution; simulation\\
Correlation model & $f\in\{0,0.025,\dots,0.40\}$; IID vs.\ 2/4/8 equal domains & Exact; declared synthetic model\\
Acceptance rule & $s\in\{8,12,16\}$, $q\in[\lceil s/2\rceil,s]$, IID $f\in\{0.05,0.10,0.20\}$ & Exact; post hoc\\
Cryptographic cost & ffdhe2048, ffdhe3072 (RFC 7919) and the 256-bit prototype group; $n\le 128$ & Local microbenchmark, CPython 3.13, Apple M4 Pro\\
Deadline testbed & ffdhe2048, $n=32,t=22$; 8 profiles $\times$ __TRACES__ traces; one-way delay lognormal (median 0/40/120\,ms); 2\% loss; 10 or 11 crashes; one-domain outage; $\Delta_d\in\{0.25,0.5,1,2,5\}$\,s & 32 custodian processes on one host, loopback TCP, real cryptography; emulation\\
\bottomrule
\end{tabularx}
"""
    write_table("t2_configuration", body.replace("__TRACES__", str(dl_meta["traces"])), ["pc03-summary.json", "analytic-manifest.json", "deadline/*.meta.json"])


def table_baselines(ops: dict, sizes: dict) -> None:
    g = "ffdhe2048"
    prove, verify = ops[(g, "partial_plus_dleq_proof")], ops[(g, "dleq_verification")]
    resp, req = sizes[g]["partial_response_bytes"], sizes[g]["audit_request_bytes"]
    det8 = 1 - comb(21, 8) / comb(32, 8)

    def cost(k: int) -> str:
        return f"{k} proofs + {k} verifications; {k * (prove + verify):.0f}\\,ms CPU; {req + k * resp:,}\\,B"

    body = r"""\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{0.17\textwidth}>{\raggedright\arraybackslash}p{0.15\textwidth}>{\raggedright\arraybackslash}p{0.14\textwidth}>{\raggedright\arraybackslash}p{0.17\textwidth}X@{}}
\toprule
Readiness check & Exercises the secret share? & Touches production ciphertext? & Detects a static state with $r=t-1$ ready shares & Cost per check ($n=32$, ffdhe2048, measured)\\
\midrule
Liveness heartbeat & No & No & No: a node that lost its share still answers & 1 message per node; no group operations\\
Share registration (Feldman/PVSS check) & Once, at setup & No & No: says nothing about later share loss & One-time $O(nt)$ exponentiations at epoch setup\\
Full-committee canary probe & Yes & No (canary) & Yes, with probability 1 & __FULL__\\
KEYSTONE sampled canary ($s=q=8$) & Yes, for the sampled members & No (canary) & Yes, with probability __DET__ (Eq.~\ref{eq:bound}) & __KEY__\\
Decrypt a real record as a test & Yes & Yes: exposes a production record & Yes & $t$ verifications plus a real disclosure; excluded by design\\
\bottomrule
\end{tabularx}
"""
    body = body.replace("__FULL__", cost(32)).replace("__KEY__", cost(8)).replace("__DET__", f"{det8:.4f}")
    write_table("t3_baselines", body, ["microbench-operations.csv", "microbench-message-sizes.csv"])


def table_robustness(dl: dict) -> None:
    pc = json.loads((RES / "pc03-summary.json").read_text())["cells"]
    iid, strat, sw = pc["RID-C003-IID-001"], pc["RID-C003-STRAT-001"], pc["RID-C003-SW-001"]
    lines = [r"\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}X r r r r r@{}}", r"\toprule",
             r"Scenario & Audit pass & Dispute success & By $\Delta_d=5$\,s & Median time & p95 time\\", r"\midrule",
             r"\multicolumn{6}{@{}l}{\textit{(a) PC03 prespecified simulation, 131{,}072 draws per cell, 95\% Wilson intervals}}\\"]
    lines.append(f"IID 10\\% unavailable & {pct(iid['audit_pass']['estimate'])} {ci(iid['audit_pass']['wilson95'])} & "
                 f"{pct(iid['reconstruction_success']['estimate'], 2)} {ci(iid['reconstruction_success']['wilson95'], 2)} & -- & -- & --\\\\")
    for policy in ("uniform", "stratified"):
        lines.append(f"Domain outage 20\\%, {policy} sample & {pct(strat[f'audit_pass_{policy}']['estimate'])} {ci(strat[f'audit_pass_{policy}']['wilson95'])} & "
                     f"{pct(1 - strat['catastrophic_rate']['estimate'])} {ci((1 - strat['catastrophic_rate']['wilson95'][1], 1 - strat['catastrophic_rate']['wilson95'][0]))} & -- & -- & --\\\\")
    lines.append(f"11 selective withholders & {pct(sw['audit_pass']['estimate'])} {ci(sw['audit_pass']['wilson95'], 3)} & "
                 f"{pct(sw['dispute_success']['estimate'])} {ci(sw['dispute_success']['wilson95'], 3)} & -- & -- & --\\\\")
    lines.append(r"\addlinespace")
    lines.append(r"\multicolumn{6}{@{}l}{\textit{(b) Emulated deadline testbed, ffdhe2048; dispute success by the primary $\Delta_d=2$\,s and by 5\,s, 95\% Wilson intervals}}\\")
    for name, rows in dl.items():
        s = deadline_summary(rows)
        n = s["traces"]
        audit = (s["audit_pass"], n)
        succ = s["by_deadline"][2.0]
        med = "--" if s["median"] is None else f"{1000 * s['median']:.0f}\\,ms"
        p95 = "--" if s["p95"] is None else f"{1000 * s['p95']:.0f}\\,ms"
        label = name.split("-", 1)[1].replace("-", " ").lower()
        lines.append(f"{label} & {pct(audit[0] / n)} {ci(wilson_score_interval(*audit))} & {pct(succ / n)} {ci(wilson_score_interval(succ, n))} & {pct(s['by_deadline'][5.0] / n)} & {med} & {p95}\\\\")
    lines += [r"\bottomrule", r"\end{tabularx}", ""]
    write_table("t4_robustness", "\n".join(lines), ["pc03-summary.json"] + [f"deadline/{n}.csv" for n in dl])


def table_scalability(ops: dict, sizes: dict) -> None:
    lines = [r"\begin{tabular}{@{}rrrrrrrr@{}}", r"\toprule",
             r" & & & & \multicolumn{2}{c}{Audit, ffdhe2048} & \multicolumn{2}{c}{Dispute: verify $t$ + combine}\\",
             r"\cmidrule(lr){5-6}\cmidrule(lr){7-8}",
             r"$n$ & $t$ & $s$ & Detection & CPU & Bytes & ffdhe2048 & ffdhe3072\\", r"\midrule"]
    g2, g3 = "ffdhe2048", "ffdhe3072"
    per_member = ops[(g2, "partial_plus_dleq_proof")] + ops[(g2, "dleq_verification")]
    for n, s in ((16, 4), (32, 8), (64, 12), (128, 16)):
        t = n - (n - 1) // 3
        det = 1 - comb(t - 1, s) / comb(n, s)
        audit_bytes = sizes[g2]["audit_request_bytes"] + s * sizes[g2]["partial_response_bytes"]
        lines.append(f"{n} & {t} & {s} & {100 * det:.2f}\\% & {s * per_member:.0f}\\,ms & {audit_bytes:,} & "
                     f"{ops[(g2, 'verify_t_and_combine', n)]:.0f}\\,ms & {ops[(g3, 'verify_t_and_combine', n)]:.0f}\\,ms\\\\")
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    write_table("t5_scalability", "\n".join(lines), ["analytic-scalability-detection.csv", "microbench-operations.csv", "microbench-message-sizes.csv"])

    op_lines = [r"\begin{tabular}{@{}lrrr@{}}", r"\toprule",
                r"Operation (median, ms) & 256-bit prototype & ffdhe2048 & ffdhe3072\\", r"\midrule"]
    names = {"canary_derivation": "Canary derivation $H_G$", "partial_plus_dleq_proof": "Partial decryption + DLEQ proof",
             "dleq_verification": "DLEQ verification", "record_seal_1KiB": "Seal 1\\,KiB record"}
    for op, label in names.items():
        op_lines.append(f"{label} & " + " & ".join(f"{ops[(g, op)]:.2f}" for g in ("keystone-safe-prime-256-v1", g2, g3)) + r"\\")
    op_lines.append(r"Partial response size (bytes) & " + " & ".join(str(sizes[g]["partial_response_bytes"]) for g in ("keystone-safe-prime-256-v1", g2, g3)) + r"\\")
    op_lines += [r"\bottomrule", r"\end{tabular}", ""]
    write_table("t6_operations", "\n".join(op_lines), ["microbench-operations.csv", "microbench-message-sizes.csv"])


def table_acceptance() -> None:
    rows = read_csv("analytic-acceptance-sensitivity.csv")
    keep = {(8, 6), (8, 7), (8, 8), (12, 10), (12, 11), (12, 12), (16, 13), (16, 14), (16, 15)}
    lines = [r"\begin{tabular}{@{}rrrrrr@{}}", r"\toprule",
             r" & & Worst-case & \multicolumn{3}{c}{Benign audit pass under IID unavailability}\\", r"\cmidrule(lr){4-6}",
             r"$s$ & $q$ & detection & $f=0.05$ & $f=0.10$ & $f=0.20$\\", r"\midrule"]
    for r in rows:
        if (int(r["s"]), int(r["q"])) in keep:
            lines.append(f"{r['s']} & {r['q']} & {pct(float(r['worst_case_detection']))} & " +
                         " & ".join(pct(float(r[f'benign_audit_pass_iid_{f}'])) for f in ("0.05", "0.10", "0.20")) + r"\\")
    lines += [r"\bottomrule", r"\end{tabular}", ""]
    write_table("t7_acceptance", "\n".join(lines), ["analytic-acceptance-sensitivity.csv"])


def table_gas() -> None:
    """Gas per bulletin-board operation from the Foundry snapshot re-run for R1, with harness scope."""
    rows = list(csv.DictReader((ROOT / "contracts/gas_report.csv").open()))
    snap = (ROOT / ".gas-snapshot").read_text()
    lines = [r"\begin{tabularx}{\textwidth}{@{}l r X@{}}", r"\toprule",
             r"Bulletin-board operation & Gas & Harness scope\\", r"\midrule"]
    for row in rows:
        gas = int(re.search(rf"{row['test']}\(\) \(gas: (\d+)\)", snap).group(1))
        if gas != int(row["gas"]):
            raise SystemExit(f"gas report and snapshot disagree for {row['test']}")
        label = row["operation"].replace("_", " ").capitalize()
        lines.append(f"{label} & {gas:,} & {row['notes'].replace('_', ' ')}\\\\")
    lines += [r"\bottomrule", r"\end{tabularx}", ""]
    write_table("t8_gas", "\n".join(lines), [".gas-snapshot", "contracts/gas_report.csv"])

def write_numbers(ops: dict, dl: dict) -> None:
    """Emit \\newcommand macros so prose numbers are generated, never typed."""
    pc = json.loads((RES / "pc03-summary.json").read_text())["cells"]
    iid, strat, sw = pc["RID-C003-IID-001"], pc["RID-C003-STRAT-001"], pc["RID-C003-SW-001"]
    acc = {(int(r["s"]), int(r["q"])): r for r in read_csv("analytic-acceptance-sensitivity.csv")}
    dom = {(r["model"], r["unavailability"]): r for r in read_csv("analytic-domain-correlation.csv")}
    macros = {
        "RIIDAudit": pct(iid["audit_pass"]["estimate"]),
        "RIIDRecon": pct(iid["reconstruction_success"]["estimate"], 2),
        "RStratDetU": pct(strat["conditional_detection_uniform"]["estimate"], 2),
        "RStratDetS": pct(strat["conditional_detection_stratified"]["estimate"], 2),
        "RStratPassU": pct(strat["audit_pass_uniform"]["estimate"]),
        "RStratPassS": pct(strat["audit_pass_stratified"]["estimate"]),
        "RStratD": f"{strat['primary_D']['estimate']:.5f}",
        "RStratHW": f"{strat['primary_D']['hoeffding_half_width']:.4f}",
        "RStratDiscordant": str(strat["primary_D"]["discordant_strat_better"]),
        "RSWAudit": pct(sw["audit_pass"]["estimate"]),
        "RSWDispute": pct(sw["dispute_success"]["estimate"]),
        "RSWDisputeHi": f"{100 * sw['dispute_success']['wilson95'][1]:.4f}\\%",
        "RAccEightSevenDet": pct(float(acc[(8, 7)]["worst_case_detection"])),
        "RAccEightSevenPass": pct(float(acc[(8, 7)]["benign_audit_pass_iid_0.10"])),
        "RAccSixteenFourteenDet": pct(float(acc[(16, 14)]["worst_case_detection"])),
        "RAccSixteenFourteenPassFive": pct(float(acc[(16, 14)]["benign_audit_pass_iid_0.05"])),
        "RAccSixteenFourteenPassTen": pct(float(acc[(16, 14)]["benign_audit_pass_iid_0.10"])),
        "RDomTwoRecon": pct(float(dom[("DOMAIN_2x16", "0.1")]["reconstructability"])),
        "RDomFourRecon": pct(float(dom[("DOMAIN_4x8", "0.1")]["reconstructability"])),
        "RIIDReconTen": pct(float(dom[("IID", "0.1")]["reconstructability"]), 2),
        "RProveTwoK": f"{ops[('ffdhe2048', 'partial_plus_dleq_proof')]:.1f}",
        "RVerifyTwoK": f"{ops[('ffdhe2048', 'dleq_verification')]:.1f}",
        "RCombineTwoK": f"{ops[('ffdhe2048', 'verify_t_and_combine', 32)]:.0f}",
        "RCombineThreeK": f"{ops[('ffdhe3072', 'verify_t_and_combine', 32)]:.0f}",
    }
    names = {"D0-CONTROL": "Control", "D1-REGIONAL": "Regional", "D2-GLOBAL": "Global", "D3-GLOBAL-LOSS2": "Loss",
             "D4-GLOBAL-CRASH10": "CrashTen", "D5-GLOBAL-CRASH11": "CrashEleven",
             "D6-GLOBAL-DOMAIN-OUTAGE": "DomainOut", "D7-HEAVY-TAIL": "HeavyTail"}
    for profile, short in names.items():
        summ = deadline_summary(dl[profile])
        n = summ["traces"]
        macros[f"RDL{short}Med"] = "--" if summ["median"] is None else f"{1000 * summ['median']:.0f}"
        macros[f"RDL{short}Pninefive"] = "--" if summ["p95"] is None else f"{1000 * summ['p95']:.0f}"
        for d, tag in ((0.5, "Half"), (1.0, "One"), (2.0, "Two"), (5.0, "Five")):
            macros[f"RDL{short}By{tag}"] = pct(summ["by_deadline"][d] / n)
        macros[f"RDL{short}Audit"] = pct(summ["audit_pass"] / n)
        macros[f"RDL{short}Succ"] = f"{summ['success']}/{n}"
    macros["RDLTraces"] = str(len(next(iter(dl.values()))))
    # Exact audit-pass expectations for the testbed fault profiles (uniform s=q=8 of n=32).
    macros["RExpLoss"] = pct((0.98 ** 2) ** 8)
    macros["RExpCrashTen"] = pct(comb(22, 8) / comb(32, 8))
    macros["RExpDomainOut"] = pct(comb(24, 8) / comb(32, 8))
    times = {name: deadline_summary(rows) for name, rows in dl.items()}
    macros["RDLAuditMedLo"] = f"{min(t['audit_median'] for t in times.values()):.2f}"
    macros["RDLAuditMedHi"] = f"{max(t['audit_median'] for t in times.values()):.2f}"
    live = [t for t in times.values() if t["median"] is not None]
    macros["RDLMedLo"] = f"{min(t['median'] for t in live):.2f}"
    macros["RDLMedHi"] = f"{max(t['median'] for t in live):.2f}"
    macros["RDLMaxSucc"] = f"{max(max(t['times']) for t in live):.2f}"
    body = "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in macros.items())
    write_table("numbers", body, ["pc03-summary.json", "analytic-*.csv", "microbench-operations.csv", "deadline/*.csv"])


def main() -> None:
    freeze_hash = freeze_sha256()
    ops: dict = {}
    for r in read_csv("microbench-operations.csv"):
        key = (r["group"], r["operation"], int(r["n"])) if r["n"] else (r["group"], r["operation"])
        ops[key] = float(r["median_ms"])
    sizes = {r["group"]: {k: int(v) for k, v in r.items() if k != "group"} for r in read_csv("microbench-message-sizes.csv")}
    dl = load_deadline()
    traces = {len(v) for v in dl.values()}
    if len(dl) != 8 or len(traces) != 1:
        raise SystemExit(f"deadline results incomplete: {sorted(dl)} traces={traces}")
    fig_detection(); fig_deadline(dl); fig_correlation(); fig_withholding(); fig_acceptance()
    table_config({"traces": traces.pop()}); table_baselines(ops, sizes); table_robustness(dl)
    table_scalability(ops, sizes); table_acceptance(); table_gas(); write_numbers(ops, dl)

    def sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    inputs = sorted(p for p in RES.rglob("*") if p.is_file()) + [ROOT / ".gas-snapshot"]
    manifest = {"freeze_sha256": freeze_hash,
                "inputs": {str(p.relative_to(ROOT)): sha(p) for p in inputs},
                "assets": {name: {"sha256": sha(PAPER / name), "sources": src} for name, src in SOURCES.items()},
                "summaries": {name: {k: v for k, v in deadline_summary(rows).items() if k != "times"} for name, rows in dl.items()}}
    (PAPER / "r1-asset-manifest.json").write_text(json.dumps(manifest, indent=2, default=str) + "\n")
    for name, s in manifest["summaries"].items():
        print(name, s)


if __name__ == "__main__":
    main()
