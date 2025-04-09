import pandas as pd
import dask.dataframe as dd
import logging
import numpy as np
from .config import OUTPUT_DIR, CONFIG

def analyze_funnel(df: pd.DataFrame, stages: list) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Analyze funnel metrics and create a summary report."""
    logging.info("Analyzing funnel metrics")
    if isinstance(df, dd.DataFrame):
        stage_counts = df.groupby('stage')['session_id'].nunique().compute().reindex(stages).fillna(0)
    else:
        stage_counts = df.groupby('stage')['session_id'].nunique().reindex(stages).fillna(0)
    
    total_sessions = stage_counts[stages[0]]
    conversion_rates = (stage_counts / total_sessions).fillna(0)
    drop_off_rates = (1 - (stage_counts / stage_counts.shift(1))).fillna(0)
    
    summary_df = pd.DataFrame({
        'Stage': stages,
        'Users': stage_counts,
        'Conversion Rate (%)': (conversion_rates * 100).round(1),
        'Drop-Off Rate (%)': (drop_off_rates * 100).round(1)
    })
    max_drop_idx = drop_off_rates.idxmax()
    summary_df['Key Insight'] = summary_df['Stage'].apply(
        lambda x: f"Biggest drop-off: {drop_off_rates[x]:.0%}" if x == max_drop_idx else ""
    )
    summary_df.to_csv(OUTPUT_DIR / "funnel_summary.csv", index=False)
    
    return stage_counts, conversion_rates, drop_off_rates

def segment_users(df: pd.DataFrame, stages: list) -> pd.DataFrame:
    """Segment users by demographics."""
    logging.info("Segmenting users by demographics")
    if isinstance(df, dd.DataFrame):
        segmented = df.groupby(['stage', 'gender', 'age'])['session_id'].nunique().compute().reset_index()
    else:
        segmented = df.groupby(['stage', 'gender', 'age'])['session_id'].nunique().reset_index()
    
    segmented.columns = ['Stage', 'Gender', 'Age', 'User Count']
    segmented['Age Group'] = pd.cut(segmented['Age'], bins=[0, 18, 35, 50, 100], labels=['0-18', '19-35', '36-50', '51+'])
    # Ensure stage order
    segmented['Stage'] = pd.Categorical(segmented['Stage'], categories=stages, ordered=True)
    segmented = segmented.sort_values('Stage')
    segmented.to_csv(OUTPUT_DIR / "user_segments.csv", index=False)
    return segmented

def analyze_root_causes(df: pd.DataFrame, stages: list) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Analyze root causes with dynamic errors, events, and URLs."""
    logging.info("Performing root cause analysis")
    if isinstance(df, dd.DataFrame):
        time_spent = df.groupby('stage')['time_to_stage'].mean().compute()
        df['has_error'] = df['events'].apply(lambda x: any('error' in str(e).lower() for e in x), meta=('has_error', 'bool'))
        error_sessions = df[df['has_error']].groupby('stage')['session_id'].nunique().compute()
        top_events = df.explode('events').groupby(['stage', 'events'])['session_id'].nunique().compute().reset_index()
        url_dropoffs = df.groupby('url')['session_id'].nunique().compute().sort_values(ascending=False)
        stats = df.groupby('stage').agg({'time_to_stage': ['mean', 'median', 'std'], 'duration': ['mean', 'median', 'std']}).compute()
    else:
        time_spent = df.groupby('stage')['time_to_stage'].mean()
        df['has_error'] = df['events'].apply(lambda x: any('error' in str(e).lower() for e in x))
        error_sessions = df[df['has_error']].groupby('stage')['session_id'].nunique()
        top_events = df.explode('events').groupby(['stage', 'events'])['session_id'].nunique().reset_index()
        url_dropoffs = df.groupby('url')['session_id'].nunique().sort_values(ascending=False)
        stats = df.groupby('stage').agg({'time_to_stage': ['mean', 'median', 'std'], 'duration': ['mean', 'median', 'std']})
    
    # Ensure stage order in time_spent
    time_spent = time_spent.reindex(stages)
    time_spent_df = pd.DataFrame({'Stage': time_spent.index, 'Avg Time to Stage (s)': time_spent.values.round(2)})
    time_spent_df.to_csv(OUTPUT_DIR / "time_spent_per_stage.csv", index=False)
    
    # Ensure stage order in error_sessions
    error_sessions = error_sessions.reindex(stages)
    error_df = pd.DataFrame({'Stage': error_sessions.index, 'Sessions with Errors': error_sessions.values})
    error_df = error_df.dropna(subset=['Stage'])  # Remove any NaN stages
    error_df.to_csv(OUTPUT_DIR / "error_sessions_per_stage.csv", index=False)
    
    # Ensure stage order in top_events
    top_events['Stage'] = pd.Categorical(top_events['stage'], categories=stages, ordered=True)
    top_events = top_events.sort_values('Stage')
    # Select only the columns we need after nlargest
    top_events_df = top_events.groupby('stage').apply(lambda x: x.nlargest(5, 'session_id'))[['stage', 'events', 'session_id']].reset_index(drop=True)
    top_events_df.columns = ['Stage', 'Event', 'User Count']
    top_events_df.to_csv(OUTPUT_DIR / "top_events_per_stage.csv", index=False)

    # Create initial URL DataFrame
    url_df = pd.DataFrame({'URL': url_dropoffs.index, 'Drop-Off Sessions': url_dropoffs.values})

    ## filter url_df with URL not in /cart, /checkout, /purchase, /launch
    url_df = url_df[~url_df['URL'].str.contains('/cart|/checkout', na=False)]

    # Calculate statistics for drop-off detection
    mean_dropoff = url_df['Drop-Off Sessions'].mean()
    std_dropoff = url_df['Drop-Off Sessions'].std()
    threshold = mean_dropoff + std_dropoff  # Define significant drop threshold

    print(f"Mean drop-off sessions: {mean_dropoff}, Std dev: {std_dropoff}, Threshold for significant drop: {threshold}")
    
    filtered_url_df = url_df[url_df['Drop-Off Sessions'] >= threshold]
    # Save the filtered DataFrame
    filtered_url_df.to_csv(OUTPUT_DIR / "top_dropoff_urls.csv", index=False)
    
    stats_df = stats.reset_index()
    stats_df['stage'] = pd.Categorical(stats_df['stage'], categories=stages, ordered=True)
    stats_df = stats_df.sort_values('stage')
    stats_df.columns = ['Stage', 'Time Mean (s)', 'Time Median (s)', 'Time Std (s)', 'Duration Mean (s)', 'Duration Median (s)', 'Duration Std (s)']
    stats_df.to_csv(OUTPUT_DIR / "stage_stats.csv", index=False)
    
    return time_spent, error_df, top_events_df, stats_df