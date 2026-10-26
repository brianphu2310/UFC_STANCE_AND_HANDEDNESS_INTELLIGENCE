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
    title_slot = st.empty()
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
    fig.update_layout(xaxis=dict(title=metric_label, gridcolor="#222228"))
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
        title_slot.markdown("")
        st.markdown('<div class="empty">Each group needs at least a few fighters before it can be compared. '
                    'Lower the minimum fights or choose All fighters.</div>', unsafe_allow_html=True)
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
    with title_slot:
        ui.page_header("Does stance decide fights?",
                       f"<b>{len(lab)}</b> fighters with at least {min_f} pro fights, {len(results)} comparisons on "
                       f"{escape(metric_label.lower())}. "
                       + ("<b>None survives the Holm correction.</b>" if not sig else
                          f"<b>{len(sig)} survive{'s' if len(sig) == 1 else ''} the Holm correction.</b>"),
                       kicker="Statistical analysis")
    verdict.markdown(f'<div class="callout" style="margin-bottom:18px">{verdict_html}</div>',
                     unsafe_allow_html=True)

    fig = go.Figure()
    ys = [f"{r.label_a} vs {r.label_b}" for r in results]
    fig.add_vline(x=0, line=dict(color=ui.ACCENT, width=1, dash="dot"))
    fig.add_scatter(
        x=[r.diff for r in results], y=ys, mode="markers",
        marker=dict(size=11, color=[ui.ACCENT if p < .05 else ui.INK for p in holm], line=dict(color=ui.SURFACE, width=2)),
        error_x=dict(type="data", symmetric=False, color=ui.INK_MUTED, thickness=2, width=6,
                     array=[r.ci_high - r.diff for r in results],
                     arrayminus=[r.diff - r.ci_low for r in results]),
        customdata=[[r.ci_low, r.ci_high, r.n_a, r.n_b, r.welch_p] for r in results],
        hovertemplate=("<b>%{y}</b><br>gap %{x:+.2f}<br>95% CI %{customdata[0]:+.2f} to "
                       "%{customdata[1]:+.2f}<br>n = %{customdata[2]} vs %{customdata[3]}"
                       "<br>Welch p = %{customdata[4]:.3f}<extra></extra>"))
    fig.update_layout(xaxis=dict(title=f"difference in mean {metric_label.lower()}"),
                      yaxis=dict(autorange="reversed"), showlegend=False)
    ui.section("Each comparison, with its uncertainty", "Dot: difference in means (group A minus group B). "
               "Line: 95% bootstrap interval. An interval that crosses the dotted zero line is consistent with no difference.")
    ui.chart(ui.layout(fig, height=120 + 52 * len(results), title="Gap with 95% bootstrap interval"))
    ui.section("Test results", "Welch's t-test (unequal variances), Mann-Whitney U as a rank check, Holm-adjusted p "
               "across the family of tests, Cohen's d for size, and the group size needed for 80% power.")

    st.dataframe(pd.DataFrame([{
        "Comparison": f"{r.label_a} vs {r.label_b}", "n": f"{r.n_a} vs {r.n_b}",
        "Means": f"{r.mean_a:.2f} vs {r.mean_b:.2f}", "Gap": f"{r.diff:+.2f}",
        "95% CI": f"{r.ci_low:+.2f} to {r.ci_high:+.2f}", "Welch p": ui.fmt_p(r.welch_p),
        "Holm-adjusted p": ui.fmt_p(hp),
        "Mann-Whitney p": ui.fmt_p(r.mwu_p),
        "Cohen's d": f"{r.d:+.2f} ({core.effect_label(r.d)})",
        "n/group for 80% power": f"{r.power_n_per_group:,}" if r.power_n_per_group < 10**5 else "—",
    } for r, hp in zip(results, holm)]), hide_index=True, width="stretch")

    try:
        an = core.anova(lab, col, metric)
        st.caption(f"All {dim.lower()} groups at once: one-way ANOVA p = {ui.fmt_p(an['p'])}, "
                   f"Kruskal–Wallis p = {ui.fmt_p(an['kruskal_p'])}. ≈ marks comparisons that use the estimated "
                   "dominant foot.")
    except ValueError:
        pass

    best = max(results, key=lambda r: abs(r.d))
    ui.section("Interpretation", "What these results support, and what they do not.")
    st.markdown(f"""<div class="interp">
  <div><h3>Supported</h3><ul>
    <li>In this sample, {escape(head.label_a.lower())}s and {escape(head.label_b.lower())}s differ by
      {head.diff:+.2f} on {escape(metric_label.lower())} (95% CI {head.ci_low:+.2f} to {head.ci_high:+.2f}).</li>
    <li>The largest effect is {escape(best.label_a)} vs {escape(best.label_b)}, d = {best.d:+.2f}
      ({core.effect_label(best.d)}), on {best.n_a} vs {best.n_b} fighters.</li>
    <li>{'No comparison clears the Holm-adjusted 5% threshold.' if not sig else f'{len(sig)} comparison(s) clear the Holm-adjusted 5% threshold.'}</li>
  </ul></div>
  <div><h3>Not supported</h3><ul>
    <li><b>Causation.</b> Fighters choose or are taught a stance; any gap could come from who adopts it, not the stance itself.</li>
    <li><b>Practical importance from a p-value.</b> A small p with a tiny d would still be a small edge; read the interval and d.</li>
    <li><b>"No effect".</b> A non-significant result with wide intervals means the data cannot tell, not that the effect is zero.
      Detecting d = {head.d:+.2f} at 80% power needs about {head.power_n_per_group if head.power_n_per_group < 10**5 else '100,000+'} fighters per group.</li>
    <li><b>All fighters.</b> These are {len(lab)} well-known, mostly winning fighters, so win rates are compressed.</li>
  </ul></div>
</div>
<style>
  .interp {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .interp > div {{ background: {ui.SURFACE}; border: 1px solid {ui.BORDER}; border-radius: 4px; padding: 18px 22px; }}
  .interp > div:first-child {{ border-top: 2px solid {ui.INK}; }} .interp > div:last-child {{ border-top: 2px solid {ui.ACCENT}; }}
  .interp h3 {{ font: 700 22px/1 {ui.DISPLAY}; text-transform: uppercase; margin: 0 0 8px; padding: 0; }}
  .interp li {{ margin: 6px 0; font-size: 14px; color: {ui.INK_2}; }}
  @media (max-width: 800px) {{ .interp {{ grid-template-columns: 1fr; }} }}
</style>""", unsafe_allow_html=True)
