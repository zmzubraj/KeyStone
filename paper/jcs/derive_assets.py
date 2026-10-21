"""Derive the JCS-specific assets from the generated R1 assets.

The JCS manuscript writes k (not r) for the number of ready custodians, because
r denotes a record there. Two R1 assets carry the old symbol: the baseline table
and the y-axis label of the acceptance trade-off figure. This script rebuilds
both under paper/jcs/ from the same stored results and plotting code, so the
R1 assets and their hash manifest stay untouched.

Run with the prototype environment:
    cd prototype && uv run --locked --extra dev python ../paper/jcs/derive_assets.py
"""
from pathlib import Path
import importlib.util

import matplotlib.axes

HERE = Path(__file__).resolve().parent
R1 = HERE.parent / "r1"
BUILDER = HERE.parents[1] / "prototype" / "scripts" / "build_r1_figures_tables.py"

OLD, NEW = "$r=t-1$", "$k=t-1$"


def derive_baseline_table() -> None:
    """Copy the R1 baseline table with the ready-count symbol renamed."""
    text = (R1 / "tables" / "t3_baselines.tex").read_text()
    assert OLD in text, "expected symbol not found in R1 baseline table"
    out = HERE / "tables" / "t3_baselines.tex"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text.replace(OLD, NEW))


def derive_acceptance_figure() -> None:
    """Re-render the acceptance trade-off figure into paper/jcs/figures with k."""
    spec = importlib.util.spec_from_file_location("r1_builder", BUILDER)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    builder.FIG = HERE / "figures"

    original_set = matplotlib.axes.Axes.set

    def set_with_k(self, **kwargs):
        if isinstance(kwargs.get("ylabel"), str):
            kwargs["ylabel"] = kwargs["ylabel"].replace(OLD, NEW)
        return original_set(self, **kwargs)

    matplotlib.axes.Axes.set = set_with_k
    try:
        builder.fig_acceptance()
    finally:
        matplotlib.axes.Axes.set = original_set


def derive_split_robustness_tables() -> None:
    """Split the R1 robustness table into a simulation table and a testbed table.

    The R1 table mixes two meanings of "dispute success" (reconstructability in the
    simulation, success by the 2 s deadline in the testbed); the JCS manuscript
    reports them separately. Rows and values are copied verbatim.
    """
    lines = (R1 / "tables" / "t4_robustness.tex").read_text().splitlines()
    a_start = next(i for i, l in enumerate(lines) if "(a)" in l)
    a_end = next(i for i, l in enumerate(lines) if l.startswith("\\addlinespace"))
    b_start = next(i for i, l in enumerate(lines) if "(b)" in l)
    b_end = next(i for i, l in enumerate(lines) if l.startswith("\\bottomrule"))
    sim_rows = []
    for row in lines[a_start + 1:a_end]:
        cells = [c.strip() for c in row.rstrip("\\").split("&")]
        sim_rows.append(" & ".join(cells[:3]) + "\\\\")
    sim = (
        "\\begin{tabular}{@{}lrr@{}}\n\\toprule\n"
        "Scenario & Audit pass & Reconstructable\\\\\n\\midrule\n"
        + "\n".join(sim_rows) + "\n\\bottomrule\n\\end{tabular}\n"
    )
    bed = (
        "\\begin{tabular}{@{}lrrrrr@{}}\n\\toprule\n"
        "Profile & Audit pass & By $\\Delta_d=2$\\,s & By 5\\,s & Median & p95\\\\\n\\midrule\n"
        + "\n".join(lines[b_start + 1:b_end]) + "\n\\bottomrule\n\\end{tabular}\n"
    )
    (HERE / "tables" / "t4a_simulation.tex").write_text(sim)
    (HERE / "tables" / "t4b_testbed.tex").write_text(bed)


def derive_configuration_table() -> None:
    """Copy the R1 configuration table with the internal cell code name replaced."""
    text = (R1 / "tables" / "t2_configuration.tex").read_text()
    assert "PC03 prespecified cells" in text, "expected label not found in R1 configuration table"
    (HERE / "tables" / "t2_configuration.tex").write_text(text.replace("PC03 prespecified cells", "Simulation cells"))


if __name__ == "__main__":
    derive_baseline_table()
    derive_configuration_table()
    derive_split_robustness_tables()
    derive_acceptance_figure()
    print("derived:", HERE / "tables" / "t3_baselines.tex", HERE / "figures" / "fig6_acceptance_tradeoff.pdf")
