from scrapers.china.dongchedi_wrapper import get_china_rankings, get_china_specs
from scrapers.japan.jada_scraper import get_japan_rankings, get_japan_specs
from scrapers.usa.usa_scraper import get_usa_rankings, get_usa_specs

def get_market_rankings(market="中国", month="", energy_type="", series_type="", count=100):
    """
    Unified interface to get car sales rankings for China, Japan, or USA.
    """
    if market == "中国":
        return get_china_rankings(month, energy_type, series_type, count)
    elif market == "日本":
        return get_japan_rankings(month, count)
    elif market == "北米":
        return get_usa_rankings(month, count)
    else:
        raise ValueError(f"Unknown market type: {market}")

def get_market_specs(market="中国", car_ids=None):
    """
    Unified interface to compare specifications by car/trim IDs for China, Japan, or USA.
    """
    if not car_ids:
        return None
        
    if market == "中国":
        return get_china_specs(car_ids)
    elif market == "日本":
        return get_japan_specs(car_ids)
    elif market == "北米":
        return get_usa_specs(car_ids)
    else:
        raise ValueError(f"Unknown market type: {market}")
