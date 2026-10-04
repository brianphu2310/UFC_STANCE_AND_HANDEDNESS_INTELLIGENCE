-- Q9. Where do the fighters come from? Country counts with each continent's share and the
-- country's rank inside its continent (join to dim_country, window functions, HAVING).
WITH country AS (
    SELECT c.continent, c.country,
           COUNT(*) AS fighters,
           AVG(r.win_rate) AS mean_win_rate,
           SUM(CASE WHEN s.stance = 'Southpaw' THEN 1 ELSE 0 END) AS southpaws
    FROM fact_fighter_record r
    JOIN dim_country c ON c.country_key = r.country_key
    JOIN dim_stance s  ON s.stance_key  = r.stance_key
    GROUP BY c.continent, c.country
    HAVING COUNT(*) >= 2
)
SELECT continent, country, fighters,
       RANK() OVER (PARTITION BY continent ORDER BY fighters DESC, country) AS rank_in_continent,
       ROUND(100.0 * fighters / SUM(fighters) OVER (PARTITION BY continent), 1) AS pct_of_continent_listed,
       southpaws,
       ROUND(mean_win_rate, 2) AS mean_win_rate
FROM country
ORDER BY continent, rank_in_continent;
