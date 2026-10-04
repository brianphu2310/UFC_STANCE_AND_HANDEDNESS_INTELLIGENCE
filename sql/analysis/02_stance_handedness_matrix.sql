-- Q2. Stance x handedness interaction: counts, share of dataset and mean win rate per cell,
-- plus each cell's difference from the overall mean (window AVG over the whole table).
SELECT s.stance,
       h.hand,
       COUNT(*)                                          AS fighters,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_fighters,
       ROUND(AVG(r.win_rate), 2)                         AS mean_win_rate,
       ROUND(AVG(r.win_rate) - AVG(AVG(r.win_rate)) OVER (), 2) AS diff_vs_mean_of_cells,
       ROUND(MIN(r.win_rate), 1)                         AS min_win_rate,
       ROUND(MAX(r.win_rate), 1)                         AS max_win_rate
FROM fact_fighter_record r
JOIN dim_stance     s ON s.stance_key = r.stance_key
JOIN dim_handedness h ON h.hand_key   = r.hand_key
GROUP BY s.stance, h.hand
ORDER BY s.stance, h.hand;
