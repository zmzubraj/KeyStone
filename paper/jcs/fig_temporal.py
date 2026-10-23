"""Figure: readiness over time, without and with repair on alarm (exact, declared synthetic model).

For the two scenarios of the paper's temporal table that use custodian MTBF 7 d and MTTR 24 h
(independent custodians; domain shocks with domain MTBF 90 d, MTTR 6 h), plots against the
audit interval T, for the designs (8,8) and (24,20):
* U(T), the probability that a dispute fails and the latest audit accepted (no repair);
* F_rep(T), the probability that a dispute fails when a rejected audit triggers resharing after
  D_r = 1 h, which succeeds only if at least t custodians are ready then (R2d repair rule);
* the floor U_0 and the failure probability without repair, Pr[Z < t], as horizontal lines.
Values are computed directly from keystone_r2.temporal; no data file is read.

Run from prototype/r2:  uv run --locked --extra dev python ../../paper/jcs/fig_temporal.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from keystone_r2 import temporal  # noqa: E402
from keystone_r2.temporal import DAY, DomainShockModel, IndependentModel  # noqa: E402

OUT = Path(__file__).resolve().parent / "figures"
SERIES = ["#2a78d6", "#eb6834"]
INK, MUTED, GRID = "#1f2328", "#59636e", "#d8dee4"
plt.rcParams.update({
    "font.family": "serif", "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "lines.linewidth": 1.6,
    "savefig.dpi": 300, "pdf.fonttype": 42,
})
N, THRESHOLD, REPAIR_DELAY = 32, 22, 1.0
DESIGNS = [(8, 8), (24, 20)]
LAM, MU = 1.0 / (7 * DAY), 1.0 / 24.0
SCENARIOS = [("(a) independent custodians", IndependentModel(N, LAM, MU)),
             ("(b) domain shocks, domain MTBF 90 d", DomainShockModel(N, LAM, MU, 1.0 / (90 * DAY), 1.0 / 6.0))]


def main() -> None:
    Ts = np.geomspace(1.0, 30 * DAY, 36)
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.7), sharey=True)
    for ax, (title, model) in zip(axes, SCENARIOS):
        base = temporal.stationary_catastrophic(model, THRESHOLD)
        ax.axhline(base, color=MUTED, linestyle=":", linewidth=1.0, label="failure without repair")
        for i, (s, q) in enumerate(DESIGNS):
            undetected = [temporal.stationary_undetected(model, T, s, q, THRESHOLD) for T in Ts]
            warm, repaired = None, []
            for T in Ts:
                r = temporal.repair_metrics(model, float(T), s, q, THRESHOLD, REPAIR_DELAY, start=warm, gate=THRESHOLD)
                warm = r["stationary"]
                repaired.append(r["failure"])
            floor = temporal.undetected_floor(model, s, q, THRESHOLD)
            ax.plot(Ts / 24.0, undetected, "--", color=SERIES[i], label=f"$U$, $({s},{q})$")
            ax.plot(Ts / 24.0, repaired, "-", color=SERIES[i], label=f"$F_{{rep}}$, $({s},{q})$")
            ax.axhline(floor, color=SERIES[i], linestyle=(0, (1, 2)), linewidth=0.9, label=f"floor $U_0$, $({s},{q})$")
        ax.set(xscale="log", yscale="log", title=title, xlabel="Audit interval $T$ (days)")
    axes[0].set_ylabel("Probability")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=6.5, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "fig7_temporal.pdf", bbox_inches="tight")
    fig.savefig(OUT / "fig7_temporal.png", bbox_inches="tight")
    print("wrote", OUT / "fig7_temporal.pdf")


if __name__ == "__main__":
    main()
