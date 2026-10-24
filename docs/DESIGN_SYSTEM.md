# Stance Intelligence design system

The app is built to look like a fight-night broadcast: an arena-black canvas, a red corner and a
blue corner, real fight photos in the page banners and in a slow slideshow behind every page, and
red neon light on the 3D stage. A gold rule marks reference lines and the
dominant hand and foot. The signature shape is the octagon: it appears in the logo mark, the hero
panels and the 3D mat. A faint chain-link diamond from the cage fence sits in the page background.

All tokens live in `ui.py`; Streamlit's own widgets (sliders, toggles, radios, inputs) take the same
colours from `.streamlit/config.toml`. Views import tokens as `ui.ACCENT`, `ui.INK_2` and so on.
The only hex values outside `ui.py` are in `.streamlit/config.toml` and the two three.js
components, and those mirror these tokens.

## Tokens

### Colour

| Token | Hex | Use | Contrast on BG |
|---|---|---|---|
| `BG` | `#0A0A0A` | Page canvas | — |
| `SURFACE` | `#151515` | Panels, charts | — |
| `SURFACE_2` | `#1F1F20` | Raised areas, inputs, hover | — |
| `BORDER` | `#2E2E30` | Decorative hairlines only | decorative |
| `FIELD_BORDER` | `#6E6E72` | Input and select outlines | 3.2:1 on SURFACE_2 |
| `INK` | `#F5F5F5` | Headings, values | 18.2:1 |
| `INK_2` | `#C8C8C8` | Body text | 11.8:1 |
| `INK_MUTED` | `#8E8E8E` | Labels, captions | 6.0:1 |
| `ACCENT` | `#EB3F45` | Red corner: marks, lines and text | 5.0:1 (4.6:1 on SURFACE) |
| `ACCENT_FILL` | `#C8102E` | Filled buttons, selected pills, sliders | white text 5.9:1 |
| `ACCENT_2` | `#3B82F6` | Blue corner: marks and lines (text uses `ACCENT_2_TEXT` `#5B9BFF`, 7.1:1) | 5.4:1 |
| `ON_ACCENT` | `#FFFFFF` | Text on `ACCENT_FILL` | 5.9:1 |
| `RULE` | `#E9B44C` | Reference lines, dominant side, focus ring | 10.5:1 |
| `MUTED_FILL` | `#2A2A2C` | Bars outside a selection | — |

Categorical palette (dark surface, assigned in a fixed order):
`#EB3F45`, `#3B82F6`, `#E9B44C`, `#2DBE8C`, `#B8B8B8`, `#6E6E72`.
Sequential scale (globe, bubbles): red-black `#2A0A0E` → red `#B3121A` → pale red `#FFB3B3`.

Helpers:
- `ui.text_color(c)`: use whenever a series colour is drawn as text (returns a text-safe variant where one exists).
- `ui.on_color(c)`: picks dark or white text for a label sitting on a fill of colour `c`.

### Type

| Role | Face | Size / weight |
|---|---|---|
| Page title (`h1`) | Big Shoulders Display | 3.1rem / 800, line-height 0.98 |
| Section title (`role="heading" aria-level="2"`) | Big Shoulders Display | 1.6rem / 700 |
| Card title, chart title | Big Shoulders Display | 1.35rem / 700, charts 19px |
| Stat value | Big Shoulders Display | 1.35–2.2rem / 700–800 |
| Body | Instrument Sans | 1rem / 400, line-height 1.5, max 70ch |
| Label, caption | Instrument Sans | 0.78–0.88rem / 500 |

Both fonts are self-hosted in `static/fonts` (OFL licensed) and served by Streamlit's static file serving (`enableStaticServing` in `.streamlit/config.toml`); `ui.inject_css()` declares the `@font-face` rules. The app makes no font requests to third parties.

Writing rules: sentence case everywhere, no all-caps labels, no middle-dot meta strings, and
numbers come with their unit ("4 cm short", not "−4").

### Shape, spacing, motion

- Radius is 3–4px on controls. Panels use the octagon cut (`clip-path`, 22–30px corner) instead of rounding.
- Spacing steps: 4, 8, 12, 16, 22, 30px. Sections open with 30px above them and a hairline.
- Motion: pages rise in on load, sections reveal as they scroll into view, tab panels slide in, a red
  sweep bar runs under the header while a request is running, and the background photos cross-fade
  slowly. The 3D views stop when the user presses Pause. Under `prefers-reduced-motion` the 3D views
  start paused and every CSS animation and transition is switched off.

## Iconography

`static/mark.svg` / `mark.png` is an octagon split down the middle into red and blue, the two corner colours. It
is the favicon and sits beside the wordmark in the top bar. It is an original mark and is
deliberately not the UFC logo: the app uses public fight data, but it is not affiliated with UFC.

The app uses no other icons. Words label every control.

## Components

| Component | Where | Notes |
|---|---|---|
| `ui.page_header(title, dek)` | Top of every page | Broadcast banner: page number and name, `h1`, one-sentence dek, and the page's fight photo with its credit (`static/hero/`, inlined as data URIs) |
| `ui.backdrop()` | Behind every page | Seven fight photos cross-fading in a random order under a dark veil |
| `ui.section(title, sub, estimated)` | Section breaks | Heading role level 2; `estimated` adds the dashed gold badge |
| Octagon hero (`st.container(key="oct_…")`) | Main panel of each page | The only place the octagon cut is used on a page |
| `.card` | Tale of the tape, plans | Title, meta line, `.kv` stat grid, `.pill` tags |
| `ui.callout(html)` | Verdicts and explanations | Red left rule |
| `.simlist / .simrow` | "Fights most like" | Name, meta, bar, score |
| `ui.chart(fig, key, alt)` | Every Plotly chart | Writes a screen-reader description (auto-built from title and series, or `alt`) |
| `globe3d` | Overview | Rotatable globe with country name cards |
| `body3d` | Explorer, Build a fighter, Spar vs Brian | Face-off, Height and Reach views; jab, cross and kick measured from real range |

### body3d controls

| Control | Type | States | Keyboard |
|---|---|---|---|
| Face-off / Height / Reach | Segmented, `aria-pressed` | Selected = red fill, white text | Tab, Enter or Space |
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
