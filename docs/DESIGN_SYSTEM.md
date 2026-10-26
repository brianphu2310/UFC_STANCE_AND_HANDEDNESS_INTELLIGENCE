# Stance Intelligence design system

A premium fight-intelligence product: a charcoal ground, panels one step lighter with a 1px border
and 4px corners, condensed editorial headlines, and one restrained accent. Red does one job at a time:
it marks the active page, the primary action, and in every chart the southpaw (the side the research
asks about). Orthodox is drawn in steel and switch in brass. No gradients, glows or resting shadows.
The signature shape is the octagon: the logo mark, the landing page's line motif and the 3D mat.

All tokens live in `ui.py`; Streamlit's own widgets take theirs from `.streamlit/config.toml`, and the
two three.js components mirror them. Views import tokens as `ui.ACCENT`, `ui.INK_2` and so on.

## Tokens

### Colour

| Token | Hex | Use | Contrast |
|---|---|---|---|
| `BG` | `#0B0B0D` | Ground: bar, page, gutters | — |
| `SURFACE` | `#131316` | Panels, charts, tables | — |
| `SURFACE_2` | `#1A1A1F` | Inputs, nested cards, popovers | — |
| `RAISED` | `#24242A` | Selected segment, bar tracks | — |
| `BORDER` | `#26262C` | 1px panel edges and row rules | decorative |
| `CONTROL` | `#3A3A42` | Control outlines | — |
| `INK` | `#F5F5F5` | Headlines, values | 17.6:1 on SURFACE |
| `INK_2` | `#A9A9B1` | Body and secondary text | 8.2:1 on SURFACE |
| `INK_MUTED` | `#86868F` | Labels, captions, axis ticks | 5.3:1 on SURFACE |
| `ACCENT` | `#E5383B` | Fight red: active page, section labels, southpaw in charts | 4.9:1 on BG |
| `ACCENT_FILL` | `#C81E2A` | The primary button | white text 5.9:1 |
| `STEEL` | `#C9CCD3` | Orthodox in charts; fighter B in a matchup | 12:1 on SURFACE |
| `BRASS` | `#C9A227` | Switch in charts; the estimated / dominant side | 7.6:1 on SURFACE |

Data palette, in a fixed order per dimension (Orthodox, Southpaw, Switch / Right, Left / ...):
`#C9CCD3`, `#E5383B`, `#C9A227`, then neutrals `#6E6E78`, `#4A4A52`, `#34343B`. Magnitudes (the
globe, the hand and foot discs) use a grey ramp, never a hue, so red keeps one meaning.

Helpers:
- `ui.text_color(c)`: use whenever a series colour is drawn as text (returns a text-safe variant where one exists).
- `ui.on_color(c)`: picks dark or white text for a label sitting on a fill of colour `c`.

### Type

| Role | Face | Size / weight |
|---|---|---|
| Landing headline | Big Shoulders Display | 56–100px / 800, capitals, leading 0.9 |
| Page title (`h1`) | Big Shoulders Display | 44px / 800, capitals (32px on a phone) |
| Section and card titles | Big Shoulders Display | 19–24px / 700, capitals |
| Key figures | Big Shoulders Display | 24–56px / 800, tabular figures |
| Section label above a title | Inter | 12px / 600, tracked capitals, red |
| Body | Inter | 14–16px / 400, line-height 1.55–1.6 |
| Labels, captions, axis ticks | Inter | 12–13px / 500 |

Both fonts are self-hosted in `static/fonts` (OFL) and inlined as data URIs by `ui._font_faces()`, so
they load under Community Cloud's path prefix; the app makes no font requests to third parties.

Writing rules: sentence case everywhere, no all-caps labels, no middle-dot meta strings, and
numbers come with their unit ("4 cm short", not "−4").

### Shape, spacing, motion

- Radius: 4px on panels, 2–3px on buttons, inputs and segments. No pills except status tags.
- Spacing steps: 4, 8, 12, 16, 22, 30px. Sections open with 30px above them and a hairline.
- Motion: page blocks rise 10px in on arrival (staggered 40ms), tab panels fade in, the tab indicator
  glides, chart updates animate over 300ms, the landing octagon draws itself once, and a red bar sweeps
  under the header while a request runs. Hover lightens a panel's border; buttons press to 98%.
  Under `prefers-reduced-motion` every animation and transition is switched off.

## Iconography

`static/mark.svg` / `mark.png` is an octagon split down the middle into steel and red. It
is the favicon and sits beside the wordmark in the top bar. It is an original mark and is
deliberately not the UFC logo: the app uses public fight data, but it is not affiliated with UFC.

The app uses no other icons. Words label every control.

## Components

| Component | Where | Notes |
|---|---|---|
| `ui.page_header(title, finding, kicker)` | Top of every page | Red section label, the `h1`, and the page's finding in one sentence built from the data, over a 1px rule |
| `ui.section(title, sub, estimated)` | Section breaks | Heading role level 2; `estimated` adds the dashed gold badge |
| Panel (`st.container(key="oct_…")`) | Grouped blocks | `SURFACE` with a 1px `BORDER`, 4px corners; charts inside drop their own frame |
| `.card` | Fighter tapes, plans, gear | Title, meta line, `.kv` stat grid, `.pill` tags |
| `ui.callout(html)` | Verdicts and explanations | Red left rule |
| `.simlist / .simrow` | "Fights most like" | Name, meta, bar, score |
| `ui.chart(fig, key, alt)` | Every Plotly chart | Writes a screen-reader description (auto-built from title and series, or `alt`) |
| `globe3d` | Overview | Rotatable globe with country name cards |
| `body3d` | Explorer, Build a fighter, Spar vs Brian | Face-off, Height and Reach views; jab, cross and kick measured from real range |

### body3d controls

| Control | Type | States | Keyboard |
|---|---|---|---|
| Face-off / Height / Reach | Segmented, `aria-pressed` | Selected = raised fill, ink text | Tab, Enter or Space |
| Spar / Jab / Cross / Kick | Segmented, Face-off only | Same | Same |
| Pause / Play | Toggle | Label and `aria-pressed` follow the state | Same |
| Rotate | Toggle | `aria-pressed` | Same |
| Reset | Button | — | Same |
| 3D canvas | `role="img"`, focusable | Accessible name follows the on-screen headline | Arrow keys turn, + and − zoom |

Stage: a full-size Octagon (30 ft across) with a white canvas, red boundary and centre markings, a
metallic chain-link fence with red neon strips, red and blue corner posts, red rim lights and fog.
Fighters have graphite skin; the Neon button switches them to a glowing red.

Body: a skinned human mesh (MakeHuman CC0 base mesh shaped into an athletic male, about 13,000
vertices, 36 bones), built by `scripts/build_body_model.py`. The joint solver computes hips, knees,
ankles, shoulders, elbows and wrists every frame and each bone is aimed at its joint, so the model
follows height, reach (arm bones stretch), weight (heavy and lean morph targets) and stance.

Fight kit in the model, all built from the skin surface so it moves with the body: fight shorts in
the corner colour with a black waistband; 4oz MMA gloves in glossy black leather, modelled on a
standard fight glove (no brand marks): a padded knuckle section about 1.2 cm thick at the wrist rising
to 2.8 cm over the knuckles, split into finger tubes by grooves, a stitched seam across the back of
the hand, a thin leather palm and thumb, bare middle and tip finger joints, and a wide hook-and-loop
strap with a label patch in the corner colour. The patch is gold on the dominant hand, and a gold
ankle band marks the dominant foot. A rear kick that lands drops the opponent to one knee for about
two seconds ("Knockdown").

## Accessibility (WCAG 2.1 AA)

Checked with axe-core on every page (including inside the component iframes), a contrast
calculation for every token pair, and a keyboard pass.

| Fixed | Criterion |
|---|---|
| Corner B colour used as text was 3.4:1; the steel corner is now 8.7:1 | 1.4.3 |
| White text on the accent fill was 3.45:1; fills now use `ACCENT_FILL` (5.7:1) | 1.4.3 |
| Input outlines were 1.2:1, now `FIELD_BORDER` (3.2:1) | 1.4.11 |
| Looping 3D animation had no way to stop, now has Pause and respects reduced motion | 2.2.2 |
| 3D views were mouse-only, now arrow keys and +/− | 2.1.1 |
| Toggle buttons had no state for screen readers, now `aria-pressed` | 4.1.2 |
| Charts had no text alternative, now an sr-only description | 1.1.1 |
| Section titles were plain divs, now heading level 2 | 1.3.1 |

Known framework issue: Streamlit puts `aria-expanded` on the sidebar `<section>`, which axe flags.
It comes from Streamlit itself and can't be fixed from the app.

Still worth testing by hand: VoiceOver or NVDA on the Plotly charts, and 200% zoom on the Overview
(its columns stack below about 1100px wide).

### Motion

- Idle: bounce on the balls of the feet, weight rocking front to back, hips drifting off the centre
  line, lead hand pawing. All of it stops while a strike or defence is in progress, and under
  reduced motion.
- Strikes snap out and come straight home: jab 0.42 s, cross 0.52 s, hook 0.6 s, uppercut 0.58 s,
  leg kick and teep 0.84 s, body kick 1.0 s. Hips and the back heel turn on rear-hand strikes, the
  lead foot pivots on the hook, the chin tucks behind the shoulder on punches.
- Footwork: a step moves the near foot first and drags the other, so feet stay planted while the
  body travels; circling is a pair of side steps.
- Defence: slip (head and hips off the line), cover (gloves to the temples), roll (drop and U-turn
  under a hook) and check (lead knee up against a leg kick). A strike is "defended" only by the
  defence that works against it.
