import pytest
import pandas as pd
from scrapers.usa.usa_scraper import (
    get_usa_rankings,
    get_usa_specs,
    US_2025_SALES,
    US_CAR_SPECS,
)


# --- get_usa_rankings ---

def test_rankings_returns_dataframe():
    df = get_usa_rankings()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_rankings_count_limit():
    df = get_usa_rankings(count=5)
    assert len(df) == 5


def test_rankings_required_columns():
    df = get_usa_rankings()
    for col in ["順位", "車種名", "販売台数", "ブランド名", "車種ID"]:
        assert col in df.columns


def test_rankings_static_data_integrity():
    """静的データのランキング順位が連番であること。"""
    df = get_usa_rankings()
    ranks = df["順位"].tolist()
    assert ranks == sorted(ranks)
    assert ranks[0] == 1


# --- get_usa_specs ---

def test_specs_known_ids():
    df = get_usa_specs([2001, 2003])
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "カテゴリ" in df.columns
    assert "項目" in df.columns


def test_specs_unknown_id_returns_mock():
    df = get_usa_specs([9999])
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_specs_empty_ids():
    df = get_usa_specs([])
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_specs_all_ranking_ids_covered():
    """すべての US ランキング car_id に対してスペックが取得できること（モックを含む）。"""
    all_ids = [item["car_id"] for item in US_2025_SALES]
    df = get_usa_specs(all_ids)
    assert not df.empty
    assert len(df.columns) >= 2 + len(all_ids)


def test_specs_known_ids_have_real_data():
    """US_CAR_SPECS に登録済みの ID は実データが返ること。"""
    known_ids = list(US_CAR_SPECS.keys())
    df = get_usa_specs(known_ids)
    assert not df.empty
    price_row = df[df["項目"] == "車両本体価格"]
    assert not price_row.empty
    for col in df.columns[2:]:
        assert price_row.iloc[0][col] != "-"


# --- データ整合性チェック ---

def test_ranking_and_spec_ids_consistent():
    """ランキングに登場するすべての car_id が US_CAR_SPECS に存在すること。"""
    ranking_ids = {item["car_id"] for item in US_2025_SALES}
    spec_ids = set(US_CAR_SPECS.keys())
    missing = ranking_ids - spec_ids
    assert missing == set(), f"スペックDBに未登録のランキングID: {missing}"
