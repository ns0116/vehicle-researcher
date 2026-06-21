import sys
from pathlib import Path

# Add project root to path to ensure proper imports of existing modules
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from _archive.dongchedi.production.ranking_scraper import get_ranking
from _archive.dongchedi.production.spec_scraper import scrape_dongchedi_specs

def get_china_rankings(month="", energy_type="", series_type="", count=100):
    """
    Wrapper for China sales rankings from Dongchedi.
    """
    return get_ranking(
        month=month,
        new_energy_type=energy_type,
        series_type=series_type,
        count=count
    )

def get_china_specs(car_ids):
    """
    Wrapper for China specifications comparison from Dongchedi.
    """
    return scrape_dongchedi_specs(car_ids)
