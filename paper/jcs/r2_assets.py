"""Build the R2 tables and in-text numbers of the JCS manuscript from committed R2 results.

Reads only committed files under research-case/05-analysis/results/r2/ (microbenchmark,
deadline testbed summary and per-trace files, temporal exact grid, design and simulation
check) plus the R1 testbed traces for the comparison column, and writes

* tables/r2_numbers.tex      macros used in the text
* tables/t4b_testbed_r2.tex  emulated testbed (R2), with the R1 median for comparison
* tables/t6_operations_r2.tex  per-operation medians for ristretto255, ffdhe2048, ffdhe3072
* tables/t9_temporal.tex     selected cells of the temporal analysis

Every result file is checked against the R2 freeze hash. No number is typed by hand.
Run from the repository root with any Python 3.11+:  python3 paper/jcs/r2_assets.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DESIGN = ROOT / "research-case/03-design/r2-design-amendment"
R2 = ROOT / "research-case/05-analysis/results/r2"
R1_DEADLINE = ROOT / "research-case/05-analysis/results/r1/deadline"
R2B = ROOT / "research-case/05-analysis/results/r2b"
R2B_DESIGN = ROOT / "research-case/03-design/r2b-replication"
R2C = ROOT / "research-case/05-analysis/results/r2c"
R2C_DESIGN = ROOT / "research-case/03-design/r2c-repair-withholding"
TABLES = HERE / "tables"
T_DESIGN = 22  # dispute threshold t of the R2 committee (n = 32)

PROFILES = [("D0-CONTROL", "control"), ("D1-REGIONAL", "regional"), ("D2-GLOBAL", "global"),
            ("D3-GLOBAL-LOSS2", "global loss2"), ("D4-GLOBAL-CRASH10", "global crash10"),
            ("D5-GLOBAL-CRASH11", "global crash11"), ("D6-GLOBAL-DOMAIN-OUTAGE", "global domain outage"),
            ("D7-HEAVY-TAIL", "heavy tail")]


def freeze_hash() -> str:
    actual = hashlib.sha256((DESIGN / "r2-design-freeze.json").read_bytes()).hexdigest()
    recorded = (DESIGN / "r2-design-freeze.SHA256SUMS").read_text().split()[0]
    assert actual == recorded, "R2 freeze hash mismatch"
    return actual


def rows(path: Path) -> list[dict]:
    with path.open() as f:
        return list(csv.DictReader(f))


def pct(x: float, digits: int = 1) -> str:
    return f"{100 * x:.{digits}f}\\%"


def sci(x: float, digits: int = 1) -> str:
    """Compact scientific notation for LaTeX math mode."""
    if x == 0:
        return "0"
    exponent = math.floor(math.log10(abs(x)))
    mantissa = x / 10**exponent
    if round(mantissa, digits) >= 10:
        mantissa, exponent = mantissa / 10, exponent + 1
    return f"{mantissa:.{digits}f}{{\\times}}10^{{{exponent}}}"


def r1_median_ms(profile_id: str) -> float | None:
    data = rows(R1_DEADLINE / f"{profile_id}.csv")
    times = sorted(float(r["dispute_time_s"]) if r["dispute_success"] == "True" and r["dispute_time_s"]
                   else math.inf for r in data)
    point = times[math.ceil(0.5 * len(times)) - 1]
    return None if math.isinf(point) else 1000 * point


def r2b_assets(r2_summary: dict) -> dict:
    """R2 + R2b testbed table and macros for the replication, calibration and model check."""
    sums = (R2B_DESIGN / "r2b-design-freeze.SHA256SUMS").read_text().split()
    fh = hashlib.sha256((R2B_DESIGN / "r2b-design-freeze.json").read_bytes()).hexdigest()
    assert fh == sums[0], "R2b freeze hash mismatch"
    rb = {(r["variant"], r["profile_id"]): r for r in rows(R2B / "deadline/r2b-summary.csv")}
    paired = {r["profile_id"]: r for r in rows(R2B / "deadline/r2b-paired.csv")}
    assert all(r["freeze_sha256"] == fh for r in list(rb.values()) + list(paired.values())) and len(rb) == 16
    calib = json.loads((R2B / "calibration/calibration-summary.json").read_text())
    pred = {(r["variant"], r["profile_id"], r["endpoint"]): r
            for r in rows(R2 / "deadline/deadline-predictions.csv")}

    def rate(r: dict, key: str = "rate") -> str:
        return pct(float(r[key]))

    def wil(r: dict) -> str:
        lo, hi = (float(x) for x in r["wilson95"].strip("[]").split(","))
        return f"[{100 * lo:.1f}, {100 * hi:.1f}]"

    def ms(x: float) -> str:
        return f"{x:.1f}" if x < 10 else f"{x:.0f}"

    lines = ["\\begin{tabular}{@{}lrrrrrrrr@{}}", "\\toprule",
             " & \\multicolumn{3}{c}{R2 (frozen deadline)} & \\multicolumn{4}{c}{R2b (corrected deadline, fresh traces)} & R1\\\\",
             "\\cmidrule(lr){2-4}\\cmidrule(lr){5-8}\\cmidrule(l){9-9}",
             "Profile & $\\Delta_d^{*}$ & serial & batch & $\\Delta_{os}$ & serial & batch & median & median\\\\",
             " & (ms) & & & (ms) & & & (ms) & (ms)\\\\", "\\midrule"]
    for pid, name in PROFILES:
        s2, b2 = r2_summary[("SERIAL", pid)], r2_summary[("BATCH", pid)]
        sb, bb = rb[("SERIAL", pid)], rb[("BATCH", pid)]
        dstar = 1000 * float(s2["primary_deadline_s"])
        dos = "--" if sb["delta_os_ms"] == "none" else ms(float(sb["delta_os_ms"]))
        med = "--" if sb["completion_median_s"] == "censored" else ms(1000 * float(sb["completion_median_s"]))
        r1 = r1_median_ms(pid)
        lines.append(f"{name} & {ms(dstar)} & {rate(s2, 'primary_rate')} & {rate(b2, 'primary_rate')} & {dos} & "
                     f"{rate(sb)} {wil(sb)} & {rate(bb)} & {med} & {'--' if r1 is None else f'{r1:.0f}'}\\\\")
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    (TABLES / "t4b_testbed_r2b.tex").write_text("\n".join(lines))

    delayed = [p for p, _ in PROFILES if p not in ("D0-CONTROL", "D5-GLOBAL-CRASH11")]
    slow = [float(paired[p]["median_batch_minus_serial_ms"]) for p in delayed]
    sign_p = max(float(paired[p]["sign_test_exact_p"]) for p in delayed)
    meets = sum(rb[("SERIAL", p)]["meets_criterion"] == "True" for p, _ in PROFILES)
    audits = sum(r["audit_expected_in_wilson95"] == "True" for r in rb.values())
    d4 = rb[("SERIAL", "D4-GLOBAL-CRASH10")]
    s0, b0r, b1 = rb[("SERIAL", "D0-CONTROL")], rb[("BATCH", "D0-CONTROL")], rb[("BATCH", "D1-REGIONAL")]
    return {
        "RtwobBzero": f"{calib['B0_ms']:.2f}",
        "RtwobCalibMed": f"{calib['FULL_PATH_ZERO_DELAY']['median_ms']:.2f}",
        "RtwobNullMed": f"{calib['THREAD']['median_ms']:.2f}",
        "RtwobHandoffUs": f"{1000 * calib['handoff_per_response_ms']:.0f}",
        "RtwobMeets": str(meets),
        "RtwobControlSucc": s0["success_by_delta_os"], "RtwobControlRate": rate(s0), "RtwobControlWilson": wil(s0),
        "RtwobControlMed": ms(1000 * float(s0["completion_median_s"])),
        "RtwobControlBatch": rate(b0r), "RtwobRegionalBatch": rate(b1),
        "RtwobOsGlobal": ms(float(rb[("SERIAL", "D2-GLOBAL")]["delta_os_ms"])),
        "RtwobOsHeavy": ms(float(rb[("SERIAL", "D7-HEAVY-TAIL")]["delta_os_ms"])),
        "RtwobDfourAtDstar": rate(d4, "rate_at_r2_delta_d_star"),
        "RtwoDfourPred": pct(float(pred[("SERIAL", "D4-GLOBAL-CRASH10", "primary")]["predicted"])),
        "RtwobAuditInside": str(audits),
        "RtwobBatchSlowLo": f"{min(slow):.0f}", "RtwobBatchSlowHi": f"{max(slow):.0f}",
        "RtwobBatchFastZero": f"{-float(paired['D0-CONTROL']['median_batch_minus_serial_ms']):.1f}",
        "RtwobSignPBound": f"10^{{{math.floor(math.log10(sign_p)) + 1}}}",
    }


def r2c_assets() -> dict:
    """Repair-on-alarm design table and macros for repair and selective withholding (R2c)."""
    fh = hashlib.sha256((R2C_DESIGN / "r2c-design-freeze.json").read_bytes()).hexdigest()
    assert fh == (R2C_DESIGN / "r2c-design-freeze.SHA256SUMS").read_text().split()[0], "R2c freeze hash mismatch"
    grid, design = rows(R2C / "repair-grid.csv"), rows(R2C / "repair-design.csv")
    sim, wh, coal = rows(R2C / "repair-sim-check.csv"), rows(R2C / "withholding.csv"), rows(R2C / "withholding-coalition.csv")
    assert all(r["freeze_sha256"] == fh for r in grid + design + sim + wh + coal)

    def g(shock: str, mtbf: str, mttr: str, T: str, dr: str, s_: str) -> dict:
        return next(r for r in grid if (r["domain_shock"], r["mtbf_days"], r["mttr_hours"], r["T_hours"],
                                        r["repair_delay_hours"], r["s"]) == (shock, mtbf, mttr, T, dr, s_))

    def dsg(shock: str, mtbf: str, mttr: str, dr: str, s_: str, target: str) -> dict:
        return next(r for r in design if (r["domain_shock"], r["mtbf_days"], r["mttr_hours"], r["repair_delay_hours"],
                                          r["s"], r["target"]) == (shock, mtbf, mttr, dr, s_, target))

    scenarios = [("IID", "none"), ("Shock 365\\,d", "MTBF_d=365d,MTTR_d=6h"), ("Shock 90\\,d", "MTBF_d=90d,MTTR_d=6h")]
    designs = [("8", "8"), ("16", "14"), ("24", "20")]
    lines = ["\\begin{tabular}{@{}llrrrrr@{}}", "\\toprule",
             "Scenario & $(s,q)$ & no repair & $T^{*}$ (h) & audits/day & resharings/day & benign\\\\", "\\midrule"]
    for label, shock in scenarios:
        for i, (s_, q_) in enumerate(designs):
            r = dsg(shock, "7", "24", "1", s_, "0.0001")
            base = float(g(shock, "7", "24", "6", "1", s_)["failure_no_repair"])
            if r["status"] == "infeasible_at_lo":
                cells = ["none", "--", "--", "--"]
            else:
                cells = [f"{float(r['continuous_T_hours']):.1f}", f"{float(r['audits_per_day_at_T']):.2f}",
                         f"{float(r['repairs_per_day_at_T']):.2f}", pct(float(r["benign_fraction_at_T"]), 2)]
            lines.append(f"{label if i == 0 else ''} & ({s_},{q_}) & {'$' + sci(base) + '$' if i == 0 else ''} & "
                         + " & ".join(cells) + "\\\\")
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    (TABLES / "t10_repair.tex").write_text("\n".join(lines))

    informative = [r for r in sim if r["vacuous"] == "False"]
    lowered = sum(float(r["failure_with_repair"]) <= float(r["failure_no_repair"]) * (1 + 1e-9) for r in grid)
    nonmono = [r for r in design if r["monotone_on_check_grid"] == "False"]
    assert all(r["status"] != "bisected" for r in nonmono), "a bisected interval depends on a non-monotone metric"
    benign = [float(r["benign_fraction"]) for r in grid if float(r["p_reject"]) > 0]
    iid6 = g("none", "7", "24", "6", "1", "8")
    w = {(r["v"], r["w"]): r for r in wh}
    cmin = {(r["v"], r["failure_target"], r["p_a"]): r for r in coal}
    return {
        "RepRows": str(len(grid)), "RepLowered": str(lowered),
        "RepSimInfo": str(len(informative)), "RepSimInfoPass": str(sum(r["wilson_pass"] == "True" for r in informative)),
        "RepSimVacuous": str(len(sim) - len(informative)),
        "RepNonMono": str(len(nonmono)), "RepDesignRows": str(len(design)),
        "RepBenignMin": pct(min(benign), 0),
        "RepIIDNoRep": sci(float(iid6["failure_no_repair"])), "RepIIDSix": sci(float(iid6["failure_with_repair"])),
        "RepIIDSixPerDay": f"{float(iid6['repairs_per_day']):.2f}",
        "WhSuccTen": pct(float(w[("0.99", "10")]["dispute_success"])),
        "WhAuditEleven": pct(float(w[("0.99", "11")]["audit_pass_s8q8"])),
        "WhAuditZero": pct(float(w[("0.99", "0")]["audit_pass_s8q8"])),
        "WhMinHigh": cmin[("0.99", "0.5", "1.0")]["w_min"], "WhMinLow": cmin[("0.9", "0.5", "1.0")]["w_min"],
        "WhStakeLo": f"{float(cmin[('0.99', '0.5', '1.0')]['stake_to_value_ratio']):.2f}",
        "WhStakeHi": f"{float(cmin[('0.99', '0.5', '0.5')]['stake_to_value_ratio']):.2f}",
    }


def write_configuration_table() -> None:
    """Extend the derived configuration table (derive_assets.py) with the R2 experiment families."""
    lines = (TABLES / "t2_configuration.tex").read_text().splitlines()
    crypto = next(i for i, l in enumerate(lines) if l.startswith("Cryptographic cost"))
    bed = next(i for i, l in enumerate(lines) if l.startswith("Deadline testbed"))
    lines[crypto] = ("Cryptographic cost & R1: ffdhe groups, $n\\le 128$. R2: ristretto255 and ffdhe, 1{,}000 runs "
                     "& Microbenchmark, CPython 3.13, Apple M4 Pro\\\\")
    lines[bed] = ("Deadline testbed & R2 and R2b (fresh paired seeds): ristretto255, TDH2, $n=32,t=22$; "
                  "8 profiles $\\times$ 300 traces $\\times$ 2 variants; lognormal delay (median 0/40/120\\,ms), "
                  "loss, crashes, domain outage & 32 processes on one host; emulation\\\\")
    lines.insert(bed + 1, "Temporal readiness & MTBF 7/30/90\\,d, MTTR 1/6/24\\,h, $T$ 1/6/24\\,h, "
                          "$(s,q)$ $(8,8)$/$(16,14)$/$(24,20)$; domain shocks & Exact, synthetic; "
                          "3-cell simulation check\\\\")
    lines.insert(bed + 2, "Repair and withholding (R2c) & Same grid with resharing after $D_r\\in\\{0.25,1\\}$\\,h; "
                          "$w\\le 11$ withholders, $v\\in\\{0.9,0.99,0.999\\}$ & Exact, synthetic; "
                          "3-cell simulation check\\\\")
    (TABLES / "t2_configuration_r2.tex").write_text("\n".join(lines) + "\n")


def main() -> None:
    fh = freeze_hash()
    macros: dict[str, str] = {}

    # ---------------------------------------------------------------- microbenchmark
    micro = {(r["group"], r["operation"]): float(r["median_ms"]) for r in rows(R2 / "microbench-summary.csv")
             if r["freeze_sha256"] == fh}
    assert len(micro) == 27, "microbenchmark summary incomplete or not stamped with the freeze hash"
    ops = [("Canary derivation $H_G$", "canary_derivation"),
           ("Partial decryption + DLEQ proof", "partial_plus_dleq_proof"),
           ("DLEQ verification", "dleq_verification_serial"),
           ("Batch verification of $t=22$ proofs", "dleq_batch_verification_t"),
           ("Seal 1\\,KiB, plain KEM", "seal_1KiB_plain_kem"),
           ("Seal 1\\,KiB, TDH2", "seal_1KiB_tdh2"),
           ("TDH2 ciphertext-proof check", "tdh2_ciphertext_proof_verification"),
           ("Combine $t$ partials, unwrap, decrypt", "combine_t_plus_unwrap_decrypt")]
    groups = ["ristretto255", "ffdhe2048", "ffdhe3072"]

    def ms(x: float) -> str:
        return f"{x:.3f}" if x < 1 else f"{x:.2f}" if x < 100 else f"{x:.1f}"

    lines = ["\\begin{tabular}{@{}lrrr@{}}", "\\toprule",
             "Operation (median, ms) & ristretto255 & ffdhe2048 & ffdhe3072\\\\", "\\midrule"]
    lines += [f"{label} & " + " & ".join(ms(micro[(g, op)]) for g in groups) + "\\\\" for label, op in ops]
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    (TABLES / "t6_operations_r2.tex").write_text("\n".join(lines))

    verify = {g: micro[(g, "dleq_verification_serial")] for g in groups}
    batch_speedup = {g: T_DESIGN * verify[g] / micro[(g, "dleq_batch_verification_t")] for g in groups}
    macros.update({
        "RtwoVerifyRis": f"{verify['ristretto255']:.2f}",
        "RtwoVerifyTwoK": f"{verify['ffdhe2048']:.1f}",
        "RtwoProveRis": f"{micro[('ristretto255', 'partial_plus_dleq_proof')]:.3f}",
        "RtwoCombineRis": f"{micro[('ristretto255', 'combine_t_plus_unwrap_decrypt')]:.2f}",
        "RtwoSealTdhRis": f"{micro[('ristretto255', 'seal_1KiB_tdh2')]:.3f}",
        "RtwoCtCheckRis": f"{micro[('ristretto255', 'tdh2_ciphertext_proof_verification')]:.3f}",
        "RtwoTcvRis": f"{T_DESIGN * verify['ristretto255']:.1f}",
        "RtwoTcvTwoK": f"{T_DESIGN * verify['ffdhe2048']:,.0f}".replace(",", "{,}"),
        "RtwoBatchRis": f"{batch_speedup['ristretto255']:.2f}",
        "RtwoBatchTwoK": f"{batch_speedup['ffdhe2048']:.2f}",
        "RtwoBatchThreeK": f"{batch_speedup['ffdhe3072']:.2f}",
    })

    # ---------------------------------------------------------------- deadline testbed
    summary = {(r["variant"], r["profile_id"]): r for r in rows(R2 / "deadline/deadline-summary.csv")}
    assert all(r["freeze_sha256"] == fh for r in summary.values()) and len(summary) == 16

    def rate_cell(r: dict) -> str:
        lo, hi = (float(x) for x in r["primary_wilson95"].strip("[]").split(","))
        return f"{pct(float(r['primary_rate']))} [{100 * lo:.1f}, {100 * hi:.1f}]"

    def time_ms(value: str) -> str:
        if value == "censored":
            return "--"
        x = 1000 * float(value)
        return f"{x:.1f}" if x < 10 else f"{x:.0f}"

    lines = ["\\begin{tabular}{@{}lrrrrrrr@{}}", "\\toprule",
             "Profile & $\\Delta_d^{*}$ & Audit pass & By $\\Delta_d^{*}$, serial & By $\\Delta_d^{*}$, batch"
             " & Median & p95 & R1 median\\\\",
             " & (ms) & (exact) & & & (ms) & (ms) & (ms)\\\\", "\\midrule"]
    audits_inside = 0
    for pid, name in PROFILES:
        s, b = summary[("SERIAL", pid)], summary[("BATCH", pid)]
        audits_inside += (s["audit_expected_in_wilson95"] == "True") + (b["audit_expected_in_wilson95"] == "True")
        r1 = r1_median_ms(pid)
        lines.append(f"{name} & {time_ms(s['primary_deadline_s'])} & "
                     f"{pct(float(s['audit_pass_rate']))} ({pct(float(s['audit_pass_expected']))}) & "
                     f"{rate_cell(s)} & {pct(float(b['primary_rate']))} & {time_ms(s['completion_median_s'])} & "
                     f"{time_ms(s['completion_p95_s'])} & {'--' if r1 is None else f'{r1:.0f}'}\\\\")
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    (TABLES / "t4b_testbed_r2.tex").write_text("\n".join(lines))

    s = lambda pid: summary[("SERIAL", pid)]  # noqa: E731
    b = lambda pid: summary[("BATCH", pid)]  # noqa: E731
    d0_med_ms = 1000 * float(s("D0-CONTROL")["completion_median_s"])
    macros.update({
        "RtwoTraces": str(int(s("D0-CONTROL")["traces"])),
        "RtwoTracesTotal": f"{16 * int(s('D0-CONTROL')['traces']):,}".replace(",", "{,}"),
        "RtwoControlDstar": f"{float(s('D0-CONTROL')['primary_deadline_s']) * 1000:.2f}",
        "RtwoControlMed": f"{d0_med_ms:.1f}",
        "RtwoControlSucc": s("D0-CONTROL")["primary_success"],
        "RtwoControlSpeedup": f"{r1_median_ms('D0-CONTROL') / d0_med_ms:.0f}",
        "RtwoGlobalMed": time_ms(s("D2-GLOBAL")["completion_median_s"]),
        "RtwoGlobalDstar": f"{float(s('D2-GLOBAL')['primary_deadline_s']) * 1000:.0f}",
        "RtwoMedLo": time_ms(s("D1-REGIONAL")["completion_median_s"]),
        "RtwoMedHi": time_ms(s("D4-GLOBAL-CRASH10")["completion_median_s"]),
        "RtwoHeavyPninefive": time_ms(s("D7-HEAVY-TAIL")["completion_p95_s"]),
        "RtwoCrashTenSerial": pct(float(s("D4-GLOBAL-CRASH10")["primary_rate"])),
        "RtwoCrashTenBatch": pct(float(b("D4-GLOBAL-CRASH10")["primary_rate"])),
        "RtwoCrashTenPninefive": time_ms(s("D4-GLOBAL-CRASH10")["completion_p95_s"]),
        "RtwoAuditInside": str(audits_inside),
        "RtwoCrashElevenSucc": s("D5-GLOBAL-CRASH11")["dispute_success_any_time"],
    })

    # ---------------------------------------------------------------- temporal
    grid = rows(R2 / "temporal/exact-grid.csv")
    design = rows(R2 / "temporal/design.csv")
    sim = rows(R2 / "temporal/sim-check.csv")
    assert all(r["freeze_sha256"] == fh for r in grid + design + sim)

    def cell(shock: str, mtbf: str, mttr: str, T: str, s_: str, q_: str) -> dict:
        return next(r for r in grid if (r["domain_shock"], r["mtbf_days"], r["mttr_hours"], r["T_hours"], r["s"],
                                        r["q"]) == (shock, mtbf, mttr, T, s_, q_))

    def interval(shock: str, mtbf: str, mttr: str, s_: str, q_: str, metric: str, target: str) -> dict:
        return next(r for r in design if (r["domain_shock"], r["mtbf_days"], r["mttr_hours"], r["s"], r["q"],
                                          r["metric"], r["target"]) == (shock, mtbf, mttr, s_, q_, metric, target))

    def t_star(r: dict) -> str:
        if r["status"] == "infeasible_at_lo":
            return "none"
        if r["status"] == "feasible_at_hi":
            return "$\\ge$720"
        return f"{float(r['continuous_T_hours']):.1f}"

    scenarios = [("IID, 7\\,d / 24\\,h", "none", "7", "24"),
                 ("IID, 30\\,d / 24\\,h", "none", "30", "24"),
                 ("Shock 365\\,d, 30\\,d / 6\\,h", "MTBF_d=365d,MTTR_d=6h", "30", "6"),
                 ("Shock 90\\,d, 30\\,d / 6\\,h", "MTBF_d=90d,MTTR_d=6h", "30", "6"),
                 ("Shock 90\\,d, 7\\,d / 24\\,h", "MTBF_d=90d,MTTR_d=6h", "7", "24")]
    designs = [("8", "8"), ("24", "20")]
    lines = ["\\begin{tabular}{@{}lrrrrrrr@{}}", "\\toprule",
             " & & \\multicolumn{2}{c}{$U$, $T=6$\\,h}"
             " & \\multicolumn{2}{c}{$U_0$} & \\multicolumn{2}{c}{$T^{*}$ (h), $\\varepsilon=10^{-4}$}\\\\",
             "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}\\cmidrule(l){7-8}",
             "Scenario & $\\Pr[Z<t]$ & (8,8) & (24,20) & (8,8) & (24,20) & (8,8) & (24,20)\\\\",
             "\\midrule"]
    for label, shock, mtbf, mttr in scenarios:
        c = {d: cell(shock, mtbf, mttr, "6", *d) for d in designs}
        first = c[designs[0]]
        parts = [label, f"${sci(float(first['stationary_catastrophic']))}$"]
        parts += [f"${sci(float(c[d]['metric2_undetected']))}$" for d in designs]
        parts += [f"${sci(float(c[d]['metric2_floor_T0']))}$" for d in designs]
        parts += [t_star(interval(shock, mtbf, mttr, *d, "metric2_undetected", "0.0001")) for d in designs]
        lines.append(" & ".join(parts) + "\\\\")
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    (TABLES / "t9_temporal.tex").write_text("\n".join(lines))

    informative = [r for r in sim if int(r["successes"]) > 0]
    exact_iid = interval("none", "7", "24", "8", "8", "metric2_undetected", "0.0001")
    bound_iid = interval("none", "7", "24", "8", "8", "metric2_bound_closed_form", "0.0001")
    post_iid = interval("none", "7", "24", "8", "8", "metric1_posterior_worst", "0.0001")
    shock_cell = cell("MTBF_d=90d,MTTR_d=6h", "30", "6", "6", "8", "8")
    iid_cell = cell("none", "30", "6", "6", "8", "8")
    hard = cell("MTBF_d=90d,MTTR_d=6h", "7", "24", "6", "8", "8")
    hard_wide = interval("MTBF_d=90d,MTTR_d=6h", "7", "24", "24", "20", "metric2_undetected", "0.0001")

    def compare(shocked: bool) -> tuple[int, int, int]:
        """Cells where (24,20) has a larger U than (8,8), and how many of those also accept more often."""
        worse = total = accepts_more = 0
        for r in grid:
            if r["s"] != "8" or (r["domain_shock"] != "none") != shocked:
                continue
            o = cell(r["domain_shock"], r["mtbf_days"], r["mttr_hours"], r["T_hours"], "24", "20")
            total += 1
            if float(o["metric2_undetected"]) > float(r["metric2_undetected"]):
                worse += 1
                accepts_more += float(o["stationary_accept"]) > float(r["stationary_accept"])
        return worse, total, accepts_more

    shock_worse, shock_total, shock_acc = compare(True)
    iid_worse, iid_total, iid_acc = compare(False)
    assert shock_acc == shock_worse and iid_acc == iid_worse, "explanation by acceptance rate does not hold"
    bound_rows = [r for r in grid if r["metric2_bound_closed_form"]]
    assert all(float(r["metric2_bound_closed_form"]) >= float(r["metric2_undetected"]) * (1 - 1e-12)
               for r in bound_rows)
    assert all(float(r["metric2_undetected"]) >= float(r["metric2_floor_T0"]) * (1 - 1e-12) for r in grid)
    macros.update({
        "TmpSimInfo": str(len(informative)),
        "TmpSimInfoPass": str(sum(r["wilson_pass"] == "True" for r in informative)),
        "TmpSimVacuous": str(len(sim) - len(informative)),
        "TmpExactIntervalIID": f"{float(exact_iid['continuous_T_hours']):.1f}",
        "TmpBoundIntervalIID": f"{float(bound_iid['continuous_T_hours']):.1f}",
        "TmpPostIntervalIID": f"{float(post_iid['continuous_T_hours']):.1f}",
        "TmpHardWideMin": f"{60 * float(hard_wide['continuous_T_hours']):.0f}",
        "TmpCatIID": sci(float(iid_cell["stationary_catastrophic"])),
        "TmpCatShock": sci(float(shock_cell["stationary_catastrophic"])),
        "TmpFloorHard": sci(float(hard["metric2_floor_T0"])),
        "TmpGridCells": str(len(grid)),
        "TmpBoundCells": str(len(bound_rows)),
        "TmpShockWorse": str(shock_worse), "TmpShockTotal": str(shock_total),
        "TmpIidWorse": str(iid_worse), "TmpIidTotal": str(iid_total),
    })

    write_configuration_table()
    macros.update(r2b_assets(summary))
    macros.update(r2c_assets())

    header = [f"% Generated by paper/jcs/r2_assets.py from committed R2 results; R2 freeze {fh[:12]}."]
    (TABLES / "r2_numbers.tex").write_text(
        "\n".join(header + [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in macros.items()]) + "\n")
    print(json.dumps(macros, indent=1))


if __name__ == "__main__":
    main()
