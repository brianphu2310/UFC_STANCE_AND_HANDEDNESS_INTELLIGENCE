-- Q3. The project hypothesis in SQL: right-handed Southpaws vs right-handed Orthodox fighters.
-- Welch t statistic and Cohen's d computed from group means / sample variances (CTEs).
-- n is small, so read this as descriptive, not as a significance test.
WITH grp AS (
    SELECT CASE WHEN s.stance = 'Southpaw' THEN 'Southpaw+Right' ELSE 'Orthodox+Right' END AS grp,
           r.win_rate AS x
    FROM fact_fighter_record r
    JOIN dim_stance s     ON s.stance_key = r.stance_key
    JOIN dim_handedness h ON h.hand_key   = r.hand_key
    WHERE h.hand = 'Right' AND s.stance IN ('Southpaw', 'Orthodox')
),
stats AS (
    SELECT grp,
           COUNT(*) AS n,
           AVG(x)   AS mean,
           (SUM(x * x) - COUNT(*) * AVG(x) * AVG(x)) / (COUNT(*) - 1) AS var
    FROM grp GROUP BY grp
),
pair AS (
    SELECT a.n AS n_sp, a.mean AS mean_sp, a.var AS var_sp,
           b.n AS n_or, b.mean AS mean_or, b.var AS var_or
    FROM stats a JOIN stats b ON a.grp = 'Southpaw+Right' AND b.grp = 'Orthodox+Right'
)
SELECT n_sp  AS southpaw_right_n,
       n_or  AS orthodox_right_n,
       ROUND(mean_sp, 2) AS southpaw_right_mean,
       ROUND(mean_or, 2) AS orthodox_right_mean,
       ROUND(mean_sp - mean_or, 2) AS mean_diff,
       ROUND((mean_sp - mean_or) / sqrt(var_sp / n_sp + var_or / n_or), 2) AS welch_t,
       ROUND((mean_sp - mean_or) /
             sqrt(((n_sp - 1) * var_sp + (n_or - 1) * var_or) / (n_sp + n_or - 2)), 2) AS cohens_d,
       CASE WHEN ABS((mean_sp - mean_or) /
                     sqrt(((n_sp - 1) * var_sp + (n_or - 1) * var_or) / (n_sp + n_or - 2))) < 0.2 THEN 'negligible'
            WHEN ABS((mean_sp - mean_or) /
                     sqrt(((n_sp - 1) * var_sp + (n_or - 1) * var_or) / (n_sp + n_or - 2))) < 0.5 THEN 'small'
            WHEN ABS((mean_sp - mean_or) /
                     sqrt(((n_sp - 1) * var_sp + (n_or - 1) * var_or) / (n_sp + n_or - 2))) < 0.8 THEN 'medium'
            ELSE 'large' END AS effect_size_label
FROM pair;
