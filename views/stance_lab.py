"""Stance lab: does stance, hand or foot change results? Real tests, honest uncertainty."""
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ufc_core as core
import ui

METRICS = {
    "Career win rate (%)": "win_rate",
    "Striking accuracy (%)": "str_acc",
    "Strikes absorbed / min": "sapm",
    "Strikes landed / min": "slpm",
    "Takedowns / 15 min": "td_avg",
    "Popularity index": "popularity_index",
}


def render(df: pd.DataFrame):
    ui.page_header("Does stance decide fights?",
                   "Test any outcome by stance, hand or foot, with intervals and corrections that "
                   "show how sure the answer really is.")
    f1, f2, f3 = st.columns([1.4, 1, 1])
    metric_label = f1.selectbox("Outcome", list(METRICS))
    metric = METRICS[metric_label]
    gender = f2.segmented_control("Fighters", ["All", "Men", "Women"], default="All",
                                  key="lab_g") or "All"
    min_f = f3.slider("Minimum pro fights", 10, 40, 10)
    lab = df[df["total_fights"] >= min_f]
    if gender != "All":
        lab = lab[lab["gender"] == gender]
    lab = lab[lab[metric].notna()]
    st.caption(f"{len(lab)} fighters in this view.")
    verdict = st.empty()          # filled once the tests have run

    dim = st.segmented_control("Compare groups by", list(core.GROUP_DIMS),
                               default="Stance × hand", key="lab_dim") or "Stance × hand"
    col, order = core.present_order(lab, dim)
    colors = ui.colors_for(dim)
    fig = go.Figure()
    for g in order:
        s = lab[lab[col] == g]
        fig.add_box(x=s[metric], y=[f"{g}  (n={len(s)})"] * len(s), orientation="h",
                    boxpoints="all", jitter=0.45, pointpos=0, fillcolor="rgba(0,0,0,0)",
                    marker=dict(color=colors[g], size=7, opacity=0.85,
                                line=dict(color=ui.SURFACE, width=1)),
                    line=dict(color=colors[g], width=1.5), text=s["fighter"],
                    hovertemplate="<b>%{text}</b><br>%{x:.1f}<extra></extra>")
    fig.update_layout(showlegend=False, xaxis=dict(title=metric_label))
    ui.chart(ui.layout(fig, height=110 + 48 * len(order), title=f"{metric_label} by {dim.lower()}"))

    m = dict(
        sp=lab["stance"] == "Southpaw", orth=lab["stance"] == "Orthodox",
        sw=lab["stance"] == "Switch", single=lab["stance"] != "Switch",
        rs=(lab["stance"] == "Southpaw") & (lab["hand"] == "Right"),
        ro=(lab["stance"] == "Orthodox") & (lab["hand"] == "Right"),
        left=lab["hand"] == "Left", right=lab["hand"] == "Right",
        lf=lab["foot"] == "Left", rf=lab["foot"] == "Right",
    )
    specs = [("sp", "orth", "Southpaw", "Orthodox"),
             ("rs", "ro", "Right-handed southpaw", "Orthodox right-hander"),
             ("sw", "single", "Switch-stance", "Single-stance"),
             ("left", "right", "Left-handed", "Right-handed"),
             ("lf", "rf", "Left-footed ≈", "Right-footed ≈")]
    results = []
    for a, b, la, lb in specs:
        try:
            results.append(core.compare_groups(lab, m[a], m[b], la, lb, metric))
        except ValueError:
            pass
    if not results:
        st.info("Not enough fighters to compare groups.")
        return

    holm = core.holm_adjust([r.welch_p for r in results])
    sig = [r for r, p in zip(results, holm) if p < 0.05]
    head = results[1] if len(results) > 1 else results[0]
    if sig:
        verdict_html = ("<b>Verdict:</b> after correcting for running "
                        f"{len(results)} comparisons at once, "
                        + ", ".join(escape(f"{r.label_a} vs {r.label_b}") for r in sig)
                        + f" still differ{'s' if len(sig) == 1 else ''} on {escape(metric_label.lower())}.")
    else:
        verdict_html = (f"<b>Verdict: no stance, hand or foot group differs reliably on "
                        f"{escape(metric_label.lower())}.</b> Every 95% interval below crosses zero "
                        f"or fails the Holm correction for {len(results)} simultaneous tests. "
                        "Right-handed southpaws are "
                        f"{head.diff:+.1f} against orthodox right-handers, a gap too small to separate from "
                        "chance with groups this size.")
    verdict.markdown(f'<div class="callout" style="border-left-color:{ui.RULE}">{verdict_html}</div>',
                     unsafe_allow_html=True)

    fig = go.Figure()
    ys = [f"{r.label_a} vs {r.label_b}" for r in results]
    fig.add_vline(x=0, line=dict(color=ui.INK_MUTED, width=1, dash="dot"))
    fig.add_scatter(
        x=[r.diff for r in results], y=ys, mode="markers",
        marker=dict(size=11, color=ui.ACCENT, line=dict(color=ui.SURFACE, width=2)),
        error_x=dict(type="data", symmetric=False, color=ui.ACCENT, thickness=2, width=6,
                     array=[r.ci_high - r.diff for r in results],
                     arrayminus=[r.diff - r.ci_low for r in results]),
        customdata=[[r.ci_low, r.ci_high, r.n_a, r.n_b, r.welch_p] for r in results],
        hovertemplate=("<b>%{y}</b><br>gap %{x:+.2f}<br>95% CI %{customdata[0]:+.2f} to "
                       "%{customdata[1]:+.2f}<br>n = %{customdata[2]} vs %{customdata[3]}"
                       "<br>Welch p = %{customdata[4]:.3f}<extra></extra>"))
    fig.update_layout(xaxis=dict(title=f"difference in mean {metric_label.lower()}"),
                      yaxis=dict(autorange="reversed"), showlegend=False)
    ui.chart(ui.layout(fig, height=120 + 52 * len(results), title="Gap with 95% bootstrap interval"))

    st.dataframe(pd.DataFrame([{
        "Comparison": f"{r.label_a} vs {r.label_b}", "n": f"{r.n_a} vs {r.n_b}",
        "Means": f"{r.mean_a:.2f} vs {r.mean_b:.2f}", "Gap": f"{r.diff:+.2f}",
        "95% CI": f"{r.ci_low:+.2f} to {r.ci_high:+.2f}", "Welch p": ui.fmt_p(r.welch_p),
        "Holm-adjusted p": ui.fmt_p(hp),
        "Mann-Whitney p": ui.fmt_p(r.mwu_p),
        "Cohen's d": f"{r.d:+.2f} ({core.effect_label(r.d)})",
        "n/group for 80% power": f"{r.power_n_per_group:,}" if r.power_n_per_group < 10**5 else "—",
    } for r, hp in zip(results, holm)]), hide_index=True, width="stretch")

    lines = [f"<b>Right-handed southpaws vs orthodox right-handers:</b> {head.mean_a:.2f} vs "
             f"{head.mean_b:.2f} ({metric_label.lower()}), Welch p = {ui.fmt_p(head.welch_p)}, "
             f"effect {core.effect_label(head.d)} (d = {head.d:+.2f}), "
             f"n = {head.n_a} vs {head.n_b}."]
    lines.append("<b>How to read this:</b> the Holm-adjusted p keeps the chance of any false "
                 f"alarm across all {len(results)} tests at 5%. The last column is how many fighters "
                 "per group a study would need to detect the observed gap 80% of the time.")
    ui.callout("<br>".join(lines))
    try:
        an = core.anova(lab, col, metric)
        st.caption(f"All {dim.lower()} groups together — ANOVA p = {ui.fmt_p(an['p'])}, "
                   f"Kruskal–Wallis p = {ui.fmt_p(an['kruskal_p'])}. "
                   "≈ marks comparisons that use the estimated dominant foot.")
    except ValueError:
        pass
