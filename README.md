
Brian phu <brianphu2310@gmail.com>
9:22 AM (15 minutes ago)
to me

# UFC Stance & Handedness Intelligence

### *An end-to-end data project that started on the sparring mats at UFC Gym Townhall, Sydney*

[![Live App][(https://img.shields.io/badge/🥊_Streamlit_App-Live-00E5CC?style=for-the-badge)](https://36kgywkvnlkwdy46v7tukw.streamlit.app](https://ufcstanceandhandednessintelligence-qsdqucvqpj5hhwymhqbeji.streamlit.app))
<img width="1512" height="799" alt="image" src="https://github.com/user-attachments/assets/d12d185e-c309-474f-a513-7427188b05a6" />
<img width="1512" height="798" alt="image" src="https://github.com/user-attachments/assets/1cafe294-e9c9-451c-b872-aa469dae21ae" />
<img width="1512" height="800" alt="image" src="https://github.com/user-attachments/assets/c1b2ec7b-6fa4-47c3-bb11-625cbbc11591" />
<img width="1512" height="798" alt="image" src="https://github.com/user-attachments/assets/4f2caf2f-3022-4ac7-b1bd-44820f742c66" />
<img width="1512" height="799" alt="image" src="https://github.com/user-attachments/assets/0d14f465-8d83-4191-9134-e1e9a715a4c7" />

[![Tableau][(https://img.shields.io/badge/📊_Tableau_Dashboard-Live-9B59EF?style=for-the-badge)]](https://public.tableau.com/app/profile/brian.ma5935/viz/UFC_STANCE_AND_HANDEDNESS_DASHBOARD/Dashboard1)(https://public.tableau.com/app/profile/brian.ma5935/viz/UFC_STANCE_AND_HANDEDNESS_DASHBOARD/Dashboard1)
<img width="1058" height="750" alt="image" src="https://github.com/user-attachments/assets/ad5b300a-2c37-4eb8-985f-2bbfbd37c498" />
<img width="1037" height="744" alt="image" src="https://github.com/user-attachments/assets/a68c84c7-75ab-4d03-b4a0-80a0c31d0122" />


[![Colab][(https://img.shields.io/badge/📓_Full_Analysis-Google_Colab-F9AB00?style=for-the-badge)]](https://colab.research.google.com/drive/1zp4jVJM39wCb73EvXKWwPtgzM1n6mwWz)(https://colab.research.google.com/drive/1zp4jVJM39wCb73EvXKWwPtgzM1n6mwWz)
<img width="1009" height="601" alt="image" src="https://github.com/user-attachments/assets/b4222659-6bb1-4c16-8185-f1bdda12caad" />
<img width="895" height="501" alt="image" src="https://github.com/user-attachments/assets/3dcdc38c-ffc5-4aaf-93b9-670e4db2c331" />
<img width="895" height="496" alt="image" src="https://github.com/user-attachments/assets/f121850f-7b4b-47af-81cf-77d6dccc61b8" />
<img width="797" height="399" alt="image" src="https://github.com/user-attachments/assets/fa6c53a0-4083-437b-922e-9eb1c0632b14" />
<img width="554" height="403" alt="image" src="https://github.com/user-attachments/assets/b864161b-f465-4ebf-96d7-16d525b3dbd6" />






-----

## The Problem I Was Actually Trying to Solve

I train Kickboxing and Muay Thai at UFC Gym Townhall in Sydney — not professionally, just because I can’t stop. One sparring session, I stepped on my partner’s foot mid-combination. Not clumsiness. We were in mirror-image stances and our footwork geometries simply collided.

That small collision surfaced a real question: **does stance actually change a fighter’s win probability, or is it just a training inconvenience?**

Then I noticed something stranger about myself. I’m Southpaw (right foot forward). Conventional wisdom says a Southpaw’s nuclear weapon is the rear left cross — the weapon Conor McGregor, Alex Pereira, and Israel Adesanya all built their careers on. But my most dangerous punch is my **Jab**. My lead-hand jab has stunned training partners and controls distance in ways my rear cross doesn’t.

This created a testable hypothesis: *Right-handed fighters who adopt a Southpaw stance might fight differently — and possibly more effectively — than left-handed Southpaws, because their dominant hand is now the “unexpected” lead hand.*

I stopped speculating and built a data pipeline to find out.

-----

## What This Project Does

This is a **full-stack analytics project** spanning web scraping, statistical testing, machine learning, database engineering, and business intelligence — all answering a single, well-defined question.

```
UFC Stats Website
│
▼
Web Scraping (BeautifulSoup + Requests)
│
▼
Data Cleaning & Feature Engineering (Pandas + NumPy)
│
├──► Excel Dataset (Pandas → .xlsx)
│
├──► Statistical Analysis (SciPy: T-Test, Shapiro-Wilk, Levene, Cohen's d)
│
├──► PostgreSQL Database (convert.py + stored procedure match_fighters())
│
├──► Interactive Dashboard (Panel + HoloViews + Plotly)
│
├──► Fighter Recommender App (Streamlit + KNN via scikit-learn)
│
└──► Business Intelligence Dashboard (Tableau Public)
```

-----

## Key Findings

The data answered my hypothesis — with an important nuance.

### Finding 1: Stance alone doesn’t predict winning

|Group |Fighters (n)|Mean Win Rate|T-stat|P-value|
|--------|------------|-------------|------|-------|
|Orthodox|93 |72.1% |0.96 |0.34 |
|Southpaw|24 |73.8% |— |— |

Southpaws win slightly more often, but the difference is **not statistically significant** (p = 0.34). Claiming “Southpaw advantage” from this data alone would be misleading.

### Finding 2: The interaction of stance × handedness tells a different story

|Group |Fighters (n)|Mean Win Rate|
|---------------------------|------------|-------------|
|Orthodox + Right-handed |78 |70.2% |
|**Southpaw + Right-handed**|**23** |**74.3%** |

|Comparison |T-stat|P-value |Cohen’s d|Interpretation |
|--------------------------------|------|--------|---------|----------------------------------------------------|
|Southpaw+Right vs Orthodox+Right|1.85 |**0.07**|**0.43** |Marginal significance, small-medium practical effect|

A p-value of 0.07 is not significant at α=0.05, but Cohen’s d of 0.43 represents a real-world performance gap that a decision-maker — say, a coach or a betting analyst — would care about. **Statistical significance ≠ practical significance.** I explicitly surface both in the analysis.

### Finding 3: My style is rare and well-represented at the top

Only 19.6% of UFC fighters are right-handed Southpaws. The group’s highest performer is Sean O’Malley at 94.4% win rate — a fighter explicitly known for using his lead hand as a weapon in unorthodox ways.

This is me in the data. And now I know who to study.

-----

## Engineering Decisions (The “Why”, Not Just the “What”)

**Why KNN for fighter matching, not cosine similarity or Euclidean distance on raw values?**

Fighter physical attributes (height, reach, weight) are on different scales. Raw Euclidean distance would make weight (in kg) dominate over reach (in cm) despite reach being more predictive of striking range. I used MinMaxScaler before KNN to normalize all features to [0,1], making the similarity metric physically meaningful rather than just mathematically convenient.

**Why PostgreSQL with a stored procedure, not just query the CSV directly?**

The `match_fighters()` stored procedure encapsulates the matching logic server-side. This means any application layer (Streamlit, an API, a future mobile app) can call one function and get structured results — without each client reimplementing filtering logic. It’s the same reason production data teams write stored procedures: to decouple business logic from presentation layer.

**Why keep the Excel file as the Streamlit data source instead of querying PostgreSQL directly?**

Deliberate deployment decision. Streamlit Cloud doesn’t have a persistent database connection to a local PostgreSQL instance. The Excel file acts as a portable “data mart” — pre-cleaned, pre-validated — that deploys with zero infrastructure dependency. The PostgreSQL layer exists for analytical workloads and future API integration, not for the demo app.

**Why report Cohen’s d alongside p-values?**

With n=23 in the Southpaw+Right group, I’m working with a small sample. A small sample will almost always return a non-significant p-value even when a real effect exists. Cohen’s d measures the effect size independent of sample size. Reporting only p-values here would be analytically dishonest — the kind of mistake that leads to bad decisions in sports analytics, clinical research, and A/B testing alike.

-----

## Technical Stack

|Layer |Tool |Why This Tool |
|--------------|---------------------------------|-----------------------------------------------------------------------------------------|
|**Scraping** |BeautifulSoup, Requests |Lightweight, sufficient for static HTML; no Selenium overhead needed |
|**Processing**|Pandas, NumPy |Industry standard; vectorized operations for clean/transform pipelines |
|**Statistics**|SciPy |T-test, Levene’s (variance equality), Shapiro-Wilk (normality) — full assumption checking|
|**ML** |scikit-learn (KNN + MinMaxScaler)|Simple, interpretable similarity — right tool for a recommendation problem at this scale |
|**Dashboard** |Panel, HoloViews, Plotly |Reactive Python-native dashboard without frontend framework overhead |
|**Web App** |Streamlit |Fastest path from Python analysis to deployed interactive product |
|**Database** |PostgreSQL + stored procedure |Production-pattern ETL and encapsulated query logic |
|**BI** |Tableau Public |Stakeholder-facing geographic and performance visualization |

-----

## Project Structure

```
UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE/
│
├── UFC_DATA_SCRAPING.ipynb # Web scraping pipeline from UFC stats
├── UFC_DATA_CLEANING_PROCESSING.ipynb # Cleaning, feature engineering, validation
├── UFC_Visualization.ipynb # EDA, T-tests, Cohen's d, distribution plots
│
├── ufc_intelligence_app.py # Streamlit app (678 lines, KNN recommender)
├── ufc_panel_dashboard.py # Panel dashboard (3 tabs: Recommend/Stats/Geo)
├── convert.py # ETL: Excel → PostgreSQL
│
├── UFC_FINAL_DATASET.xlsx # Master cleaned dataset (used by Streamlit)
├── UFC_Data_Raw.xlsx # Raw scraped data
├── ufc_data.csv # Exported for Tableau
│
├── UNIT_TEST.py # Unit tests for data pipeline functions
└── requirements.txt # Pinned dependencies
```

-----

## How to Run Locally

```bash
# Clone
git clone https://github.com/brianphu2310/UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE.git
cd UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run ufc_intelligence_app.py

# Or open notebooks in order:
# 1. UFC_DATA_SCRAPING.ipynb
# 2. UFC_DATA_CLEANING_PROCESSING.ipynb
# 3. UFC_Visualization.ipynb
```

Or **no installation needed** — everything runs in browser:

|Platform |Link |What you get |
|-----------------|----------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
|Streamlit App |[Launch →]([https://36kgywkvnlkwdy46v7tukw.streamlit.app](https://ufcstanceandhandednessintelligence-qsdqucvqpj5hhwymhqbeji.streamlit.app)) |Enter your stats, find your fighter twin, see the map |
|Tableau Dashboard|[View →]([https://public.tableau.com/app/profile/brian.ma5935/viz/UFC_STANCE_AND_HANDEDNESS_DASHBOARD/Dashboard1](https://public.tableau.com/app/profile/brian.ma5935/viz/UFC_STANCE_AND_HANDEDNESS_DASHBOARD/Dashboard1))|Stance/handedness performance by continent and weight class|
|Google Colab |[Open →]([https://colab.research.google.com/drive/1zp4jVJM39wCb73EvXKWwPtgzM1n6mwWz](https://colab.research.google.com/drive/1zp4jVJM39wCb73EvXKWwPtgzM1n6mwWz)) |Full statistical analysis with Panel dashboard |

-----

## What I’d Do Differently With More Data

The most honest limitation of this project: n=117 fighters is small for the interaction analysis. The Southpaw+Right group has only 23 observations, which is why p=0.07 sits just outside significance. With a larger dataset I would:

- **Stratify by weight class** — the Southpaw advantage may be more pronounced in striking-heavy divisions (Bantamweight, Featherweight) than wrestling-dominant ones
- **Add temporal analysis** — does the Southpaw advantage erode as more coaches develop Southpaw-specific defence training?
- **Include strike accuracy and significant strikes landed** — win rate is a blunt instrument; per-minute striking metrics would validate whether the lead-hand hypothesis holds at the technique level

These are questions I’d pursue if I had access to the full UFC Stats API rather than scraped summary data.

-----

## About

Brian Phu — Data Analyst & Southpaw Kickboxer
UFC Gym Townhall, Sydney
[LinkedIn]([https://www.linkedin.com/in/brianphu2310](https://www.linkedin.com/in/brian-phu-data-analysta55353390/)) · [GitHub]([https://github.com/brianphu2310](https://github.com/brianphu2310))

> *“Every question I’ve answered in this project started with a physical observation on the mats. That’s what I want my data work to always do — stay connected to a real problem.”*
