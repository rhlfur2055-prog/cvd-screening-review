"""Screening-value analysis for colour-vision-deficiency (CVD) self-tests.

Every input constant below is taken from a peer-reviewed source listed in
paper/references.md. Everything else (PPV, NPV, missed cases, CIs) is derived
here, so the numbers in the paper can be regenerated with `uv run src/analysis.py`.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
RES = ROOT / "results"

# --- sourced inputs -------------------------------------------------------
# Kim & Ng, Optom Vis Sci 2019 (KNHANES, n=2,686, HRR test)
PREV = {"male": 0.065, "female": 0.011, "overall": 0.039}
N_KNHANES = 2686
# Birch, Ophthalmic Physiol Opt 1997: hidden-digit plates detect ~50% of CVD
SENS_HIDDEN = 0.50
# Birch 1997: transformation + vanishing plates 95.5-99% sensitivity
SENS_TV = (0.955, 0.99)
# Sorkin et al., Optom Vis Sci 2016: app specificity 95.2% (best) vs 54.8% (worst)
SPEC_APP = {"app_high_spec": 0.952, "app_low_spec": 0.548}
# Sorkin 2016 abstract: both apps sensitivity 100% (38/38) -- measured against the
# Ishihara booklet as reference (n=42 normal, 38 colour-deficient), not a gold standard
SENS_APP = 1.0

# --- helpers --------------------------------------------------------------


def ppv(prev: float, sens: float, spec: float) -> float:
    tp = prev * sens
    fp = (1 - prev) * (1 - spec)
    return tp / (tp + fp)


def npv(prev: float, sens: float, spec: float) -> float:
    tn = (1 - prev) * spec
    fn = prev * (1 - sens)
    return tn / (tn + fn)


def wilson(p: float, n: int, z: float = 1.96) -> tuple[float, float]:
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def main() -> None:
    FIG.mkdir(exist_ok=True)
    RES.mkdir(exist_ok=True)
    out: dict = {}

    # Table 1: prevalence with Wilson CI (derived; sex-specific n unknown -> overall only)
    lo, hi = wilson(PREV["overall"], N_KNHANES)
    out["overall_prev_wilson95"] = [round(lo, 4), round(hi, 4)]

    # Table 2: screening value grid
    scen = {
        "hidden-digit plate (sens .50)": (SENS_HIDDEN, 0.95),
        "transformation+vanishing plate (sens .955)": (SENS_TV[0], 0.95),
        "app, best specificity (.952), sens 1.0": (SENS_APP, SPEC_APP["app_high_spec"]),
        "app, worst specificity (.548), sens 1.0": (SENS_APP, SPEC_APP["app_low_spec"]),
    }
    rows = []
    for name, (se, sp) in scen.items():
        for grp, pv in PREV.items():
            rows.append(
                dict(
                    scenario=name, group=grp, prevalence=pv, sens=se, spec=sp,
                    ppv=round(ppv(pv, se, sp), 3), npv=round(npv(pv, se, sp), 4),
                    missed_per_1000=round(1000 * pv * (1 - se), 1),
                    false_alarm_per_1000=round(1000 * (1 - pv) * (1 - sp), 1),
                )
            )
    out["screening_grid"] = rows
    out["note"] = "specificity .95 for plates is an ASSUMPTION (no source); see paper limitations"

    # Figure 1: PPV vs specificity, male vs female, sens .955
    sp_axis = np.linspace(0.5, 0.999, 300)
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=200)
    for grp, col in (("male", "#1f6feb"), ("female", "#d1483b"), ("overall", "#555")):
        ax.plot(sp_axis, [ppv(PREV[grp], SENS_TV[0], s) for s in sp_axis], color=col, label=f"{grp} (prev {PREV[grp]:.1%})")
    for name, s in SPEC_APP.items():
        ax.axvline(s, ls=":", color="#999")
    ax.text(0.552, 0.03, "worst app\nspec .548", fontsize=7, color="#666")
    ax.text(0.90, 0.03, "best app\nspec .952", fontsize=7, color="#666")
    ax.set_xlabel("Specificity")
    ax.set_ylabel("Positive predictive value")
    ax.set_title("PPV of a CVD screen (sensitivity fixed at .955)")
    ax.legend(frameon=False, fontsize=8)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(FIG / "fig1_ppv_vs_specificity.png")
    plt.close(fig)

    # Figure 2: cases missed per 1,000 males by test sensitivity
    labels = ["hidden-digit\n(.50)", "TV plates\n(.955)", "TV plates\n(.99)"]
    sens = [SENS_HIDDEN, *SENS_TV]
    miss = [1000 * PREV["male"] * (1 - s) for s in sens]
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=200)
    bars = ax.bar(labels, miss, color=["#d1483b", "#1f6feb", "#1f6feb"])
    for b, m in zip(bars, miss):
        ax.text(b.get_x() + b.get_width() / 2, m + 0.6, f"{m:.1f}", ha="center", fontsize=9)
    ax.set_ylabel("Missed CVD cases per 1,000 men")
    ax.set_title("Missed cases at Korean male prevalence (6.5%)")
    fig.tight_layout()
    fig.savefig(FIG / "fig2_missed_cases.png")
    plt.close(fig)

    (RES / "screening_grid.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    with (RES / "screening_grid.md").open("w", encoding="utf-8") as f:
        f.write("| Scenario | Group | Prev | Sens | Spec | PPV | NPV | Missed/1000 | False alarms/1000 |\n|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['scenario']} | {r['group']} | {r['prevalence']:.1%} | {r['sens']} | {r['spec']} | {r['ppv']} | {r['npv']} | {r['missed_per_1000']} | {r['false_alarm_per_1000']} |\n")
    print(json.dumps(out["overall_prev_wilson95"]))
    print((RES / "screening_grid.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
