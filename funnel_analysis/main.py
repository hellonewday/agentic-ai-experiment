from .data_loader import load_data
from .processor import process_sessions
from .analyzer import analyze_funnel, segment_users, analyze_root_causes
from .visualizer import visualize_funnel, visualize_root_causes, generate_insights
from .config import CONFIG

def main():
    """Execute the funnel drop-off analysis."""
    funnel_events, sessions = load_data(CONFIG['sessions_file'], CONFIG['funnel_events_file'])
    df, stages = process_sessions(sessions, funnel_events, CONFIG['dask_threshold'])
    stage_counts, conversion_rates, drop_off_rates = analyze_funnel(df, stages)
    segment_users(df, stages)
    time_spent, error_df, top_events_df, stats_df = analyze_root_causes(df, stages)
    visualize_funnel(stage_counts, conversion_rates, drop_off_rates, stages)
    visualize_root_causes(time_spent, error_df, top_events_df, df, stages)
    generate_insights(df, stage_counts, drop_off_rates, error_df)

if __name__ == "__main__":
    main()