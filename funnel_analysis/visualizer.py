import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import logging
import dask.dataframe as dd
from .config import OUTPUT_DIR, CONFIG

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
    sns.barplot(x=stages, y=stage_counts, palette="Blues_d", order=stages)
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
    sns.barplot(x=stages[1:], y=drop_off_rates[1:] * 100, palette="Reds_d", order=stages[1:])
    plt.title('Where Are We Losing Users? (%)')
    plt.xlabel('Stage Transition')
    plt.ylabel('Drop-Off Rate (%)')
    for i, v in enumerate(drop_off_rates[1:] * 100):
        plt.text(i, v + 1, f"{v:.1f}%", ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "drop_off_rates.png")
    plt.close()

    # Cumulative Drop-Off Line Plot
    cumulative_drop = (1 - conversion_rates) * 100
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=stages, y=cumulative_drop, marker='o', color='purple')
    plt.title('Cumulative Drop-Off Across Stages (%)')
    plt.xlabel('Stage')
    plt.ylabel('Cumulative Drop-Off Rate (%)')
    for i, v in enumerate(cumulative_drop):
        plt.text(i, v + 1, f"{v:.1f}%", ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "cumulative_drop_off.png")
    plt.close()

def visualize_root_causes(time_spent: pd.Series, error_df: pd.DataFrame, top_events_df: pd.DataFrame, df: pd.DataFrame, stages: list):
    """Visualize root cause analysis with additional charts."""
    logging.info("Generating root cause visualizations")
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=stages, y=time_spent.reindex(stages), palette="Greens_d", order=stages)
    plt.title('Average Time Spent Before Reaching Each Stage (s)')
    plt.xlabel('Stage')
    plt.ylabel('Time (seconds)')
    for i, v in enumerate(time_spent.reindex(stages)):
        plt.text(i, v + 1, f"{v:.1f}", ha='center', va='bottom')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "time_spent_per_stage.png")
    plt.close()

    if not error_df.empty:
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Stage', y='Sessions with Errors', data=error_df, palette="Reds_d", order=stages)
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
    sns.barplot(x='Stage', y='User Count', hue='Event', data=top_events_df, palette="viridis", order=stages)
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
    sns.boxplot(x='stage', y='time_to_stage', data=df, palette="Pastel1", order=stages)
    plt.title('Time to Reach Each Stage (s) - Distribution')
    plt.xlabel('Stage')
    plt.ylabel('Time (seconds)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "time_to_stage_boxplot.png")
    plt.close()

    if isinstance(df, dd.DataFrame):
        df = df.compute()

    df['Age Group'] = pd.cut(df['age'], bins=[0, 18, 35, 50, 100], labels=['0-18', '19-35', '36-50', '51+'])
    df['stage'] = pd.Categorical(df['stage'], categories=stages, ordered=True)
    
    pivot_gender = df.pivot_table(index='stage', columns='gender', values='session_id', aggfunc='nunique', fill_value=0, observed=False)
    pivot_gender = pivot_gender.div(pivot_gender.sum(axis=1), axis=0) * 100  # Normalize to percentages
    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot_gender, annot=True, fmt='.1f', cmap='YlOrRd', cbar_kws={'label': 'Percentage (%)'})
    plt.title('Drop-Off Patterns by Gender (%)')
    plt.xlabel('Gender')
    plt.ylabel('Stage')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "drop_off_gender_heatmap.png")
    plt.close()

    pivot_age = df.pivot_table(index='stage', columns='Age Group', values='session_id', aggfunc='nunique', fill_value=0, observed=False)
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
        f.write("\nQuick Tips:\n- Check 'funnel_summary.csv' for the big picture.\n- See 'top_dropoff_urls.csv' for where users are leaving (top 50 URLs).\n- Look at 'drop_off_gender_heatmap.png' and 'drop_off_age_heatmap.png' for demographic trends.\n- Review 'user_segments_chart.png' to see who’s dropping off.\n")