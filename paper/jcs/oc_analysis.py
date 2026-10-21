"""Exact operating-characteristic analysis of the canary audit for the JCS manuscript.

Writes paper/jcs/tables/t_oc.tex (acceptance probability by number of ready
custodians k) and paper/jcs/tables/jcs_numbers.tex (in-text macros). Everything
is closed form (hypergeometric tails and Wald's sequential-test approximations);
no simulation and no randomness. This analysis was added in response to review
and is reported as post hoc design guidance.

Run: python3 paper/jcs/oc_analysis.py
"""
from math import comb, log
from pathlib import Path

N, T = 32, 22
ALPHA = BETA = 0.05
DESIGNS = [(8, 8), (8, 7), (16, 14), (16, 13), (24, 20)]
KS = [21, 22, 24, 26, 28, 30]
OUT = Path(__file__).resolve().parent / "tables"


def accept(k: int, s: int, q: int) -> float:
    """Pr[audit accepts | exactly k of N custodians ready], uniform sample of size s."""
    return sum(comb(k, j) * comb(N - k, s - j) for j in range(q, min(s, k) + 1)) / comb(N, s)


def smallest_separating_sample(margin: int) -> tuple[int, int]:
    """Smallest s (then smallest q) with false accept <= ALPHA at k=T-1 and pass >= 1-BETA at k=T+margin."""
    for s in range(1, N + 1):
        for q in range(1, s + 1):
            if accept(T - 1, s, q) <= ALPHA and accept(T + margin, s, q) >= 1 - BETA:
                return s, q
    raise ValueError("no separating design")


def sprt_asn(s: int, q: int, margin: int) -> tuple[float, float]:
    """Wald approximations of the expected number of audits under H0 (k=T-1) and H1 (k=T+margin)."""
    p0, p1 = accept(T - 1, s, q), accept(T + margin, s, q)
    a_bound, b_bound = log((1 - BETA) / ALPHA), log(BETA / (1 - ALPHA))
    up, down = log(p1 / p0), log((1 - p1) / (1 - p0))
    ez0 = p0 * up + (1 - p0) * down
    ez1 = p1 * up + (1 - p1) * down
    asn0 = (ALPHA * a_bound + (1 - ALPHA) * b_bound) / ez0
    asn1 = ((1 - BETA) * a_bound + BETA * b_bound) / ez1
    return asn0, asn1


def pct(x: float) -> str:
    return f"{100 * x:.1f}\\%"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    rows = []
    for s, q in DESIGNS:
        cells = " & ".join(pct(accept(k, s, q)) for k in KS)
        rows.append(f"{s} & {q} & {cells}\\\\")
    header = " & ".join(f"$k={k}$" for k in KS)
    table = (
        "\\begin{tabular}{@{}rr" + "r" * len(KS) + "@{}}\n\\toprule\n"
        f" & & \\multicolumn{{{len(KS)}}}{{c}}{{Pr[audit accepts] with $k$ ready custodians ($n=32$, $t=22$)}}\\\\\n"
        f"\\cmidrule(lr){{3-{2 + len(KS)}}}\n$s$ & $q$ & {header}\\\\\n\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n\\end{tabular}\n"
    )
    (OUT / "t_oc.tex").write_text(table)

    sep = {m: smallest_separating_sample(m) for m in (4, 6, 8)}
    asn_8 = sprt_asn(8, 8, 6)
    asn_16 = sprt_asn(16, 14, 6)
    mcnemar_p = 2 * 0.5 ** 28  # exact two-sided sign test on 28 discordant pairs, all one way
    macros = {
        "OcEightTwentyOne": pct(accept(21, 8, 8)),
        "OcEightTwentyTwo": pct(accept(22, 8, 8)),
        "OcEightTwentySix": pct(accept(26, 8, 8)),
        "SepSFour": str(sep[4][0]), "SepQFour": str(sep[4][1]),
        "SepSSix": str(sep[6][0]), "SepQSix": str(sep[6][1]),
        "SepSEight": str(sep[8][0]), "SepQEight": str(sep[8][1]),
        "AsnEightDead": f"{asn_8[0]:.1f}", "AsnEightLive": f"{asn_8[1]:.1f}",
        "AsnSixteenDead": f"{asn_16[0]:.1f}", "AsnSixteenLive": f"{asn_16[1]:.1f}",
        "McNemarP": f"{mcnemar_p:.1e}".replace("e-0", "\\times10^{-").replace("e-", "\\times10^{-") + "}",
    }
    lines = [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in macros.items()]
    (OUT / "jcs_numbers.tex").write_text("\n".join(lines) + "\n")
    print((OUT / "jcs_numbers.tex").read_text())


if __name__ == "__main__":
    main()
