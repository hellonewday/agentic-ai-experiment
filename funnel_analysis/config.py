from pathlib import Path

# Get the directory of the funnel_analysis package
PACKAGE_DIR = Path(__file__).parent

# Configuration dictionary
CONFIG = {
    'sessions_file': str(PACKAGE_DIR / 'sessions.json'),
    'funnel_events_file': str(PACKAGE_DIR / 'funnel_events.json'),
    'dask_threshold': 100000,
    'stage_order': ['Browsing', 'Adding to Cart', 'Checkout', 'Purchase']
}

# Output directory (still relative to the working directory, but can be adjusted if needed)
OUTPUT_DIR = Path("funnel_analysis_output")
OUTPUT_DIR.mkdir(exist_ok=True)