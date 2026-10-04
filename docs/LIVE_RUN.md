# Last live ingestion run (UFCStats)

Written by the workflow `live-ingestion.yml` on a GitHub-hosted runner. Run: https://github.com/brianphu2310/UFC_STANCE_AND_HANDEDNESS_INTELLIGENCE/actions/runs/37233336917

- Run at (UTC): 2026-10-04T20:45:52Z

## First rows

## Run log (tail)
```
2026-10-04 20:45:50,508 DEBUG urllib3.connectionpool: Starting new HTTP connection (1): ufcstats.com:80
2026-10-04 20:45:50,643 DEBUG urllib3.connectionpool: http://ufcstats.com:80 "GET /robots.txt HTTP/1.1" 404 18
2026-10-04 20:45:52,038 DEBUG urllib3.connectionpool: http://ufcstats.com:80 "GET /statistics/fighters HTTP/1.1" 200 None
2026-10-04 20:45:52,039 INFO ingestion.fetch: fetched http://ufcstats.com/statistics/fighters (2994 chars)
2026-10-04 20:45:52,040 WARNING ingestion.ufcstats: no fighter table on page 1; stopping
2026-10-04 20:45:52,040 ERROR ingestion.ufcstats: no rows scraped; nothing written
```
