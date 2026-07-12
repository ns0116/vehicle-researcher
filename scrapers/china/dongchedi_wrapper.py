from .ranking_scraper import get_ranking
from .spec_scraper import scrape_dongchedi_specs


def get_china_rankings(month: str = "", energy_type: str = "", series_type: str = "", count: int = 100):
    """Wrapper for China sales rankings from Dongchedi."""
    return get_ranking(
        month=month,
        new_energy_type=energy_type,
        series_type=series_type,
        count=count,
    )


def get_china_specs(car_ids: list[int]):
    """Wrapper for China specifications comparison from Dongchedi."""
    return scrape_dongchedi_specs(car_ids)
