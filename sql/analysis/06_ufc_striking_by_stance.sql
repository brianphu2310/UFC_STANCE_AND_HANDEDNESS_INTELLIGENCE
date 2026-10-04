-- Q6. UFC striking and grappling profile by stance and handedness (join to the UFC-performance fact).
-- Rates are averaged per fighter, fighters with fewer than 3 fights with fight-level stats excluded.
SELECT s.stance,
       h.hand,
       COUNT(*)                         AS fighters,
       ROUND(AVG(u.slpm), 2)            AS avg_sig_strikes_landed_per_min,
       ROUND(AVG(u.str_acc), 1)         AS avg_strike_accuracy_pct,
       ROUND(AVG(u.sapm), 2)            AS avg_sig_strikes_absorbed_per_min,
       ROUND(AVG(u.td_avg), 2)          AS avg_takedowns_per_15,
       ROUND(AVG(u.kd_avg), 2)          AS avg_knockdowns_per_15,
       ROUND(AVG(u.slpm) - AVG(u.sapm), 2) AS striking_differential
FROM fact_ufc_performance u
JOIN fact_fighter_record r ON r.fighter_key = u.fighter_key
JOIN dim_stance s          ON s.stance_key  = r.stance_key
JOIN dim_handedness h      ON h.hand_key    = r.hand_key
WHERE u.stats_fights >= 3
GROUP BY s.stance, h.hand
ORDER BY s.stance, h.hand;
