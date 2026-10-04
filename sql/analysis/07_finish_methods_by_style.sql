-- Q7. How each fighting style wins in the UFC: share of wins by KO/TKO, submission and decision.
-- Wins that fall in none of the three buckets (e.g. DQ) are reported as 'other'.
WITH wins AS (
    SELECT st.fighting_style,
           COUNT(*)               AS fighters,
           SUM(u.ufc_wins)        AS ufc_wins,
           SUM(u.ufc_ko_wins)     AS ko,
           SUM(u.ufc_sub_wins)    AS sub,
           SUM(u.ufc_dec_wins)    AS dec
    FROM fact_ufc_performance u
    JOIN fact_fighter_record r    ON r.fighter_key = u.fighter_key
    JOIN dim_fighting_style st    ON st.style_key  = r.style_key
    GROUP BY st.fighting_style
)
SELECT fighting_style, fighters, ufc_wins,
       ROUND(100.0 * ko  / ufc_wins, 1) AS ko_pct,
       ROUND(100.0 * sub / ufc_wins, 1) AS sub_pct,
       ROUND(100.0 * dec / ufc_wins, 1) AS decision_pct,
       ROUND(100.0 * (ufc_wins - ko - sub - dec) / ufc_wins, 1) AS other_pct,
       CASE WHEN 1.0 * (ko + sub) / ufc_wins >= 0.6 THEN 'high finish rate (>=60%)' ELSE 'lower finish rate (<60%)' END AS profile
FROM wins
ORDER BY ufc_wins DESC;
