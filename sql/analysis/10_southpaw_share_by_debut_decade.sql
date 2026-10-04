-- Q10. Is southpaw representation changing across UFC debut cohorts? Cohort = decade of first
-- UFC fight. Uses LAG to show the change from the previous cohort. Descriptive only: the
-- 117 fighters are a curated set, not a random sample, and the 1990s cohort has very few fighters.
WITH cohort AS (
    SELECT (CAST(SUBSTR(u.first_ufc_fight, 1, 4) AS INTEGER) / 10) * 10 AS debut_decade,
           COUNT(*) AS fighters,
           SUM(CASE WHEN s.stance = 'Southpaw' THEN 1 ELSE 0 END) AS southpaws
    FROM fact_ufc_performance u
    JOIN fact_fighter_record r ON r.fighter_key = u.fighter_key
    JOIN dim_stance s          ON s.stance_key  = r.stance_key
    WHERE u.first_ufc_fight IS NOT NULL
    GROUP BY debut_decade
),
shares AS (
    SELECT debut_decade, fighters, southpaws, 100.0 * southpaws / fighters AS southpaw_pct
    FROM cohort
)
SELECT debut_decade || 's' AS debut_cohort, fighters, southpaws,
       ROUND(southpaw_pct, 1) AS southpaw_pct,
       ROUND(southpaw_pct - LAG(southpaw_pct) OVER (ORDER BY debut_decade), 1) AS change_vs_prev_cohort_pts
FROM shares
ORDER BY debut_decade;
