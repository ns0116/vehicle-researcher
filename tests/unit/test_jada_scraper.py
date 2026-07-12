import pytest
import pandas as pd
from scrapers.japan.jada_scraper import (
    get_japan_rankings,
    get_japan_specs,
    get_fallback_rankings,
    get_available_months,
    JADA_RANKINGS,
    JAPAN_CAR_SPECS,
)


# --- get_available_months ---

def test_available_months_returns_list():
    months = get_available_months()
    assert isinstance(months, list)
    assert len(months) >= 2


def test_available_months_descending():
    months = get_available_months()
    assert months == sorted(months, reverse=True)


# --- get_japan_rankings ---

def test_rankings_known_month():
    df, is_estimated = get_japan_rankings(month="202605")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert is_estimated is False


def test_rankings_unknown_month_is_estimated():
    df, is_estimated = get_japan_rankings(month="202001")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert is_estimated is True


def test_rankings_count_limit():
    df, _ = get_japan_rankings(month="202605", count=3)
    assert len(df) == 3


def test_rankings_required_columns():
    df, _ = get_japan_rankings(month="202605")
    for col in ["順位", "車種名", "販売台数", "ブランド名", "車種ID"]:
        assert col in df.columns


# --- get_fallback_rankings ---

def test_fallback_has_same_length_as_base():
    result = get_fallback_rankings("202001")
    assert len(result) == len(JADA_RANKINGS["202605"])


def test_fallback_sales_within_range():
    result = get_fallback_rankings("202001")
    for item in result:
        base_sales = next(b["sales"] for b in JADA_RANKINGS["202605"] if b["car_id"] == item["car_id"])
        assert item["sales"] >= base_sales * 0.85
        assert item["sales"] <= base_sales * 1.15


# --- get_japan_specs ---

def test_specs_known_ids():
    df = get_japan_specs([1001, 1002])
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "カテゴリ" in df.columns
    assert "項目" in df.columns


def test_specs_unknown_id_returns_mock():
    df = get_japan_specs([9999])
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_specs_empty_ids():
    df = get_japan_specs([])
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_specs_all_ranking_ids_covered():
    """すべてのランキング car_id に対してスペックが取得できること（モックを含む）。"""
    all_ids = [item["car_id"] for item in JADA_RANKINGS["202605"]]
    df = get_japan_specs(all_ids)
    assert not df.empty
    # 列数 = カテゴリ + 項目 + 各車両列
    assert len(df.columns) >= 2 + len(all_ids)


def test_specs_known_ids_have_real_data():
    """JAPAN_CAR_SPECS に登録済みの ID は実データが返ること。"""
    known_ids = list(JAPAN_CAR_SPECS.keys())
    df = get_japan_specs(known_ids)
    assert not df.empty
    # 少なくとも価格が空欄でないことを確認
    price_row = df[df["項目"] == "車両本体価格"]
    assert not price_row.empty
    for col in df.columns[2:]:
        assert price_row.iloc[0][col] != "-"
