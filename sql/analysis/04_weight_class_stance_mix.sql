-- Q4. Stance mix per weight class (conditional aggregation with CASE) and how each division's
-- southpaw share ranks (RANK window), keeping the divisions with at least 5 fighters.
WITH mix AS (
    SELECT w.weight_class,
           COUNT(*) AS fighters,
           SUM(CASE WHEN s.stance = 'Orthodox' THEN 1 ELSE 0 END) AS orthodox,
           SUM(CASE WHEN s.stance = 'Southpaw' THEN 1 ELSE 0 END) AS southpaw,
           SUM(CASE WHEN s.stance = 'Switch'   THEN 1 ELSE 0 END) AS switch_stance,
           AVG(r.win_rate) AS mean_win_rate
    FROM fact_fighter_record r
    JOIN dim_weight_class w ON w.weight_class_key = r.weight_class_key
    JOIN dim_stance s       ON s.stance_key       = r.stance_key
    GROUP BY w.weight_class
    HAVING COUNT(*) >= 5
)
SELECT weight_class, fighters, orthodox, southpaw, switch_stance,
       ROUND(100.0 * southpaw / fighters, 1) AS southpaw_pct,
       RANK() OVER (ORDER BY 1.0 * southpaw / fighters DESC) AS southpaw_share_rank,
       ROUND(mean_win_rate, 2) AS mean_win_rate
FROM mix
ORDER BY southpaw_share_rank, weight_class;
