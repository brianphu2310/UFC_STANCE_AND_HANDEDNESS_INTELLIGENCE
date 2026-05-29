<img width="4096" height="2304" alt="image" src="https://github.com/user-attachments/assets/9ad930fb-2875-495f-8f32-672549ddfed4" />

# UFC Stance & Handedness Intelligence
### *An end-to-end data project that started on the sparring mats at UFC Gym Townhall, Sydney*

[![Streamlit App](https://img.shields.io/badge/🥊_Streamlit_App-Live-00C7A3?style=for-the-badge&logo=streamlit&logoColor=white)](https://ufcstanceandhandednessintelligence-qsdqucvqpj5hhwymhqbeji.streamlit.app)
[![Tableau](https://img.shields.io/badge/📊_Tableau_Dashboard-Live-9B59EF?style=for-the-badge&logo=tableau&logoColor=white)](https://public.tableau.com/app/profile/brian.ma5935/viz/UFCRECOMENDATIONENGINE/Dashboard1)
[![Colab](https://img.shields.io/badge/📓_Full_Analysis-Google_Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)](https://colab.research.google.com/drive/1zp4jVJM39wCb73EvXKWwPtgzM1n6mwWz)
[![Kaggle Dataset](https://img.shields.io/badge/📦_Dataset-Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/brianphu)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray?style=for-the-badge)](LICENSE)

---

## The Problem I Was Actually Trying to Solve

I train Kickboxing and Muay Thai at UFC Gym Townhall in Sydney — not professionally, just because I can't stop. One sparring session, I stepped on my partner's foot mid-combination. Not clumsiness — we were in **mirror-image stances** and our footwork geometries simply collided.

That small collision surfaced a real question: **does stance actually change a fighter's win probability, or is it just a training inconvenience?**

Then I noticed something stranger about myself. I'm Southpaw (right foot forward). Conventional wisdom says a Southpaw's nuclear weapon is the rear left cross — the weapon Conor McGregor, Alex Pereira, and Israel Adesanya all built their careers on. But my most dangerous punch is my **jab**. My lead-hand jab has stunned training partners and controls distance in ways my rear cross doesn't.

This created a testable hypothesis:

> *Right-handed fighters who adopt a Southpaw stance might fight differently — and possibly more effectively — than left-handed Southpaws, because their dominant hand is now the "unexpected" lead hand.*

I stopped speculating and built a data pipeline to find out.

---

##  What This Project Solves

### Problem 1: Fighters don't know who to study

| Before | After |
|--------|-------|
| Beginners watch random UFC fights with no direction | App recommends **top 5 similar fighters** based on your physical stats |
| "Who fights like me?" takes months to figure out | **30 seconds** to get personalized recommendations |
| No data on which fighters match your stance + handedness combo | KNN algorithm finds **statistically similar fighters** |

**Solution:** Streamlit app with KNN + MinMaxScaler → finds your fighter twin.

---

### Problem 2: Coaches can't prove stance advantages with data

| Before | After |
|--------|-------|
| "Southpaw advantage" is just gym talk, no evidence | **Statistical tests** (T-Test, p-value, Cohen's d) show the real effect |
| No one knows if the advantage is stance OR handedness | **Interaction analysis** (stance × handedness) isolates the real variable |
| Decisions based on anecdotes, not data | **Evidence-based** coaching decisions |

**Solution:** Statistical analysis in Python (SciPy) + Tableau dashboard.

---

### Problem 3: Trainees waste time watching wrong fighters

| Before | After |
|--------|-------|
| A right-handed Southpaw watches Orthodox fighters → wrong techniques | App recommends **right-handed Southpaw** fighters specifically |
| No filter by weight class | **Weight class filter** in Tableau dashboard |
| "What should I learn from this fighter?" → no guidance | **Specific tips** for each recommended fighter |

**Solution:** Fighter recommender + training tips + geographic map.

---

### Problem 4: No one knows if the "rare style" actually wins

| Before | After |
|--------|-------|
| Everyone says Southpaw is rare, but does it help? | **Quantified:** 23/117 fighters (19.6%) are right-handed Southpaws |
| "Right-handed Southpaw might be good" — no numbers | **74.3% mean win rate** vs 70.2% for Orthodox+Right |
| Coaches can't decide which stance to teach | **Cohen's d = 0.43** (small-medium practical advantage) |

**Solution:** Effect size measurement + win rate analysis by group.

---

##  Live Demos
<img width="1505" height="938" alt="image" src="https://github.com/user-attachments/assets/4583a410-aaba-4274-aea2-8daac6f00f0e" />


### 1 — Streamlit App · Fighter Recommender

> 🔗 **[Launch App →](https://ufcstanceandhandednessintelligence-qsdqucvqpj5hhwymhqbeji.streamlit.app)**

<img width="1512" alt="Streamlit main interface" src="https://github.com/user-attachments/assets/d12d185e-c309-474f-a513-7427188b05a6" />
<img width="1512" alt="Similar fighters results" src="https://github.com/user-attachments/assets/1cafe294-e9c9-451c-b872-aa469dae21ae" />
<img width="1512" alt="Geographic map" src="https://github.com/user-attachments/assets/c1b2ec7b-6fa4-47c3-bb11-625cbbc11591" />
<img width="1512" alt="App detail view" src="https://github.com/user-attachments/assets/4f2caf2f-3022-4ac7-b1bd-44820f742c66" />
<img width="1512" alt="App results page" src="https://github.com/user-attachments/assets/0d14f465-8d83-4191-9134-e1e9a715a4c7" />

---

### 2 — Tableau Dashboard

> 🔗 **[View Dashboard →](https://public.tableau.com/app/profile/brian.ma5935/viz/UFCRECOMENDATIONENGINE/Dashboard1)**

<img width="1058" alt="Tableau dashboard" src="https://github.com/user-attachments/assets/ad5b300a-2c37-4eb8-985f-2bbfbd37c498" />
<img width="1037" alt="Tableau filter view" src="https://github.com/user-attachments/assets/a68c84c7-75ab-4d03-b4a0-80a0c31d0122" />

---

### 3 — Google Colab · Full Statistical Analysis

> 🔗 **[Open in Colab →](https://colab.research.google.com/drive/1zp4jVJM39wCb73EvXKWwPtgzM1n6mwWz)**

<img width="1009" alt="Statistical test results" src="https://github.com/user-attachments/assets/b4222659-6bb1-4c16-8185-f1bdda12caad" />
<img width="895" alt="Distribution plots" src="https://github.com/user-attachments/assets/3dcdc38c-ffc5-4aaf-93b9-670e4db2c331" />
<img width="895" alt="Panel dashboard" src="https://github.com/user-attachments/assets/f121850f-7b4b-47af-81cf-77d6dccc61b8" />
<img width="797" alt="Recommendations tab" src="https://github.com/user-attachments/assets/fa6c53a0-4083-437b-922e-9eb1c0632b14" />
<img width="554" alt="Colab notebook view" src="https://github.com/user-attachments/assets/b864161b-f465-4ebf-96d7-16d525b3dbd6" />

---

##  Data Collection — Multi-Source Scraping

**File:** `UFC_DATA_SCRAPING.ipynb`

All data is sourced from publicly available websites. No synthetic data. No paid APIs. The pipeline pulls from **three complementary sources** to maximise coverage and cross-validate records.

### Source 1 — UFCSTATS.com (primary)

The official UFC statistics database. Used for: stance, handedness, physical attributes, career record, and win rate.

```python
BASE_URL = "http://www.ufcstats.com/statistics/fighters"

# Paginate through A–Z fighter index
for letter in string.ascii_lowercase:
    index_url = f"{BASE_URL}?char={letter}&page=all"
    response  = requests.get(index_url, headers=HEADERS)
    soup      = BeautifulSoup(response.content, 'html.parser')

    fighter_links = [
        a['href'] for a in soup.select('td.b-statistics__table-col a')
    ]

    for url in fighter_links:
        r    = requests.get(url, headers=HEADERS)
        fsoup = BeautifulSoup(r.content, 'html.parser')

        name       = fsoup.select_one('.b-content__title-highlight').text.strip()
        stance     = extract_attr(fsoup, 'Stance')
        reach      = extract_attr(fsoup, 'Reach')
        height     = extract_attr(fsoup, 'Height')
        wins       = int(fsoup.select_one('.b-content__info-item:nth-child(1)').text.split()[0])
        losses     = int(fsoup.select_one('.b-content__info-item:nth-child(2)').text.split()[0])
        win_rate   = round(wins / (wins + losses) * 100, 1) if (wins + losses) > 0 else None

        fighters.append({
            'name': name, 'stance': stance, 'reach': reach,
            'height': height, 'wins': wins, 'losses': losses,
            'win_rate': win_rate
        })

    time.sleep(1.2)  # polite crawl delay
```

### Source 2 — Tapology.com (handedness + nationality enrichment)

UFCSTATS does not expose handedness directly. Tapology fighter profiles include dominant hand, nationality, and gym affiliation — used to enrich the primary dataset.

```python
BASE_TAPOLOGY = "https://www.tapology.com/search?term={name}&type=fighters"

def get_tapology_data(fighter_name: str) -> dict:
    search_url = BASE_TAPOLOGY.format(name=urllib.parse.quote(fighter_name))
    soup       = BeautifulSoup(requests.get(search_url, headers=HEADERS).content, 'html.parser')

    first_result = soup.select_one('a.name')
    if not first_result:
        return {}

    profile_url  = "https://www.tapology.com" + first_result['href']
    psoup        = BeautifulSoup(requests.get(profile_url, headers=HEADERS).content, 'html.parser')

    handedness  = extract_detail(psoup, 'Stance')   # 'Orthodox' / 'Southpaw'
    dominant    = extract_detail(psoup, 'Dominant Hand')  # 'Right' / 'Left'
    nationality = extract_detail(psoup, 'Nationality')
    gym         = extract_detail(psoup, 'Gym')

    return {'handedness': dominant, 'nationality': nationality, 'gym': gym}
```

### Source 3 — Sherdog.com (career history validation)

Sherdog provides independent fight records used to cross-validate win/loss counts from UFCSTATS and catch discrepancies (title changes, no-contests, DQ outcomes).

```python
def validate_record_sherdog(fighter_name: str, ufc_wins: int, ufc_losses: int) -> dict:
    search_url = f"https://www.sherdog.com/stats/fightfinder?SearchTxt={urllib.parse.quote(fighter_name)}"
    soup       = BeautifulSoup(requests.get(search_url, headers=HEADERS).content, 'html.parser')

    profile_link = soup.select_one('a.result-link')
    if not profile_link:
        return {'validated': False}

    psoup    = BeautifulSoup(requests.get("https://www.sherdog.com" + profile_link['href'], headers=HEADERS).content, 'html.parser')
    record   = psoup.select_one('.record')
    s_wins   = int(record.select_one('.wins span').text)
    s_losses = int(record.select_one('.losses span').text)

    return {
        'validated':      (s_wins == ufc_wins and s_losses == ufc_losses),
        'sherdog_wins':   s_wins,
        'sherdog_losses': s_losses,
        'discrepancy':    abs(s_wins - ufc_wins) + abs(s_losses - ufc_losses)
    }
```

### Merge & deduplication

```python
# Merge all three sources on normalised fighter name
df_ufc      = pd.read_csv('raw_ufcstats.csv')
df_tapology = pd.read_csv('raw_tapology.csv')
df_sherdog  = pd.read_csv('raw_sherdog.csv')

df = (df_ufc
      .merge(df_tapology, on='name_normalised', how='left')
      .merge(df_sherdog[['name_normalised','validated','discrepancy']],
             on='name_normalised', how='left'))

# Drop fighters with missing stance or handedness after enrichment
df = df.dropna(subset=['stance', 'handedness'])
df = df[df['validated'] != False]   # remove records with mismatched fight history

print(f"Final dataset: {len(df)} fighters")  # → 117 fighters
```

| Data point | Primary source | Enrichment source |
|---|---|---|
| Name | UFCSTATS | — |
| Height | UFCSTATS | — |
| Reach | UFCSTATS | — |
| Weight class | UFCSTATS | — |
| Stance (Orthodox / Southpaw) | UFCSTATS | Tapology (cross-check) |
| Handedness (Right / Left) | Tapology | — |
| Wins / Losses | UFCSTATS | Sherdog (validated) |
| Win rate % | Calculated | — |
| Nationality | Tapology | — |
| Gym | Tapology | — |

**Raw output:** `UFC_Data_Raw.xlsx` — 117 fighters × 12 attributes.


##  Excel Dashboard — Pivot Tables + XLOOKUP for Fighter Analysis

**File:** `UFC_FINAL_DATASET.xlsx`
<img width="753" height="666" alt="image" src="https://github.com/user-attachments/assets/bc193a7b-6f28-49c0-adfb-19b7fb3bf617" />


Not every fight fan wants to run Python code or navigate Tableau. Sometimes you just want to open Excel, type a name, and get answers.

So I built an Excel dashboard for the dataset — because quick questions deserve quick answers.

### What's Inside (5 Sheets)

| Sheet | Core Excel Feature | What It Does |
|-------|-------------------|---------------|
|  **Fighter Lookup** | XLOOKUP | Type a fighter name → stance, handedness, win rate, weight class |
|  **Stance Pivot** | Pivot Table | Average win rate by stance (Orthodox vs Southpaw) |
|  **Handedness Pivot** | Pivot Table | Average win rate by handedness (Right vs Left) |
|  **Stance × Handedness** | Pivot Table | Interaction analysis — 4 groups (Orthodox+Right, Southpaw+Right, etc.) |
|  **Weight Class Pivot** | Pivot Table + Slicer | Win rate by weight class — filter by stance or handedness |

### The XLOOKUP Setup (Fighter Lookup Sheet)

```excel
# User types fighter name in B2 → everything below appears automatically

=XLOOKUP(B2, Fighters[Name], Fighters[Stance], "Not found")
=XLOOKUP(B2, Fighters[Name], Fighters[Handedness], "Not found")
=XLOOKUP(B2, Fighters[Name], Fighters[Win_Rate], "Not found")
=XLOOKUP(B2, Fighters[Name], Fighters[Weight_Class], "Not found")
=XLOOKUP(B2, Fighters[Name], Fighters[Nationality], "Not found")

---

##  Dataset on Kaggle

The cleaned dataset (`UFC_FINAL_DATASET.xlsx` + `ufc_data.csv`) is published publicly on Kaggle so anyone can use it for their own analysis — no scraping required.

>  **[Download dataset → kaggle.com/brianphu](https://www.kaggle.com/brianphu)**

**What's included:**

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| `UFC_FINAL_DATASET.xlsx` | 117 | 12 | Cleaned master dataset used by Streamlit |
| `ufc_data.csv` | 117 | 12 | CSV version for Tableau + Python analysis |

**Column reference:**

| Column | Type | Example |
|--------|------|---------|
| `name` | string | Sean O'Malley |
| `height_cm` | float | 175.0 |
| `reach_cm` | float | 182.0 |
| `weight_lbs` | float | 145.0 |
| `weight_class` | string | Bantamweight |
| `stance` | string | Southpaw |
| `handedness` | string | Right |
| `wins` | int | 17 |
| `losses` | int | 1 |
| `win_rate` | float | 94.4 |
| `nationality` | string | USA |
| `continent` | string | North America |

If you use this dataset in your own project, a ⭐ on the repo or an upvote on Kaggle is always appreciated.

---

##  Key Findings

### Finding 1 — Stance alone doesn't predict winning

| Group | n | Mean Win Rate | T-stat | P-value |
|-------|---|--------------|--------|---------|
| Orthodox | 93 | 72.1% | 0.96 | 0.34 |
| Southpaw | 24 | 73.8% | — | — |

Southpaws win slightly more often, but the difference is **not statistically significant** (p = 0.34). Claiming "Southpaw advantage" from stance alone would be misleading.

---

### Finding 2 — Stance × handedness tells a different story

| Group | n | Mean Win Rate |
|-------|---|--------------|
| Orthodox + Right-handed | 78 | 70.2% |
| **Southpaw + Right-handed** | **23** | **74.3%** |

| Comparison | T-stat | P-value | Cohen's d | Interpretation |
|---|---|---|---|---|
| Southpaw+Right vs Orthodox+Right | 1.85 | 0.07 | **0.43** | Marginal significance, small-medium practical effect |

> p = 0.07 is not significant at α = 0.05, but **Cohen's d = 0.43** represents a real-world performance gap a coach or betting analyst would care about. Statistical significance ≠ practical significance — both are surfaced explicitly here.

---

### Finding 3 — The rare style is well-represented at the top

Only **19.6%** of UFC fighters are right-handed Southpaws. The group's highest performer is **Sean O'Malley at 94.4% win rate** — a fighter explicitly known for using his lead hand as a weapon in unorthodox ways.

---

##  How to Find Your Fighter Twin

### Method 1 — Streamlit App (easiest)

**Link:** [https://ufcstanceandhandednessintelligence-qsdqucvqpj5hhwymhqbeji.streamlit.app](https://ufcstanceandhandednessintelligence-qsdqucvqpj5hhwymhqbeji.streamlit.app)

| Step | What to do |
|------|-----------|
| 1 | Enter your **Height** (cm) |
| 2 | Enter your **Reach** (cm) |
| 3 | Enter your **Weight** (lbs) |
| 4 | Select your **Stance** (Orthodox / Southpaw) |
| 5 | Select your **Handedness** (Right / Left) |
| 6 | Click **"Find My Fighter Twin"** |

**What you get:**
- Top 5 most similar fighters (KNN, normalized physical attributes)
- Match score (higher = more similar)
- Specific technique tips for each twin
- Interactive world map of where your twins come from

---

### Method 2 — Tableau Dashboard (deep analysis)

**Link:** [https://public.tableau.com/app/profile/brian.ma5935/vizzes](https://public.tableau.com/app/profile/brian.ma5935/vizzes)

| Filter | What it does |
|--------|-------------|
| Stance | Show only Orthodox OR Southpaw fighters |
| Handedness | Show only Right-handed OR Left-handed |
| Weight Class | Focus on your division |
| Continent | See geographic patterns |

---

### Method 3 — Google Colab (statistical analysis)

**Link:** [Open in Colab](https://colab.research.google.com/drive/1zp4jVJM39wCb73EvXKWwPtgzM1n6mwWz)

Click **Runtime → Run all** to see T-test results, Cohen's d effect sizes, and distribution plots.

---

##  Who You Should Study (According to the Data)

| Your Style | Fighter | Win Rate | Focus |
|---|---|---|---|
| **Southpaw + Right-handed** | Sean O'Malley | 94.4% | Lead hand precision, distance control, unconventional angles |
| **Southpaw + Right-handed** | Israel Adesanya | 88.9% | Feints, jab setups, counter striking |
| **Southpaw + Right-handed** | Conor McGregor | 78.6% | Left hand timing, precision striking |
| **Orthodox + Right-handed** | Khabib Nurmagomedov | 88.9% | Pressure, wrestling, fight IQ |
| **Orthodox + Right-handed** | Alexander Volkanovski | 88.2% | Footwork, adaptability, cardio |
| **Any + Left-handed** | Alex Pereira | 83.3% | Power striking, clinch setups |

---

##  Full Data Pipeline

```
UFCSTATS.com + Tapology.com + Sherdog.com
│
▼
Multi-Source Web Scraping (BeautifulSoup + Requests)
│                    UFC_DATA_SCRAPING.ipynb
▼
Merge, Validate & Deduplicate (Pandas)
│                    UFC_DATA_CLEANING_PROCESSING.ipynb
│
├──► UFC_Data_Raw.xlsx          (117 fighters × 12 attributes)
├──► UFC_FINAL_DATASET.xlsx     (cleaned master)
├──► ufc_data.csv               (Tableau export)
│
├──►  Published on Kaggle     kaggle.com/brianphu
│
├──► Statistical Analysis (SciPy: T-Test, Shapiro-Wilk, Levene, Cohen's d)
│                    UFC_Visualization.ipynb
│
├──► PostgreSQL Database (convert.py + stored procedure match_fighters())
│
├──► Interactive Dashboard (Panel + HoloViews + Plotly)
│                    ufc_panel_dashboard.py
│
├──► Fighter Recommender App (Streamlit + KNN via scikit-learn)
│                    ufc_intelligence_app.py
│
└──► Business Intelligence Dashboard (Tableau Public)
```

---

##  Technical Stack

| Layer | Tool | Why This Tool |
|---|---|---|
| Scraping | BeautifulSoup, Requests | Lightweight for static HTML; no Selenium overhead |
| Processing | Pandas, NumPy | Industry standard; vectorized operations |
| Statistics | SciPy | T-test, Levene's, Shapiro-Wilk — full assumption checking |
| ML | scikit-learn (KNN + MinMaxScaler) | Simple, interpretable similarity at this scale |
| Dashboard | Panel, HoloViews, Plotly | Reactive Python-native, no frontend framework needed |
| Web App | Streamlit | Fastest path from Python analysis to deployed product |
| Database | PostgreSQL + stored procedure | Encapsulated query logic, decoupled from app layer |
| BI | Tableau Public | Stakeholder-facing geographic and performance visualization |
| Dataset sharing | Kaggle | Public dataset hub — no installation required for consumers |

### Why KNN with MinMaxScaler?

Fighter attributes (height, reach, weight) are on different scales. Raw Euclidean distance would make weight dominate over reach, even though reach is more predictive of striking range. MinMaxScaler normalizes all features to [0, 1], making similarity physically meaningful.

### Why PostgreSQL with a stored procedure?

The `match_fighters()` stored procedure encapsulates matching logic server-side. Any application layer — Streamlit, an API, a future mobile app — calls one function and gets structured results, without reimplementing filtering logic client-side.

### Why Excel as the Streamlit data source (not PostgreSQL directly)?

Deliberate deployment decision. Streamlit Cloud has no persistent connection to a local PostgreSQL instance. The Excel file acts as a portable data mart — pre-cleaned, pre-validated — that deploys with zero infrastructure dependency.

### Why report Cohen's d alongside p-values?

With n = 23 in the Southpaw+Right group, a small sample will almost always return a non-significant p-value even when a real effect exists. Cohen's d measures effect size independent of sample size. Reporting only p-values here would be analytically dishonest — the kind of mistake that leads to bad decisions in sports analytics, clinical research, and A/B testing alike.

---

##  Project Structure

```
UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE/
│
├── UFC_DATA_SCRAPING.ipynb              # Web scraping — UFCSTATS, Tapology, Sherdog
├── UFC_DATA_CLEANING_PROCESSING.ipynb   # Merge, validate, feature engineering
├── UFC_Visualization.ipynb              # EDA, T-Tests, Cohen's d, Panel dashboard
│
├── ufc_intelligence_app.py              # Streamlit app (KNN recommender)
├── ufc_panel_dashboard.py               # Panel dashboard (3 tabs)
├── convert.py                           # ETL: Excel → PostgreSQL
│
├── UFC_FINAL_DATASET.xlsx               # Cleaned master dataset (used by Streamlit)
├── UFC_Data_Raw.xlsx                    # Raw scraped data pre-cleaning
├── ufc_data.csv                         # Exported for Tableau
│
├── UNIT_TEST.py                         # Unit tests for data pipeline
└── requirements.txt                     # Pinned dependencies
```

---

##  How to Run Locally

```bash
# Clone
git clone https://github.com/brianphu2310/UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE.git
cd UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run ufc_intelligence_app.py
```

**Or run notebooks in order:**
1. `UFC_DATA_SCRAPING.ipynb` — scrapes UFCSTATS + Tapology + Sherdog
2. `UFC_DATA_CLEANING_PROCESSING.ipynb` — merge, validate, engineer features
3. `UFC_Visualization.ipynb` — statistical analysis + Panel dashboard

**Want the data without scraping?** Download directly from Kaggle:
```bash
kaggle datasets download brianphu/ufc-stance-handedness-intelligence
```

---

##  Limitations & What I'd Do With More Data

The most honest limitation: n = 117 fighters is small for the interaction analysis. The Southpaw+Right group has only 23 observations, which is why p = 0.07 sits just outside significance.

With a larger dataset I would:

- **Stratify by weight class** — the Southpaw advantage may be more pronounced in striking-heavy divisions (Bantamweight, Featherweight) than wrestling-dominant ones
- **Add temporal analysis** — does the advantage erode as more coaches develop Southpaw-specific defence training?
- **Include strike accuracy and significant strikes landed** — win rate is a blunt instrument; per-minute striking metrics would validate whether the lead-hand hypothesis holds at technique level

---

##  About

**Brian Phu** — Data Analyst & Southpaw Kickboxer, UFC Gym Townhall Sydney

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/brian-phu-data-analysta55353390/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/brianphu2310)
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=flat&logo=kaggle&logoColor=white)](https://www.kaggle.com/brianphu)
[![Tableau](https://img.shields.io/badge/Tableau-E97627?style=flat&logo=tableau&logoColor=white)](https://public.tableau.com/app/profile/brian.ma5935/vizzes)

> *"Every question I've answered in this project started with a physical observation on the mats. That's what I want my data work to always do — stay connected to a real problem."*

---

**Last updated:** May 2026 &nbsp;|&nbsp; **Fighters analysed:** 117 &nbsp;|&nbsp; **Sources scraped:** 3 (UFCSTATS, Tapology, Sherdog) &nbsp;|&nbsp; **Dashboards:** 3 (Streamlit, Panel, Tableau) &nbsp;|&nbsp; One curious fighter

---

*MIT License — free to use, modify, and share.*


