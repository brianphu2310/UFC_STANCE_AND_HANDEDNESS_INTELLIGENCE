-- Q5. Top 3 fighters by win rate in each division among those with at least 15 recorded
-- fights (ROW_NUMBER per partition), with the gap to the division average (window AVG).
WITH ranked AS (
    SELECT p.weight_class, p.fighter_name, p.stance, p.hand, p.wins, p.losses, p.win_rate,
           ROW_NUMBER() OVER (PARTITION BY p.weight_class
                              ORDER BY p.win_rate DESC, p.total_fights DESC, p.fighter_name) AS division_rank,
           AVG(p.win_rate) OVER (PARTITION BY p.weight_class) AS division_avg
    FROM vw_fighter_profile p
    WHERE p.total_fights >= 15
)
SELECT weight_class, division_rank, fighter_name, stance, hand, wins, losses,
       ROUND(win_rate, 2) AS win_rate,
       ROUND(win_rate - division_avg, 2) AS vs_division_avg
FROM ranked
WHERE division_rank <= 3
ORDER BY weight_class, division_rank;
