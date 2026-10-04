-- Q1. Does stance alone separate win rates?
-- Mean of per-fighter win rates vs pooled win rate (sum of wins / sum of fights), with a
-- sample-size flag (CASE) and each stance's share of all fighters (window function).
WITH by_stance AS (
    SELECT s.stance,
           COUNT(*)                        AS fighters,
           AVG(r.win_rate)                 AS mean_win_rate,
           1.0 * SUM(r.wins) / SUM(r.total_fights) * 100 AS pooled_win_rate,
           AVG(r.total_fights)             AS avg_fights
    FROM fact_fighter_record r
    JOIN dim_stance s ON s.stance_key = r.stance_key
    GROUP BY s.stance
)
SELECT stance,
       fighters,
       ROUND(100.0 * fighters / SUM(fighters) OVER (), 1) AS pct_of_fighters,
       ROUND(mean_win_rate, 2)   AS mean_win_rate,
       ROUND(pooled_win_rate, 2) AS pooled_win_rate,
       ROUND(avg_fights, 1)      AS avg_fights,
       CASE WHEN fighters < 10 THEN 'small sample (n<10)'
            WHEN fighters < 30 THEN 'moderate sample'
            ELSE 'larger sample' END AS sample_note
FROM by_stance
ORDER BY fighters DESC;
