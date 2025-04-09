### Workflow

#### I. Prerequisites.
Need `data.csv` to run this workflow

#### II. Transform raw data into aggregated data
1. Run `load_and_clean_data.py`

2. Run `categorize-event-names.py`

3. Run `cd .. && python3 -m funnel_analysis.main`

#### III. Agent components

4. (WIP) Run `test.py` to crawl `top_dropoff_urls.csv` URLs

5. (WIP) Run `test2.py` to analyze the multiple screenshots

