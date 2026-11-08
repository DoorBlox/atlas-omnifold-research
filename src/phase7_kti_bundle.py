"""Checksum-verified descriptive KTI evidence bundle from frozen ATLAS 2x2 moments.

Produces publication-oriented vector figures, numerical tables, source variance
accounting, reproducibility hashes and a Methods/Results draft. This is a
SECONDARY analysis, not an official ATLAS 2D covariance algorithm. Never
evaluate or publish a real-data compatibility p-value (G15 NO-GO).

Usage:
    python -m src.phase7_kti_bundle --v1 data/derived/phase7-v1 \
        --v2 data/derived/phase7-v2 --out outputs/four-cell-v1
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

from src.phase7_interaction import CELLS, load_fractions
from src.phase7_joint_reference import (
    SCENARIOS, analyze as analyze_joint, shared_observable_variance,
    validate_covariance,
)
from src.phase7_source_accounting import (
    STOCHASTIC_SOURCES, audit_components, read_manifest,
)
from src.phase7_v2_reconstruct import wsum

OBSERVABLES = ("mass_low", "multiplicity_low", "joint_log_odds")
MODEL_NAMES = tuple(x[0] for x in SCENARIOS)
MODEL_LABELS = {
    "both_fully_correlated": "DD full / Sherpa full",
    "dd_decorrelated_sherpa_correlated": "DD four-bin / Sherpa full",
    "dd_correlated_sherpa_decorrelated": "DD full / Sherpa four-bin",
    "both_four_bin_decorrelated": "DD four-bin / Sherpa four-bin",
}
REFERENCE_LABELS = {
    "real": ("ATLAS unfolded real data", "shared nominal generator",
             "shared_nominal_generator"),
    "pseudo": ("ATLAS unfolded pseudodata", "independent known target truth",
               "independent_known_truth"),
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("Refuse to write an empty numerical table")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _observables(p: np.ndarray) -> tuple[dict[str, float], dict[str, np.ndarray]]:
    p = np.asarray(p, dtype=float)
    if p.shape != (4,) or not np.isfinite(p).all() or np.min(p) <= 0:
        raise ValueError("All four normalized cells must be strictly positive")
    if not np.isclose(p.sum(), 1., rtol=0, atol=1e-8):
        raise ValueError("Normalized shape does not sum to one")
    values = {
        "mass_low": float(p[0] + p[1]),
        "multiplicity_low": float(p[0] + p[2]),
        "joint_log_odds": float(math.log((p[0]*p[3])/(p[1]*p[2]))),
    }
    gradients = {
        "mass_low": np.array([1., 1., 0., 0.]),
        "multiplicity_low": np.array([1., 0., 1., 0.]),
        "joint_log_odds": np.array([1/p[0], -1/p[1], -1/p[2], 1/p[3]]),
    }
    return values, gradients


def _paired_inputs(nominal: dict) -> tuple[np.ndarray, ...]:
    hp = wsum(nominal, "weights_nominal")
    hq = wsum(nominal, "weight_mc")
    spp = wsum(nominal, "weights_nominal", "sum_w2")
    sqq = wsum(nominal, "weight_mc", "sum_w2")
    spq = wsum(nominal, "weight_mc", "sum_w_times_nominal")
    return hp, hq, spp, sqq, spq


def _source_rows(kind: str, p: np.ndarray, q: np.ndarray, parts: dict,
                 model_metrics: dict, manifest: dict, paired: tuple | None) -> list[dict]:
    _, gp = _observables(p)
    _, gq = _observables(q)
    rows = []
    for observable in OBSERVABLES:
        total_variance = float(model_metrics["observables"][observable]["conditional_standard_error"]) ** 2
        if total_variance <= 0:
            raise ValueError("Conditional source variance must be positive")
        entries = []
        for name, c in parts.items():
            if kind == "real" and name == "finite_evaluation_mc":
                if paired is None:
                    raise ValueError("Missing real-generator paired event moments")
                var = shared_observable_variance(*paired, gp[observable], gq[observable])
                scope = "paired_generator_and_unfolded"
            elif kind == "pseudo" and name == "independent_truth_finite_mc":
                var = float(gq[observable] @ c @ gq[observable])
                scope = "independent_target_truth"
            else:
                var = float(gp[observable] @ c @ gp[observable])
                scope = "unfolded_measurement_only"
            if not math.isfinite(var) or var < -1e-12:
                raise ValueError(f"Invalid source variance {kind}/{observable}/{name}: {var}")
            entries.append((name, max(var, 0.), scope))
        if not np.isclose(sum(v for _, v, _ in entries), total_variance,
                          rtol=1e-8, atol=1e-12):
            raise ValueError(f"Comparator-aware source variance does not close: {kind}/{observable}")
        for name, var, scope in sorted(entries, key=lambda x: (-x[1], x[0])):
            rows.append({
                "sample": kind,
                "observable": observable,
                "source": name,
                "family": manifest.get(name, "independent_truth_reference_statistic"),
                "covariance_scope": scope,
                "variance": var,
                "fraction_of_total_conditional_variance": var / total_variance,
                "source_model": "provisional_both_fully_correlated",
            })
    return rows


def _svg_document(title: str, description: str, elements: list[str],
                  width: int = 1060, height: int = 760) -> str:
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
        f'<title>{escape(title)}</title><desc>{escape(description)}</desc>'
        '<style>'
        'text{font-family:Arial,Helvetica,sans-serif;fill:#18314a}'
        '.title{font-size:26px;font-weight:bold}'
        '.subtitle{font-size:15px;fill:#506779}'
        '.panel{font-size:19px;font-weight:bold}'
        '.label{font-size:14px}'
        '.value{font-size:16px;font-weight:bold}'
        '.small{font-size:12px;fill:#52677a}'
        '</style>'
        '<rect width="100%" height="100%" fill="#ffffff"/>'
    )
    return head + "".join(elements) + "</svg>"


def _svg_text(x: float, y: float, value: str, cls: str = "label",
              anchor: str = "start") -> str:
    return (f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" '
            f'text-anchor="{anchor}">{escape(str(value))}</text>')


def _svg_rect(x: float, y: float, w: float, h: float, fill: str,
              stroke: str = "none", radius: int = 0) -> str:
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" '
            f'height="{max(h, 0):.1f}" fill="{fill}" stroke="{stroke}" rx="{radius}"/>')


def _heat_color(frac: float) -> str:
    t = min(max(frac / 0.5, 0.), 1.)
    return f"rgb({round(238-149*t)},{round(247-85*t)},{round(249-44*t)})"


def _figure_joint(samples: dict) -> str:
    panels = [
        ("Real ATLAS unfolded", samples["real"]["measurement"]),
        ("Nominal generator", samples["real"]["reference"]),
        ("Unfolded pseudodata", samples["pseudo"]["measurement"]),
        ("Independent known truth", samples["pseudo"]["reference"]),
    ]
    el = [
        _svg_text(48, 52, "Charged-jet mass × track multiplicity", "title"),
        _svg_text(48, 80, "Normalized weighted fractions; fixed generator-defined thresholds", "subtitle"),
    ]
    for i, (name, shape) in enumerate(panels):
        left = 50 + (i % 2) * 515
        top = 112 + (i // 2) * 310
        el.append(_svg_rect(left, top, 465, 282, "#f6f9fb", "#dbe4eb", 10))
        el.append(_svg_text(left + 20, top + 31, name, "panel"))
        bx, by, side = left + 133, top + 61, 82
        el.append(_svg_text(bx + 41, by - 8, "Mass low", "label", "middle"))
        el.append(_svg_text(bx + 123, by - 8, "Mass high", "label", "middle"))
        for rr in range(2):
            el.append(_svg_text(bx - 14, by + rr*side + 48,
                                "Tracks low" if rr == 0 else "Tracks high",
                                "label", "end"))
            for cc in range(2):
                idx = ((0, 2), (1, 3))[rr][cc]
                val = float(shape[idx])
                el.append(_svg_rect(bx + cc*side, by + rr*side,
                                    side-2, side-2, _heat_color(val), "#ffffff", 3))
                el.append(_svg_text(bx + cc*side + 40, by + rr*side + 38,
                                    f"{val:.2%}", "value", "middle"))
                el.append(_svg_text(bx + cc*side + 40, by + rr*side + 60,
                                    CELLS[idx], "small", "middle"))
        el.append(_svg_text(left + 20, top + 260, "LL, LH, HL, HH: mass level first, tracks second", "small"))
    el.append(_svg_text(50, 746, "ATLAS 2024 released weights | Frozen 2×2 descriptive projection | G15 NO-GO", "small"))
    return _svg_document("Four source-backed ATLAS joint shapes",
                         "Actual real, generator, pseudodata and independent truth four-cell fractions",
                         el, height=760)


def _figure_differences(joint_rows: list[dict], marginal_rows: list[dict]) -> str:
    data = {}
    for kind in ("real", "pseudo"):
        d = [(row["cell"], float(row["delta_fraction"])) for row in joint_rows if row["sample"] == kind]
        d += [(("Mass-low marginal" if row["observable"] == "mass_low" else "Tracks-low marginal"),
               float(row["difference"]))
              for row in marginal_rows
              if row["sample"] == kind and row["observable"] in ("mass_low", "multiplicity_low")]
        data[kind] = d
    limit = max(2.5, 1.15 * max(abs(v)*100 for rows in data.values() for _, v in rows))
    el = [
        _svg_text(48, 53, "Unfolded minus reference: joint and marginal", "title"),
        _svg_text(48, 80, "Differences in percentage points; zero is descriptive equality, not a test decision", "subtitle"),
    ]
    for i, kind in enumerate(("real", "pseudo")):
        left, top = 50 + 515*i, 125
        title = "Real − nominal generator" if kind == "real" else "Pseudodata − known truth"
        el.append(_svg_rect(left, top, 465, 470, "#f6f9fb", "#dbe4eb", 10))
        el.append(_svg_text(left + 20, top + 34, title, "panel"))
        zero = left + 292
        el.append(f'<line x1="{zero:.1f}" y1="{top+67}" x2="{zero:.1f}" y2="{top+406}" stroke="#758999" stroke-width="1.5"/>')
        for j, (label, delta) in enumerate(data[kind]):
            y = top + 89 + j*52
            length = min(abs(delta)*100/limit * 130, 130)
            color = "#007c86" if delta >= 0 else "#d76c46"
            el.append(_svg_text(left + 18, y + 6, label, "label"))
            el.append(_svg_rect(zero if delta >= 0 else zero-length,
                                y-13, length, 25, color, radius=3))
            el.append(_svg_text(zero + (length + 7 if delta >= 0 else -length - 7),
                                y + 6, f"{delta*100:+.3f} pp", "small",
                                "start" if delta >= 0 else "end"))
        el.append(_svg_text(left + 20, top + 447, "Teal: positive  |  Orange: negative", "small"))
    el.append(_svg_text(50, 650, "Four joint-cell differences sum to zero; the two marginals are derived from the same four cells.", "subtitle"))
    el.append(_svg_text(50, 702, "Reference differs by sample; no calibrated significance or generator-compatibility claim.", "small"))
    return _svg_document("Observed four-cell and marginal differences",
                         "Percentage-point differences of unfolded distributions from their appropriate references",
                         el, height=720)


def _figure_sources(source_rows: list[dict]) -> str:
    el = [
        _svg_text(48, 52, "What drives uncertainty in joint association?", "title"),
        _svg_text(48, 80, "Five largest conditional log-odds variance shares under one provisional 2D model", "subtitle"),
    ]
    for i, kind in enumerate(("real", "pseudo")):
        left, top = 50 + i*515, 123
        el.append(_svg_rect(left, top, 465, 420, "#f6f9fb", "#dbe4eb", 10))
        title = "Real vs paired nominal generator" if kind == "real" else "Pseudodata vs independent truth"
        el.append(_svg_text(left + 18, top + 31, title, "panel"))
        ranked = [r for r in source_rows if r["sample"] == kind and r["observable"] == "joint_log_odds"][:5]
        if len(ranked) != 5:
            raise ValueError("Missing five source contributions")
        for j, row in enumerate(ranked):
            y = top + 76 + j*64
            share = float(row["fraction_of_total_conditional_variance"])
            name = row["source"].replace("_", " ")
            el.append(_svg_text(left + 18, y, name, "label"))
            el.append(_svg_rect(left + 18, y + 9, 342, 18, "#dce6ec", radius=3))
            el.append(_svg_rect(left + 18, y + 9, 342*share, 18,
                                "#007c86" if kind == "real" else "#a86a3a", radius=3))
            el.append(_svg_text(left + 370, y + 24, f"{share:.1%}", "value"))
    el.append(_svg_text(50, 591, "Source fractions are modelled variance contributions, not causal probabilities.", "subtitle"))
    el.append(_svg_text(50, 623, "Includes paired finite-MC covariance for real reference and independent truth finite-MC for pseudodata.", "small"))
    el.append(_svg_text(50, 646, "DD/Sherpa correlations and training dependence are not experimentally validated; G15 NO-GO.", "small"))
    return _svg_document("Conditional source variance shares for joint log-odds",
                         "Source-level decomposition of the four-cell association under the provisional full/full model",
                         el, height=668)


def _figure_scenarios(scenario_rows: list[dict]) -> str:
    el = [
        _svg_text(48, 52, "Sensitivity to two-point source correlations", "title"),
        _svg_text(48, 80, "Conditional standard error of the joint log-odds difference; four prespecified scenarios", "subtitle"),
    ]
    vals = [float(row["joint_log_odds_conditional_standard_error"]) for row in scenario_rows]
    limit = max(vals) * 1.2
    for j, scenario in enumerate(MODEL_NAMES):
        y = 147 + j*126
        el.append(_svg_rect(50, y-35, 960, 111, "#f6f9fb", "#dbe4eb", 8))
        el.append(_svg_text(69, y-10, MODEL_LABELS[scenario], "panel"))
        for k, kind in enumerate(("real", "pseudo")):
            row = next(r for r in scenario_rows if r["sample"] == kind and r["scenario"] == scenario)
            value = float(row["joint_log_odds_conditional_standard_error"])
            bar_y = y + 5 + 31*k
            el.append(_svg_text(74, bar_y+15, "Real" if kind == "real" else "Pseudo", "label"))
            el.append(_svg_rect(170, bar_y, 650*value/limit, 22,
                                "#007c86" if kind == "real" else "#a86a3a", radius=3))
            el.append(_svg_text(180 + 650*value/limit, bar_y+16, f"{value:.5f}", "value"))
    el.append(_svg_text(50, 681, "These are assumption-conditional standard errors, not validated coverage intervals.", "subtitle"))
    el.append(_svg_text(50, 712, "Do not select the correlation model by its observed real-data agreement; G5/G12 provisional, G15 NO-GO.", "small"))
    return _svg_document("Joint-association standard-error sensitivity",
                         "Full and four-bin-independent DD and Sherpa assumptions; no formal significance",
                         el, height=738)


def _markdown_results(result: dict, joint_rows: list[dict],
                      marginal_rows: list[dict], scenario_rows: list[dict],
                      source_rows: list[dict]) -> str:
    spec = result["bin_spec"]
    lines = [
        "# KTI Methods and Results — frozen 2×2 joint shape",
        "",
        "**Status: source-backed descriptive secondary analysis, G15 NO-GO.** "
        "This is not a calibrated generator-compatibility test.",
        "",
        "## Data and prespecified method",
        "",
        "We re-used the ATLAS Collaboration's 2024 unbinned Z+jets OmniFold release "
        "(PRL 133, 261803; Zenodo DOI 10.5281/zenodo.11507450), via the "
        "checksum-verified, four-cell derived snapshots. The selection is "
        f"{spec['selection']}; the leading charged-jet mass threshold is "
        f"{spec['mass_star_GeV']:.12g} GeV and charged-track multiplicity "
        f"threshold is {spec['tracks_star']}. The thresholds were frozen from "
        "the nominal generator, not fitted to observed real-data differences. "
        "The cell order is LL, LH, HL, HH (mass category first).",
        "",
        "For cell weights h_i, we define p_i=h_i/sum_j h_j. The mass-low "
        "marginal is p_LL+p_LH, the multiplicity-low marginal is p_LL+p_HL, "
        "and joint association is log[(p_LL p_HH)/(p_LH p_HL)]. "
        "The association statistic cannot be reconstructed from the two marginals alone. "
        "Real unfolded data are compared descriptively to the nominal generator "
        "using shared-event paired finite-MC moments; unfolded pseudodata are "
        "compared to their independent known target truth.",
        "",
        "The conditional 4×4 normalized-shape covariance has a normalization "
        "null mode and three independent contrast directions. The source-wise "
        "prototype uses the official 1D helper's R−1 replica formula, "
        "a project-defined four-cell normalization and signed count-shift Jacobian, "
        "with four prespecified DD/Sherpa full-versus-independent-bin assumptions. "
        "The 2D nuisance correlations and learned-weight dependencies are not "
        "officially validated. The independent target-truth finite-MC term is "
        "included for pseudodata, whereas the paired finite-MC term replaces "
        "the measurement-only evaluation-MC term in the real comparison.",
        "",
        "## Table 1. Actual normalized four-cell fractions",
        "",
        "| Sample | Cell | Unfolded | Reference | Difference (percentage points) |",
        "|---|---|---:|---:|---:|",
    ]
    for row in joint_rows:
        lines.append(f"| {row['sample']} | {row['cell']} | "
                     f"{float(row['measurement_fraction']):.6f} | "
                     f"{float(row['reference_fraction']):.6f} | "
                     f"{float(row['delta_percentage_points']):+.4f} |")
    lines += [
        "",
        "The real reference is the nominal generator on shared events. "
        "The pseudodata reference is independent known target truth, not "
        "the pseudodata nominal generator. Four-cell differences sum to zero.",
        "",
        "## Table 2. Marginals and joint association",
        "",
        "| Sample | Observable | Unfolded | Reference | Difference | Conditional SE, full/full |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in marginal_rows:
        lines.append(f"| {row['sample']} | {row['observable']} | "
                     f"{float(row['measurement_value']):.6f} | "
                     f"{float(row['reference_value']):.6f} | "
                     f"{float(row['difference']):+.6f} | "
                     f"{float(row['conditional_standard_error_full_full']):.6f} |")
    lines += [
        "",
        "The SE column is **conditional on the provisional full/full DD/Sherpa "
        "source model**, with appropriate comparator finite-MC terms. It is "
        "not a calibrated experimental uncertainty or a license to quote significance.",
        "",
        "## Table 3. Correlation-model sensitivity (not inferential)",
        "",
        "| DD/Sherpa assumption | Real log-odds conditional SE | Pseudo log-odds conditional SE |",
        "|---|---:|---:|",
    ]
    for name in MODEL_NAMES:
        real = next(row for row in scenario_rows if row["sample"] == "real" and row["scenario"] == name)
        pseudo = next(row for row in scenario_rows if row["sample"] == "pseudo" and row["scenario"] == name)
        lines.append(f"| {MODEL_LABELS[name]} | "
                     f"{float(real['joint_log_odds_conditional_standard_error']):.6f} | "
                     f"{float(pseudo['joint_log_odds_conditional_standard_error']):.6f} |")
    lines += [
        "",
        "The scenario-specific uncalibrated quadratic diagnostics and complete "
        "4×4 covariances are retained in the machine-readable tables. They "
        "are **not** converted into a real-data p-value or a generator verdict.",
        "",
        "## Table 4. Largest conditional joint-association variance contributors",
        "",
        "| Sample | Source | Share of conditional log-odds variance |",
        "|---|---|---:|",
    ]
    for kind in ("real", "pseudo"):
        for row in [r for r in source_rows if r["sample"] == kind
                    and r["observable"] == "joint_log_odds"][:5]:
            lines.append(f"| {kind} | {row['source']} | "
                         f"{float(row['fraction_of_total_conditional_variance']):.2%} |")
    lines += [
        "",
        "The source shares sum to one within each observable, using the "
        "appropriate comparator-aware gradient and finite-MC covariance. "
        "They describe modeled variance, not probabilities of physical causes.",
        "",
        "## Pseudodata validation and limitations",
        "",
        "One released unfolded pseudodata sample was compared with its "
        "independent known target. This is a **single known-target closure**, "
        "not an ensemble of independently retrained pseudo-measurements. "
        "The public 1D example selects 15 project-equivalent covariance "
        "families, whereas the project's 2D prototype contains 29 "
        "(25 systematic-labelled and four stochastic); this is an "
        "inclusion-scope difference, not a numerical equality target. "
        "The correspondence of all 25 project systematic labels to "
        "the 25 published components is not proven one-to-one.",
        "",
        "The 2D DD and Sherpa hidden-variable nuisance correlations, "
        "the full neural-network training dependence and experimental "
        "frequentist coverage remain unverified. Hence **G5 PROVISIONAL, "
        "G8 UNVERIFIED, G12 UNVERIFIED, G15 NO-GO**. "
        "This work supports descriptive joint-versus-marginal comparisons, "
        "not a calibrated generator-compatibility claim.",
        "",
        "## Figure captions",
        "",
        "**Figure 1:** Four actual normalized mass–multiplicity joint shapes: "
        "real unfolded, nominal generator, unfolded pseudodata, and independent target truth.",
        "",
        "**Figure 2:** Signed differences of four joint-cell fractions and "
        "two derived marginals, in percentage points.",
        "",
        "**Figure 3:** Five largest model-conditional joint log-odds variance "
        "contributors for each comparison.",
        "",
        "**Figure 4:** Conditional log-odds standard-error sensitivity under "
        "the four prespecified DD/Sherpa source-correlation models.",
        "",
        "## Primary references and reproducibility",
        "",
        "- ATLAS Collaboration, *Physical Review Letters* 133, 261803 (2024), "
        "https://doi.org/10.1103/PhysRevLett.133.261803",
        "- Official ATLAS release, https://doi.org/10.5281/zenodo.11507450",
        "- Official supplemental User Guide, Section 2, recommendation 5; "
        "CERN 1D multifold_util.py source audit documented in the repository.",
        "- Derived snapshot provenance and source-run IDs: "
        "data/derived/phase7-v1/provenance.json and "
        "data/derived/phase7-v2/provenance.json.",
        "- Rebuild: python -m src.phase7_kti_bundle "
        "--v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 "
        "--out outputs/four-cell-v1",
        "",
    ]
    return "\n".join(lines)


def generate(v1: Path, v2: Path, out: Path) -> dict:
    """Fail closed on checksum drift, model drift, non-normalized shapes or GO."""
    v1, v2, out = Path(v1), Path(v2), Path(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError("Evidence bundle output must be an empty directory")
    # Reconstructs and checks both v1/v2 snapshots, R-1 replica covariances,
    # shared-event cross moments, known-target covariance and all four models.
    joint, model_components = analyze_joint(v1, v2, return_components=True)
    if joint["G15"] != "NO_GO" or tuple(joint["scenario_order"]) != MODEL_NAMES:
        raise ValueError("Scientific gate or pre-specified scenario order drift")
    spec_real = json.loads((v1/"real/bin_spec_covariance.json").read_text(encoding="utf-8"))
    spec_pseudo = json.loads((v1/"pseudo/pseudo_bin_spec.json").read_text(encoding="utf-8"))
    if (spec_real["mass_star"] != spec_pseudo["mass_star"] or
        spec_real["tracks_star"] != spec_pseudo["tracks_star"] or
        spec_real["selection"] != spec_pseudo["selection"] or
        spec_real["threshold_source"] != "nominal_generator_only"):
        raise ValueError("Frozen real/pseudodata bin definition drift")
    spec = {"mass_star_GeV": spec_real["mass_star"],
            "tracks_star": spec_real["tracks_star"],
            "selection": spec_real["selection"],
            "threshold_source": "nominal_generator_only"}
    stored = json.loads((v2/"moments.json").read_text(encoding="utf-8"))
    v1_proof = json.loads((v1/"provenance.json").read_text(encoding="utf-8"))
    v2_proof = json.loads((v2/"provenance.json").read_text(encoding="utf-8"))

    joint_rows, marginal_rows, scenario_rows = [], [], []
    covariance_rows, source_rows = [], []
    samples, source_accounting = {}, {}
    for kind in ("real", "pseudo"):
        base = v1/kind
        csv_path = base/("real_2x2_cells.csv" if kind == "real" else "pseudo_closure_cells.csv")
        meas_col = "unfolded_fraction" if kind == "real" else "pseudo_unfolded_fraction"
        ref_col = "generator_fraction" if kind == "real" else "independent_target_truth_fraction"
        p, q = load_fractions(csv_path, meas_col), load_fractions(csv_path, ref_col)
        rows = _read_csv(csv_path)
        if [r["cell"] for r in rows] != list(CELLS):
            raise ValueError("Frozen four-cell order drift")
        meas_label, ref_label, ref_kind = REFERENCE_LABELS[kind]
        samples[kind] = {"measurement": p.tolist(), "reference": q.tolist(),
                         "measurement_label": meas_label, "reference_label": ref_label,
                         "reference_kind": ref_kind}
        for i, cell in enumerate(CELLS):
            delta = float(p[i]-q[i])
            joint_rows.append({
                "sample": kind, "cell": cell,
                "measurement_label": meas_label, "reference_label": ref_label,
                "measurement_fraction": float(p[i]),
                "reference_fraction": float(q[i]),
                "delta_fraction": delta, "delta_percentage_points": delta*100,
            })
        manifest_path = base/("source_manifest.csv" if kind == "real" else "pseudo_source_manifest.csv")
        manifest = read_manifest(manifest_path)
        archive_path = base/("source_covariances.npz" if kind == "real" else "pseudo_source_covariances.npz")
        with np.load(archive_path, allow_pickle=False) as archive:
            source_audit = audit_components({k: archive[k] for k in archive.files}, manifest)
        counts = source_audit["source_counts"]
        if (counts["all_project_components"] != 29 or
            counts["paper_systematic_count_arithmetic"] != 25 or
            counts["stochastic_components"] != 4 or
            counts["pseudo_notebook_1d_included_components"] != 15 or
            len(STOCHASTIC_SOURCES) != 4):
            raise ValueError("Frozen source taxonomy drift")
        source_accounting[kind] = {
            "total_project_components": 29, "systematic_labelled": 25,
            "stochastic": 4, "notebook_1d_selected": 15,
            "notebook_1d_omitted": 14,
            "notebook_1d_trace_share": source_audit["pseudo_notebook_1d_trace_share"],
            "one_to_one_paper_mapping_verified": False,
            "official_2d_model_verified": False,
            "replica_counts": joint["samples"][kind]["replica_counts"],
        }
        model_results = joint["samples"][kind]["models"]
        if tuple(m["scenario"] for m in model_results) != MODEL_NAMES:
            raise ValueError("Model scenario order changed")
        for model in model_results:
            scenario = model["scenario"]
            components = model_components[kind][scenario]
            c = validate_covariance(sum(components.values()))
            if np.linalg.matrix_rank(c, tol=1e-12) != 3 or model["contrast_rank"] != 3:
                raise ValueError("Shape covariance must have three independent contrasts")
            scenario_rows.append({
                "sample": kind, "scenario": scenario,
                "uncalibrated_quadratic_not_a_pvalue": model["uncalibrated_quadratic_not_a_pvalue"],
                "covariance_trace": model["covariance_trace"],
                "contrast_rank": model["contrast_rank"],
                "normalization_null_residual": model["normalization_null_residual"],
                "mass_low_conditional_standard_error": model["observables"]["mass_low"]["conditional_standard_error"],
                "multiplicity_low_conditional_standard_error": model["observables"]["multiplicity_low"]["conditional_standard_error"],
                "joint_log_odds_conditional_standard_error": model["observables"]["joint_log_odds"]["conditional_standard_error"],
            })
            for i, ri in enumerate(CELLS):
                for j, cj in enumerate(CELLS):
                    covariance_rows.append({
                        "sample": kind, "scenario": scenario,
                        "row_cell": ri, "col_cell": cj,
                        "shape_covariance": float(c[i, j]),
                        "covariance_scope": "conditional_provisional_p_minus_reference",
                    })
        values_p, _ = _observables(p)
        values_q, _ = _observables(q)
        for obs in OBSERVABLES:
            ses = [float(m["observables"][obs]["conditional_standard_error"])
                   for m in model_results]
            marginal_rows.append({
                "sample": kind, "observable": obs,
                "measurement_value": values_p[obs],
                "reference_value": values_q[obs],
                "difference": values_p[obs]-values_q[obs],
                "conditional_standard_error_full_full": ses[0],
                "conditional_standard_error_min": min(ses),
                "conditional_standard_error_max": max(ses),
                "reference_kind": ref_kind,
                "uncertainty_scope": "conditional_provisional_not_experimental_coverage",
            })
        paired = _paired_inputs(stored["samples"]["real"]["nominal"]) if kind == "real" else None
        source_rows.extend(_source_rows(kind, p, q,
                           model_components[kind][MODEL_NAMES[0]], model_results[0],
                           manifest, paired))

    # Fail closed on expected source-run identity and historical primary inputs.
    if (v1_proof["sources"]["real"]["run_id"] != 42324639484 or
        v1_proof["sources"]["pseudo"]["run_id"] != 42327464929 or
        v2_proof["scientific_gate"] != "G15_NO_GO"):
        raise ValueError("Original source run provenance drift")
    checks = {
        "checksum_verified_v1_and_v2": True,
        "generator_defined_fixed_2x2_thresholds": True,
        "four_positive_cells_per_shape": True,
        "normalized_four_cell_sum_and_zero_residual_sum": True,
        "twenty_nine_systematic_and_stochastic_components_audited": True,
        "sample_replica_counts_and_R_minus_1_reconciled": True,
        "real_reference_paired_finite_MC_used": True,
        "pseudodata_independent_known_truth_used": True,
        "four_prespecified_source_correlation_models": True,
        "source_variances_sum_to_comparator_aware_total": True,
        "all_four_by_four_covariances_have_rank_three_and_null_mode": True,
        "no_real_data_significance_permission": True,
    }
    result = {
        "status": "CHECKSUM_VERIFIED_DESCRIPTIVE_FOUR_CELL_V1_BUNDLE",
        "G5": "PROVISIONAL", "G8": "UNVERIFIED", "G12": "UNVERIFIED",
        "G15": "NO_GO", "inference_permission": "NO_GO",
        "bin_spec": spec, "scenario_order": list(MODEL_NAMES),
        "source_accounting": source_accounting, "samples": samples,
        "provenance": {
            "ATLAS_paper": "https://doi.org/10.1103/PhysRevLett.133.261803",
            "Zenodo_release": "https://doi.org/10.5281/zenodo.11507450",
            "original_archive_md5": v1_proof["archive_md5"],
            "real_source_run": v1_proof["sources"]["real"]["run_id"],
            "pseudo_source_run": v1_proof["sources"]["pseudo"]["run_id"],
            "v2_moments_sha256": v2_proof["moments_sha256"],
            "official_1d_helper_sha256": joint["primary_helper_file_sha256"],
        },
        "checks": checks,
        "limitations": [
            "Not an ATLAS-approved two-dimensional covariance prescription",
            "DD and Sherpa nuisance correlations are pre-specified sensitivity assumptions",
            "Other source families and learned-weight training dependencies may be correlated",
            "A single known-target pseudodata closure is not repeated experimental coverage",
            "No real-data generator-compatibility inference is authorized",
        ],
    }
    if not all(checks.values()):
        raise ValueError("One or more KTI evidence quality gates failed")
    out.mkdir(parents=True, exist_ok=True)
    _write_csv(out/"tables/joint_cells.csv", joint_rows)
    _write_csv(out/"tables/marginal_association.csv", marginal_rows)
    _write_csv(out/"tables/scenario_sensitivity.csv", scenario_rows)
    _write_csv(out/"tables/source_variance.csv", source_rows)
    _write_csv(out/"tables/covariance_matrix.csv", covariance_rows)
    _write_text(out/"figures/fig1_joint_shapes.svg", _figure_joint(samples))
    _write_text(out/"figures/fig2_cell_and_marginal_differences.svg",
                _figure_differences(joint_rows, marginal_rows))
    _write_text(out/"figures/fig3_joint_source_variance.svg", _figure_sources(source_rows))
    _write_text(out/"figures/fig4_correlation_sensitivity.svg", _figure_scenarios(scenario_rows))
    _write_text(out/"MANUSCRIPT_RESULTS.md",
                _markdown_results(result, joint_rows, marginal_rows, scenario_rows, source_rows))
    _write_text(out/"checks.json", json.dumps(checks, indent=2, sort_keys=True))
    _write_text(out/"results.json", json.dumps(result, indent=2, sort_keys=True))
    _write_text(out/"README.md", "\n".join([
        "# ATLAS 2024 OmniFold KTI — four-cell descriptive release (v1)",
        "",
        "Actual, checksum-verified normalized 2×2 results from frozen ATLAS 2024",
        "derived moments. This is a descriptive secondary analysis, not an",
        "ATLAS-approved 2D covariance model or a calibrated compatibility test.",
        "",
        "## Reproduce without downloading the original multi-GB ATLAS archive",
        "",
        "    python -m pytest -q tests/test_phase7_kti_bundle.py",
        "    python -m src.phase7_kti_bundle --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/four-cell-v1",
        "",
        "Inputs: checksum-pinned data/derived/phase7-v1 and phase7-v2.",
        "Output: 5 machine-readable CSV tables, 4 SVG vector figures,",
        "MANUSCRIPT_RESULTS.md, checks.json, results.json and manifest.json.",
        "All output hashes are recorded in manifest.json for exact rebuild comparison.",
        "",
        "See MANUSCRIPT_RESULTS.md for all numerical values, captions and limitations.",
        "G5 PROVISIONAL; G8/G12 UNVERIFIED; G15 NO-GO. No real-data p-value.",
        "",
    ]))
    file_hashes = {}
    for path in sorted(p for p in out.rglob("*") if p.is_file()):
        file_hashes[path.relative_to(out).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    _write_text(out/"manifest.json", json.dumps({
        "status": "CHECKSUM_PINNED_DESCRIPTIVE_BUNDLE",
        "source_runs": {"real": 42324639484, "pseudo": 42327464929},
        "v2_moments_sha256": v2_proof["moments_sha256"],
        "files": file_hashes,
        "G15": "NO_GO",
    }, indent=2, sort_keys=True))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1", type=Path, default=Path("data/derived/phase7-v1"))
    parser.add_argument("--v2", type=Path, default=Path("data/derived/phase7-v2"))
    parser.add_argument("--out", type=Path, default=Path("outputs/four-cell-v1"))
    args = parser.parse_args()
    report = generate(args.v1, args.v2, args.out)
    print(json.dumps({
        "status": report["status"], "G15": report["G15"],
        "source_runs": [report["provenance"]["real_source_run"],
                        report["provenance"]["pseudo_source_run"]],
        "figures": 4, "tables": 5, "checks_passed": len(report["checks"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
