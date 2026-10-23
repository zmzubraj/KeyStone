"""Figure: selective withholding, audits versus disputes (exact, from the committed R2c table).

Reads research-case/05-analysis/results/r2c/withholding.csv (checked against the R2c freeze hash)
and plots, against the number w of selective withholders, the dispute success probability and the
audit pass probability of three designs, for custodian readiness v = 0.99 (solid) and v = 0.9 (dashed).
Run with any Python that has matplotlib:  python3 paper/jcs/fig_withholding.py
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DESIGN = ROOT / "research-case/03-design/r2c-repair-withholding"
DATA = ROOT / "research-case/05-analysis/results/r2c/withholding.csv"
OUT = HERE / "figures"
SERIES = ["#1f2328", "#2a78d6", "#eb6834", "#1baf7a"]
INK, MUTED, GRID = "#1f2328", "#59636e", "#d8dee4"
plt.rcParams.update({
    "font.family": "serif", "font.size": 8.5, "axes.labelsize": 8.5, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "lines.linewidth": 1.6, "lines.markersize": 4, "savefig.dpi": 300, "pdf.fonttype": 42,
})


def main() -> None:
    fh = hashlib.sha256((DESIGN / "r2c-design-freeze.json").read_bytes()).hexdigest()
    with DATA.open() as f:
        rows = [r for r in csv.DictReader(f)]
    assert all(r["freeze_sha256"] == fh for r in rows), "withholding.csv not stamped with the R2c freeze"
    columns = [("dispute_success", "dispute succeeds"), ("audit_pass_s8q8", "audit passes, (8,8)"),
               ("audit_pass_s16q14", "audit passes, (16,14)"), ("audit_pass_s24q20", "audit passes, (24,20)")]
    fig, ax = plt.subplots(figsize=(4.6, 2.7))
    for v, style in (("0.99", "-"), ("0.9", "--")):
        sub = [r for r in rows if r["v"] == v]
        ws = [int(r["w"]) for r in sub]
        for i, (key, label) in enumerate(columns):
            ax.plot(ws, [float(r[key]) for r in sub], style, color=SERIES[i], marker="o" if i == 0 else None,
                    label=label if v == "0.99" else None)
    ax.set(xlabel="Selective withholders $w$ (of $n=32$, $t=22$)", ylabel="Probability", ylim=(-0.03, 1.03))
    ax.legend(loc="lower left", fontsize=6.5)
    fig.tight_layout()
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "fig8_withholding.pdf", bbox_inches="tight")
    fig.savefig(OUT / "fig8_withholding.png", bbox_inches="tight")
    print("wrote", OUT / "fig8_withholding.pdf")


if __name__ == "__main__":
    main()
