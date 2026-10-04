-- Star-style warehouse for the UFC stance & handedness project (SQLite).
-- Surrogate keys are INTEGER PRIMARY KEYs assigned by pipeline/transform.py (sorted by natural key,
-- so a rebuild from the same CSV gives the same keys). See docs/DATA_MODEL.md.
PRAGMA foreign_keys = ON;

CREATE TABLE dim_stance (
    stance_key  INTEGER PRIMARY KEY,
    stance      TEXT NOT NULL UNIQUE CHECK (stance IN ('Orthodox','Southpaw','Switch'))
);
CREATE TABLE dim_handedness (
    hand_key    INTEGER PRIMARY KEY,
    hand        TEXT NOT NULL UNIQUE CHECK (hand IN ('Right','Left'))
);
CREATE TABLE dim_weight_class (
    weight_class_key  INTEGER PRIMARY KEY,
    weight_class      TEXT NOT NULL UNIQUE,
    gender            TEXT NOT NULL CHECK (gender IN ('Men','Women'))
);
CREATE TABLE dim_country (
    country_key  INTEGER PRIMARY KEY,
    country      TEXT NOT NULL UNIQUE,
    continent    TEXT NOT NULL
);
CREATE TABLE dim_fighting_style (
    style_key       INTEGER PRIMARY KEY,
    fighting_style  TEXT NOT NULL UNIQUE
);
CREATE TABLE dim_fighter (
    fighter_key          INTEGER PRIMARY KEY,
    fighter_name         TEXT NOT NULL UNIQUE,         -- natural / business key
    gender               TEXT NOT NULL CHECK (gender IN ('Men','Women')),
    dob                  TEXT NOT NULL,                -- ISO date
    ufcstats_url         TEXT,
    is_champion          INTEGER NOT NULL CHECK (is_champion IN (0,1)),   -- curated flag
    is_active            INTEGER CHECK (is_active IN (0,1)),
    stance_project       TEXT,                         -- stance in the original project Excel
    weight_class_source  TEXT,                         -- 'original' | 'corrected'
    learning_tip         TEXT
);

-- Grain: one row per fighter (career snapshot of the project record + physical attributes).
CREATE TABLE fact_fighter_record (
    fighter_key       INTEGER PRIMARY KEY REFERENCES dim_fighter(fighter_key),
    stance_key        INTEGER NOT NULL REFERENCES dim_stance(stance_key),
    hand_key          INTEGER NOT NULL REFERENCES dim_handedness(hand_key),
    weight_class_key  INTEGER NOT NULL REFERENCES dim_weight_class(weight_class_key),
    country_key       INTEGER NOT NULL REFERENCES dim_country(country_key),
    style_key         INTEGER NOT NULL REFERENCES dim_fighting_style(style_key),
    wins              INTEGER NOT NULL CHECK (wins >= 0),
    losses            INTEGER NOT NULL CHECK (losses >= 0),
    total_fights      INTEGER NOT NULL CHECK (total_fights = wins + losses),
    win_rate          REAL NOT NULL CHECK (win_rate BETWEEN 0 AND 100),
    height_cm         REAL,
    reach_cm          REAL,
    ape_index_cm      REAL,
    age_years         REAL,
    popularity_index  INTEGER CHECK (popularity_index BETWEEN 0 AND 100)
);

-- Grain: one row per fighter that has UFC fight-level stats (career totals / rates).
CREATE TABLE fact_ufc_performance (
    fighter_key       INTEGER PRIMARY KEY REFERENCES dim_fighter(fighter_key),
    ufc_fights        INTEGER NOT NULL,
    ufc_wins          INTEGER NOT NULL,
    ufc_losses        INTEGER NOT NULL,
    ufc_ko_wins       INTEGER NOT NULL,
    ufc_sub_wins      INTEGER NOT NULL,
    ufc_dec_wins      INTEGER NOT NULL,
    title_fights      INTEGER,
    main_events       INTEGER,
    first_ufc_fight   TEXT,
    last_ufc_fight    TEXT,
    stats_fights      INTEGER,
    ufc_minutes       REAL,
    slpm REAL, str_acc REAL, sapm REAL, str_def REAL,
    td_avg REAL, td_acc REAL, td_def REAL, sub_avg REAL, kd_avg REAL, ctrl_pct REAL,
    pct_distance REAL, pct_clinch REAL, pct_ground REAL,
    pct_head REAL, pct_body REAL, pct_leg REAL,
    striking_index    REAL,
    grappling_index   REAL
);

-- Audit trail of the last load (one row per table).
CREATE TABLE etl_load_audit (
    table_name  TEXT PRIMARY KEY,
    row_count   INTEGER NOT NULL,
    source_file TEXT NOT NULL
);

-- Indexes on the foreign keys and the columns the analysis queries filter / group by.
CREATE INDEX ix_fact_record_stance      ON fact_fighter_record(stance_key);
CREATE INDEX ix_fact_record_hand        ON fact_fighter_record(hand_key);
CREATE INDEX ix_fact_record_stance_hand ON fact_fighter_record(stance_key, hand_key);
CREATE INDEX ix_fact_record_weight      ON fact_fighter_record(weight_class_key);
CREATE INDEX ix_fact_record_country     ON fact_fighter_record(country_key);
CREATE INDEX ix_fact_record_style       ON fact_fighter_record(style_key);
CREATE INDEX ix_fact_record_win_rate    ON fact_fighter_record(win_rate);
CREATE INDEX ix_fact_perf_first_fight   ON fact_ufc_performance(first_ufc_fight);
CREATE INDEX ix_dim_country_continent   ON dim_country(continent);

-- Convenience view: one denormalised row per fighter for ad-hoc analysis.
CREATE VIEW vw_fighter_profile AS
SELECT f.fighter_key, f.fighter_name, f.gender, f.is_champion,
       s.stance, h.hand, s.stance || ' + ' || h.hand AS stance_hand,
       w.weight_class, c.country, c.continent, st.fighting_style,
       r.wins, r.losses, r.total_fights, r.win_rate,
       r.height_cm, r.reach_cm, r.ape_index_cm, r.age_years, r.popularity_index
FROM fact_fighter_record r
JOIN dim_fighter        f  ON f.fighter_key       = r.fighter_key
JOIN dim_stance         s  ON s.stance_key        = r.stance_key
JOIN dim_handedness     h  ON h.hand_key          = r.hand_key
JOIN dim_weight_class   w  ON w.weight_class_key  = r.weight_class_key
JOIN dim_country        c  ON c.country_key       = r.country_key
JOIN dim_fighting_style st ON st.style_key        = r.style_key;
