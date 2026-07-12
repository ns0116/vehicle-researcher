import pytest
import pandas as pd
from scrapers.china.ranking_scraper import parse_ranking_data


VALID_RESPONSE = {
    "status": 0,
    "data": {
        "list": [
            {
                "rank": 1, "series_name": "比亚迪海鸥", "count": 50000,
                "price": "7-10万", "dealer_price": "7-10万",
                "min_price": 7.0, "max_price": 10.0,
                "brand_name": "比亚迪", "sub_brand_name": "比亚迪",
                "image": "https://example.com/img.jpg", "series_pic_count": 10,
                "car_review_count": 100, "series_id": 123, "brand_id": 1,
                "sub_brand_id": 2, "online_car_ids": [456], "offline_car_ids": [],
                "last_rank": 2,
            }
        ],
        "paging": {"has_more": False}
    }
}


def test_parse_ranking_data_valid():
    df = parse_ranking_data(VALID_RESPONSE)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]["順位"] == 1
    assert df.iloc[0]["車種名"] == "比亚迪海鸥"
    assert df.iloc[0]["販売台数"] == 50000


def test_parse_ranking_data_none():
    result = parse_ranking_data(None)
    assert result is None


def test_parse_ranking_data_wrong_status():
    bad = {"status": 1, "data": {"list": []}}
    result = parse_ranking_data(bad)
    assert result is None


def test_parse_ranking_data_empty_list():
    empty = {"status": 0, "data": {"list": []}}
    result = parse_ranking_data(empty)
    assert result is None


def test_parse_ranking_data_columns():
    df = parse_ranking_data(VALID_RESPONSE)
    expected_cols = ["順位", "車種名", "販売台数", "ブランド名", "車種ID"]
    for col in expected_cols:
        assert col in df.columns
