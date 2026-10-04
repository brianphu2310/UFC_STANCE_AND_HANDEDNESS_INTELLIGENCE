-- Q8. Win rate by experience band (CASE) and stance, with a running total of fighters per
-- stance across the bands (cumulative window). Experience = recorded W+L fights.
WITH banded AS (
    SELECT s.stance,
           CASE WHEN r.total_fights < 20 THEN '1: 10-19 fights'
                WHEN r.total_fights < 30 THEN '2: 20-29 fights'
                WHEN r.total_fights < 40 THEN '3: 30-39 fights'
                ELSE '4: 40+ fights' END AS experience_band,
           r.win_rate
    FROM fact_fighter_record r
    JOIN dim_stance s ON s.stance_key = r.stance_key
)
SELECT stance, experience_band,
       COUNT(*) AS fighters,
       SUM(COUNT(*)) OVER (PARTITION BY stance ORDER BY experience_band) AS cumulative_fighters,
       ROUND(AVG(win_rate), 2) AS mean_win_rate
FROM banded
GROUP BY stance, experience_band
ORDER BY stance, experience_band;
