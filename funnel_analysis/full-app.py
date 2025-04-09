import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from datetime import datetime
import os
from pathlib import Path
import dask.dataframe as dd
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OUTPUT_DIR = Path("funnel_analysis_output")
OUTPUT_DIR.mkdir(exist_ok=True)

CONFIG = {
    'sessions_file': 'sessions.json',
    'funnel_events_file': 'funnel_events.json',
    'dask_threshold': 100000
}


def load_data(sessions_file: str, funnel_events_file: str) -> tuple[dict, list]:
    """Load sessions and funnel events from JSON files."""
    logging.info(f"Loading funnel events from {funnel_events_file}")
    with open(funnel_events_file, 'r') as f:
        funnel_events = json.load(f)
    
    logging.info(f"Loading sessions from {sessions_file}")
    with open(sessions_file, 'r') as f:
        sessions = json.load(f)
    
    return funnel_events, sessions

def process_sessions(sessions: list, funnel_events: dict) -> tuple[pd.DataFrame, list]:
    """Process sessions into a DataFrame with event sequences, timing, and URLs."""
    stages = list(funnel_events.keys())
    events_list = []
    
    logging.info("Processing sessions for funnel stages")
    for session in sessions:
        session_id = session['session_id']
        start_time = datetime.fromisoformat(session['start_session'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(session['end_session'].replace('Z', '+00:00'))
        duration = (end_time - start_time).total_seconds()
        events = session['events']
        
        event_data = [(event['event_name'], datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')),
                       event.get('page_url', 'N/A')) for event in events]
        event_names = [e[0] for e in event_data]
        event_timestamps = [e[1] for e in event_data]
        event_urls = [e[2] for e in event_data]
        
        for stage in stages:
            stage_events = set(funnel_events[stage])
            stage_hits = [i for i, event in enumerate(event_names) if event in stage_events]
            if stage_hits:
                first_hit = min(stage_hits)
                time_to_stage = (event_timestamps[first_hit] - start_time).total_seconds()
                events_list.append({
                    'session_id': session_id,
                    'stage': stage,
                    'time_to_stage': time_to_stage,
                    'duration': duration,
                    'events': event_names,
                    'url': event_urls[first_hit],
                    'timestamp': event_timestamps[first_hit],
                    'age': session.get('age'),
                    'gender': session.get('gender'),
                    'country': session.get('country')
                })
    
    df = pd.DataFrame(events_list)
    if len(sessions) > CONFIG['dask_threshold']:
        logging.info("Switching to Dask for large dataset processing")
        df = dd.from_pandas(df, npartitions=8)
    
    return df, stages

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
    """Segment users by demographics and visualize."""
    logging.info("Segmenting users by demographics")
    if isinstance(df, dd.DataFrame):
        segmented = df.groupby(['stage', 'gender', 'age'])['session_id'].nunique().compute().reset_index()
    else:
        segmented = df.groupby(['stage', 'gender', 'age'])['session_id'].nunique().reset_index()
    
    segmented.columns = ['Stage', 'Gender', 'Age', 'User Count']
    
    # Bin ages for better visualization
    segmented['Age Group'] = pd.cut(segmented['Age'], bins=[0, 18, 35, 50, 100], labels=['0-18', '19-35', '36-50', '51+'])
    pivot_df = segmented.pivot_table(index='Stage', columns=['Gender', 'Age Group'], values='User Count', fill_value=0)
    
    plt.figure(figsize=(14, 8))
    pivot_df.plot(kind='bar', stacked=True, colormap='tab20')
    plt.title('Users by Stage, Gender, and Age Group')
    plt.xlabel('Stage')
    plt.ylabel('Number of Users')
    plt.legend(title='Gender & Age', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "user_segments_chart.png", bbox_inches='tight')
    plt.close()
    
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
        url_dropoffs = df.groupby('url')['session_id'].nunique().compute().sort_values(ascending=False).head(50)
        stats = df.groupby('stage').agg({'time_to_stage': ['mean', 'median', 'std'], 'duration': ['mean', 'median', 'std']}).compute()
    else:
        time_spent = df.groupby('stage')['time_to_stage'].mean()
        df['has_error'] = df['events'].apply(lambda x: any('error' in str(e).lower() for e in x))
        error_sessions = df[df['has_error']].groupby('stage')['session_id'].nunique()
        top_events = df.explode('events').groupby(['stage', 'events'])['session_id'].nunique().reset_index()
        url_dropoffs = df.groupby('url')['session_id'].nunique().sort_values(ascending=False).head(50)
        stats = df.groupby('stage').agg({'time_to_stage': ['mean', 'median', 'std'], 'duration': ['mean', 'median', 'std']})
    
    time_spent_df = pd.DataFrame({'Stage': time_spent.index, 'Avg Time to Stage (s)': time_spent.values.round(2)})
    time_spent_df.to_csv(OUTPUT_DIR / "time_spent_per_stage.csv", index=False)
    
    error_df = pd.DataFrame({'Stage': error_sessions.index, 'Sessions with Errors': error_sessions.values})
    error_df.to_csv(OUTPUT_DIR / "error_sessions_per_stage.csv", index=False)
    
    top_events_df = top_events.groupby('stage').apply(lambda x: x.nlargest(5, 'session_id')).reset_index(drop=True)
    top_events_df.columns = ['Stage', 'Event', 'User Count']
    top_events_df.to_csv(OUTPUT_DIR / "top_events_per_stage.csv", index=False)
    
    url_df = pd.DataFrame({'URL': url_dropoffs.index, 'Drop-Off Sessions': url_dropoffs.values})
    url_df.to_csv(OUTPUT_DIR / "top_dropoff_urls.csv", index=False)
    
    stats_df = stats.reset_index()
    stats_df.columns = ['Stage', 'Time Mean (s)', 'Time Median (s)', 'Time Std (s)', 'Duration Mean (s)', 'Duration Median (s)', 'Duration Std (s)']
    stats_df.to_csv(OUTPUT_DIR / "stage_stats.csv", index=False)
    
    return time_spent, error_df, top_events_df, stats_df

def visualize_funnel(stage_counts: pd.Series, conversion_rates: pd.Series, drop_off_rates: pd.Series, stages: list):
    """Generate clear, business-friendly funnel visualizations."""
    logging.info("Generating funnel visualizations")
    
    fig = go.Figure(go.Funnel(
        y=stages, x=stage_counts, textposition="inside", 
        textinfo="value+percent previous", marker={"color": "teal"}
    ))
    fig.update_layout(title="User Journey Through Funnel", title_x=0.5)
    fig.write_image(OUTPUT_DIR / "funnel_chart.png")
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=stages, y=stage_counts, palette="Blues_d")
    plt.title('How Many Users Reach Each Stage?')
    plt.xlabel('Stage')
    plt.ylabel('Number of Users')
    for i, v in enumerate(stage_counts):
        plt.text(i, v + max(stage_counts) * 0.01, str(int(v)), ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "sessions_per_stage.png")
    plt.close()
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=stages[1:], y=drop_off_rates[1:] * 100, palette="Reds_d")
    plt.title('Where Are We Losing Users? (%)')
    plt.xlabel('Stage Transition')
    plt.ylabel('Drop-Off Rate (%)')
    for i, v in enumerate(drop_off_rates[1:] * 100):
        plt.text(i, v + 1, f"{v:.1f}%", ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "drop_off_rates.png")
    plt.close()

def visualize_root_causes(time_spent: pd.Series, error_df: pd.DataFrame, top_events_df: pd.DataFrame, df: pd.DataFrame, stages: list):
    """Visualize root cause analysis with additional charts."""
    logging.info("Generating root cause visualizations")
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=time_spent.index, y=time_spent.values, palette="Greens_d")
    plt.title('Average Time Spent Before Reaching Each Stage (s)')
    plt.xlabel('Stage')
    plt.ylabel('Time (seconds)')
    for i, v in enumerate(time_spent):
        plt.text(i, v + 1, f"{v:.1f}", ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "time_spent_per_stage.png")
    plt.close()

    if not error_df.empty:
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Stage', y='Sessions with Errors', data=error_df, palette="Reds_d")
        plt.title('Error Impact by Stage')
        plt.xlabel('Stage')
        plt.ylabel('Users Affected by Errors')
        for i, v in enumerate(error_df['Sessions with Errors']):
            plt.text(i, v + 1, str(int(v)), ha='center', va='bottom')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "error_sessions_per_stage.png")
        plt.close()

    plt.figure(figsize=(14, 8))
    sns.barplot(x='Stage', y='User Count', hue='Event', data=top_events_df, palette="viridis")
    plt.title('Top 5 Events per Stage')
    plt.xlabel('Stage')
    plt.ylabel('Number of Users')
    plt.legend(title='Event', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "top_events_per_stage.png", bbox_inches='tight')
    plt.close()

    if isinstance(df, dd.DataFrame):
        df = df.compute()
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='stage', y='time_to_stage', data=df, palette="Pastel1")
    plt.title('Time to Reach Each Stage (s) - Distribution')
    plt.xlabel('Stage')
    plt.ylabel('Time (seconds)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "time_to_stage_boxplot.png")
    plt.close()

# Fixed Heatmaps: Separate by Gender and Age Group
    if isinstance(df, dd.DataFrame):
        df = df.compute()

    # Bin ages for better visualization
    df['Age Group'] = pd.cut(df['age'], bins=[0, 18, 35, 50, 100], labels=['0-18', '19-35', '36-50', '51+'])
    
    # Gender Heatmap
    pivot_gender = df.pivot_table(index='stage', columns='gender', values='session_id', aggfunc='nunique', fill_value=0)
    pivot_gender = pivot_gender.div(pivot_gender.sum(axis=1), axis=0) * 100  # Normalize to percentages
    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot_gender, annot=True, fmt='.1f', cmap='YlOrRd', cbar_kws={'label': 'Percentage (%)'})
    plt.title('Drop-Off Patterns by Gender (%)')
    plt.xlabel('Gender')
    plt.ylabel('Stage')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "drop_off_gender_heatmap.png")
    plt.close()

    # Age Group Heatmap
    pivot_age = df.pivot_table(index='stage', columns='Age Group', values='session_id', aggfunc='nunique', fill_value=0)
    pivot_age = pivot_age.div(pivot_age.sum(axis=1), axis=0) * 100  # Normalize to percentages
    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot_age, annot=True, fmt='.1f', cmap='YlOrRd', cbar_kws={'label': 'Percentage (%)'})
    plt.title('Drop-Off Patterns by Age Group (%)')
    plt.xlabel('Age Group')
    plt.ylabel('Stage')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "drop_off_age_heatmap.png")
    plt.close()

def generate_insights(df: pd.DataFrame, stage_counts: pd.Series, drop_off_rates: pd.Series, error_df: pd.DataFrame):
    """Generate a business-friendly text summary."""
    logging.info("Generating insights summary")
    max_drop_stage = drop_off_rates.idxmax()
    max_drop_rate = drop_off_rates.max() * 100
    total_users = stage_counts[0]
    
    with open(OUTPUT_DIR / "insights.txt", "w") as f:
        f.write("Funnel Drop-Off Insights\n")
        f.write("====================\n")
        f.write(f"Total Users Started: {int(total_users)}\n")
        f.write(f"Biggest Drop-Off: Between {max_drop_stage} and the next stage ({max_drop_rate:.1f}% of users left).\n")
        if not error_df.empty:
            top_error_stage = error_df.loc[error_df['Sessions with Errors'].idxmax()]
            f.write(f"Error Alert: {top_error_stage['Stage']} had {int(top_error_stage['Sessions with Errors'])} users hit errors.\n")
        f.write("\nQuick Tips:\n- Check 'funnel_summary.csv' for the big picture.\n- See 'top_dropoff_urls.csv' for where users are leaving.\n- Look at 'user_segments_chart.png' for who’s dropping off.\n")

def main():
    """Execute the funnel drop-off analysis."""
    funnel_events, sessions = load_data(CONFIG['sessions_file'], CONFIG['funnel_events_file'])
    df, stages = process_sessions(sessions, funnel_events)
    stage_counts, conversion_rates, drop_off_rates = analyze_funnel(df, stages)
    segment_users(df, stages)
    time_spent, error_df, top_events_df, stats_df = analyze_root_causes(df, stages)
    visualize_funnel(stage_counts, conversion_rates, drop_off_rates, stages)
    visualize_root_causes(time_spent, error_df, top_events_df, df, stages)
    generate_insights(df, stage_counts, drop_off_rates, error_df)
    logging.info("Analysis complete. Outputs saved to 'funnel_analysis_output' directory.")

if __name__ == "__main__":
    main()