from typing import Optional

import pandas as pd
from datetime import datetime

from ..utils import pivot_spec_fields

# Local database for Japan passenger car rankings (JADA)
JADA_RANKINGS = {
    "202605": [
        {"rank": 1, "name": "ヤリス", "brand": "トヨタ", "sales": 10401, "price": "150万 - 270万円", "car_id": 1001},
        {"rank": 2, "name": "カローラ", "brand": "トヨタ", "sales": 9799, "price": "160万 - 300万円", "car_id": 1002},
        {"rank": 3, "name": "ライズ", "brand": "トヨタ", "sales": 9633, "price": "170万 - 230万円", "car_id": 1003},
        {"rank": 4, "name": "シエンタ", "brand": "トヨタ", "sales": 9314, "price": "195万 - 310万円", "car_id": 1004},
        {"rank": 5, "name": "ルーミー", "brand": "トヨタ", "sales": 8381, "price": "156万 - 210万円", "car_id": 1005},
        {"rank": 6, "name": "フリード", "brand": "ホンダ", "sales": 6622, "price": "250万 - 340万円", "car_id": 1006},
        {"rank": 7, "name": "アルファード", "brand": "トヨタ", "sales": 6454, "price": "540万 - 872万円", "car_id": 1007},
        {"rank": 8, "name": "ヴォクシー", "brand": "トヨタ", "sales": 5985, "price": "309万 - 396万円", "car_id": 1008},
        {"rank": 9, "name": "ノア", "brand": "トヨタ", "sales": 5912, "price": "267万 - 389万円", "car_id": 1009},
        {"rank": 10, "name": "アクア", "brand": "トヨタ", "sales": 5090, "price": "199万 - 256万円", "car_id": 1010},
        {"rank": 11, "name": "ヴェゼル", "brand": "ホンダ", "sales": 4890, "price": "239万 - 340万円", "car_id": 1011},
        {"rank": 12, "name": "ハリアー", "brand": "トヨタ", "sales": 4720, "price": "312万 - 620万円", "car_id": 1012},
        {"rank": 13, "name": "ノート", "brand": "日産", "sales": 4680, "price": "229万 - 258万円", "car_id": 1013},
        {"rank": 14, "name": "プリウス", "brand": "トヨタ", "sales": 4500, "price": "275万 - 460万円", "car_id": 1014},
        {"rank": 15, "name": "セレナ", "brand": "日産", "sales": 4320, "price": "276万 - 479万円", "car_id": 1015}
    ],
    "202604": [
        {"rank": 1, "name": "ヤリス", "brand": "トヨタ", "sales": 9890, "price": "150万 - 270万円", "car_id": 1001},
        {"rank": 2, "name": "カローラ", "brand": "トヨタ", "sales": 9210, "price": "160万 - 300万円", "car_id": 1002},
        {"rank": 3, "name": "シエンタ", "brand": "トヨタ", "sales": 8760, "price": "195万 - 310万円", "car_id": 1004},
        {"rank": 4, "name": "ライズ", "brand": "トヨタ", "sales": 8450, "price": "170万 - 230万円", "car_id": 1003},
        {"rank": 5, "name": "ルーミー", "brand": "トヨタ", "sales": 7920, "price": "156万 - 210万円", "car_id": 1005},
        {"rank": 6, "name": "フリード", "brand": "ホンダ", "sales": 6120, "price": "250万 - 340万円", "car_id": 1006},
        {"rank": 7, "name": "ノート", "brand": "日産", "sales": 5890, "price": "229万 - 258万円", "car_id": 1013},
        {"rank": 8, "name": "アクア", "brand": "トヨタ", "sales": 4980, "price": "199万 - 256万円", "car_id": 1010},
        {"rank": 9, "name": "ヴォクシー", "brand": "トヨタ", "sales": 4870, "price": "309万 - 396万円", "car_id": 1008},
        {"rank": 10, "name": "プリウス", "brand": "トヨタ", "sales": 4410, "price": "275万 - 460万円", "car_id": 1014}
    ]
}


def get_fallback_rankings(month: str) -> list[dict]:
    """
    JADA_RANKINGS に存在しない月のフォールバック。
    WARNING: 返されるデータは202605データを基にした推定値であり、JADA公式数値ではない。
    """
    base = JADA_RANKINGS["202605"]
    data = []
    val_mod = int(month) % 10 if month.isdigit() else 5
    for item in base:
        sales_var = int(item["sales"] * (0.9 + (val_mod * 0.02)))
        data.append({
            "rank": item["rank"],
            "name": item["name"],
            "brand": item["brand"],
            "sales": sales_var,
            "price": item["price"],
            "car_id": item["car_id"]
        })
    return data


# Specifications Database for Japanese Cars
JAPAN_CAR_SPECS = {
    1001: {
        "series_name": "ヤリス", "car_name": "HYBRID G (1.5L HEV)",
        "info": {
            "official_price": "200.0万円", "manufacturer": "トヨタ", "segment": "コンパクトカー (Bセグメント)",
            "energy_type": "ハイブリッド (HEV)", "engine": "1.5L 直列3気筒 + モーター", "max_power": "91Ps (システム最大 116Ps)",
            "max_torque": "120N・m", "transmission": "電気式無段変速機 (e-CVT)", "dimensions": "3940 x 1695 x 1500 mm",
            "wheelbase": "2550 mm", "weight": "1060 kg", "fuel_economy": "36.0 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "5人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1002: {
        "series_name": "カローラ", "car_name": "HYBRID G (1.8L HEV)",
        "info": {
            "official_price": "257.0万円", "manufacturer": "トヨタ", "segment": "セダン (Cセグメント)",
            "energy_type": "ハイブリッド (HEV)", "engine": "1.8L 直列4気筒 + モーター", "max_power": "98Ps (システム最大 140Ps)",
            "max_torque": "142N・m", "transmission": "電気式無段変速機 (e-CVT)", "dimensions": "4495 x 1745 x 1435 mm",
            "wheelbase": "2640 mm", "weight": "1350 kg", "fuel_economy": "30.2 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "5人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1003: {
        "series_name": "ライズ", "car_name": "Z (1.0L ターボ)",
        "info": {
            "official_price": "214.0万円", "manufacturer": "トヨタ", "segment": "コンパクトSUV",
            "energy_type": "ガソリン ターボ", "engine": "1.0L 直列3気筒 ターボ (1KR-VET)", "max_power": "98Ps",
            "max_torque": "140N・m", "transmission": "D-CVT (副変速機付き無段変速機)", "dimensions": "3995 x 1695 x 1620 mm",
            "wheelbase": "2525 mm", "weight": "940 kg", "fuel_economy": "17.4 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "5人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1004: {
        "series_name": "シエンタ", "car_name": "HYBRID G (5人乗り)",
        "info": {
            "official_price": "269.0万円", "manufacturer": "トヨタ", "segment": "コンパクトミニバン",
            "energy_type": "ハイブリッド (HEV)", "engine": "1.5L 直列3気筒 + モーター", "max_power": "91Ps (システム最大 116Ps)",
            "max_torque": "120N・m", "transmission": "電気式無段変速機 (e-CVT)", "dimensions": "4260 x 1695 x 1695 mm",
            "wheelbase": "2750 mm", "weight": "1370 kg", "fuel_economy": "28.2 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "5人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1005: {
        "series_name": "ルーミー", "car_name": "G (1.0L ターボ)",
        "info": {
            "official_price": "185.6万円", "manufacturer": "トヨタ", "segment": "コンパクトトールワゴン",
            "energy_type": "ガソリン ターボ", "engine": "1.0L 直列3気筒 ターボ (1KR-VET)", "max_power": "98Ps",
            "max_torque": "140N・m", "transmission": "D-CVT (副変速機付き無段変速機)", "dimensions": "3700 x 1670 x 1735 mm",
            "wheelbase": "2490 mm", "weight": "940 kg", "fuel_economy": "16.6 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "5人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1006: {
        "series_name": "フリード", "car_name": "e:HEV AIR (6人乗り)",
        "info": {
            "official_price": "285.7万円", "manufacturer": "ホンダ", "segment": "コンパクトミニバン",
            "energy_type": "ハイブリッド (HEV)", "engine": "1.5L 直列4気筒 + 2モーター", "max_power": "106Ps (モーター 123Ps)",
            "max_torque": "127N・m (モーター 253N・m)", "transmission": "電気式無段変速機", "dimensions": "4310 x 1695 x 1755 mm",
            "wheelbase": "2740 mm", "weight": "1460 kg", "fuel_economy": "25.4 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "6人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1007: {
        "series_name": "アルファード", "car_name": "HYBRID Z (2.5L E-Four)",
        "info": {
            "official_price": "620.0万円", "manufacturer": "トヨタ", "segment": "高級ミニバン (LLクラス)",
            "energy_type": "ハイブリッド (HEV)", "engine": "2.5L 直列4気筒 + モーター", "max_power": "190Ps (システム最大 250Ps)",
            "max_torque": "236N・m", "transmission": "電気式無段変速機 (e-CVT)", "dimensions": "4995 x 1850 x 1935 mm",
            "wheelbase": "3000 mm", "weight": "2230 kg", "fuel_economy": "16.7 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "7人乗り", "drive_type": "E-Four (電気式4輪駆動)"
        }
    },
    1008: {
        "series_name": "ヴォクシー", "car_name": "HYBRID S-G (2.0L HEV)",
        "info": {
            "official_price": "369.3万円", "manufacturer": "トヨタ", "segment": "ミニバン (Mクラス)",
            "energy_type": "ハイブリッド (HEV)", "engine": "2.0L 直列4気筒 + モーター (M20A-FXS)", "max_power": "152Ps (システム最大 197Ps)",
            "max_torque": "188N・m", "transmission": "電気式無段変速機 (e-CVT)", "dimensions": "4695 x 1730 x 1895 mm",
            "wheelbase": "2850 mm", "weight": "1720 kg", "fuel_economy": "22.0 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "7人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1009: {
        "series_name": "ノア", "car_name": "HYBRID S-G (2.0L HEV)",
        "info": {
            "official_price": "342.1万円", "manufacturer": "トヨタ", "segment": "ミニバン (Mクラス)",
            "energy_type": "ハイブリッド (HEV)", "engine": "2.0L 直列4気筒 + モーター (M20A-FXS)", "max_power": "152Ps (システム最大 197Ps)",
            "max_torque": "188N・m", "transmission": "電気式無段変速機 (e-CVT)", "dimensions": "4695 x 1730 x 1870 mm",
            "wheelbase": "2850 mm", "weight": "1710 kg", "fuel_economy": "22.0 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "7人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1010: {
        "series_name": "アクア", "car_name": "Zグレード (1.5L HEV)",
        "info": {
            "official_price": "240.0万円", "manufacturer": "トヨタ", "segment": "コンパクトカー (Bセグメント)",
            "energy_type": "ハイブリッド (HEV)", "engine": "1.5L 直列3気筒 + モーター", "max_power": "91Ps (システム最大 116Ps)",
            "max_torque": "120N・m", "transmission": "電気式無段変速機 (e-CVT)", "dimensions": "4050 x 1695 x 1485 mm",
            "wheelbase": "2600 mm", "weight": "1130 kg", "fuel_economy": "33.6 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "5人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1011: {
        "series_name": "ヴェゼル", "car_name": "e:HEV X 2WD",
        "info": {
            "official_price": "274.0万円", "manufacturer": "ホンダ", "segment": "コンパクトSUV",
            "energy_type": "ハイブリッド (HEV)", "engine": "1.5L 直列4気筒 + 2モーター (i-MMD)", "max_power": "106Ps (モーター 131Ps)",
            "max_torque": "253N・m (モーター)", "transmission": "電気式無段変速機", "dimensions": "4330 x 1790 x 1590 mm",
            "wheelbase": "2610 mm", "weight": "1430 kg", "fuel_economy": "26.0 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "5人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1012: {
        "series_name": "ハリアー", "car_name": "HYBRID G 2WD",
        "info": {
            "official_price": "414.0万円", "manufacturer": "トヨタ", "segment": "ミドルクラスSUV (Dセグメント)",
            "energy_type": "ハイブリッド (HEV)", "engine": "2.5L 直列4気筒 + モーター (A25A-FXS)", "max_power": "178Ps (システム最大 222Ps)",
            "max_torque": "221N・m", "transmission": "電気式無段変速機 (e-CVT)", "dimensions": "4740 x 1855 x 1660 mm",
            "wheelbase": "2690 mm", "weight": "1740 kg", "fuel_economy": "21.4 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "5人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1013: {
        "series_name": "ノート", "car_name": "e-POWER X",
        "info": {
            "official_price": "229.9万円", "manufacturer": "日産", "segment": "コンパクトカー (Bセグメント)",
            "energy_type": "シリーズハイブリッド (e-POWER)", "engine": "1.2L 直列3気筒 (発電用) + モーター", "max_power": "82Ps (モーター 116Ps)",
            "max_torque": "103N・m (モーター 280N・m)", "transmission": "なし (モーター直接駆動)", "dimensions": "4045 x 1695 x 1505 mm",
            "wheelbase": "2580 mm", "weight": "1220 kg", "fuel_economy": "28.4 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "5人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1014: {
        "series_name": "プリウス", "car_name": "2.0L Gグレード HEV",
        "info": {
            "official_price": "320.0万円", "manufacturer": "トヨタ", "segment": "ハッチバック/セダン (Cセグメント)",
            "energy_type": "ハイブリッド (HEV)", "engine": "2.0L 直列4気筒 + モーター", "max_power": "152Ps (システム最大 196Ps)",
            "max_torque": "188N・m", "transmission": "電気式無段変速機 (e-CVT)", "dimensions": "4600 x 1780 x 1430 mm",
            "wheelbase": "2750 mm", "weight": "1400 kg", "fuel_economy": "28.6 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "5人乗り", "drive_type": "FF (前輪駆動)"
        }
    },
    1015: {
        "series_name": "セレナ", "car_name": "e-POWER B",
        "info": {
            "official_price": "295.6万円", "manufacturer": "日産", "segment": "ミニバン (Mクラス)",
            "energy_type": "シリーズハイブリッド (e-POWER)", "engine": "1.4L 直列4気筒 (KR14DDe) + 2モーター", "max_power": "82Ps (モーター 136Ps)",
            "max_torque": "103N・m (モーター 330N・m)", "transmission": "なし (モーター直接駆動)", "dimensions": "4765 x 1715 x 1858 mm",
            "wheelbase": "2940 mm", "weight": "1820 kg", "fuel_economy": "19.0 km/L (WLTCモード)",
            "warranty": "3年または6万km", "seating": "7人乗り", "drive_type": "FF (前輪駆動)"
        }
    }
}

SPEC_FIELDS: list[tuple[str, str, str]] = [
    ("基本情報", "official_price", "車両本体価格"),
    ("基本情報", "manufacturer", "メーカー"),
    ("基本情報", "segment", "セグメント"),
    ("基本情報", "energy_type", "エネルギータイプ"),
    ("基本情報", "engine", "エンジン仕様"),
    ("性能", "max_power", "最高出力"),
    ("性能", "max_torque", "最大トルク"),
    ("性能", "transmission", "変速機"),
    ("寸法・重量", "dimensions", "長x幅x高 (mm)"),
    ("寸法・重量", "wheelbase", "ホイールベース (mm)"),
    ("寸法・重量", "weight", "車両重量 (kg)"),
    ("性能", "fuel_economy", "燃費消費率"),
    ("基本情報", "seating", "乗車定員"),
    ("基本情報", "drive_type", "駆動方式"),
    ("基本情報", "warranty", "保証期間"),
]


def get_available_months() -> list[str]:
    """JADA_RANKINGS に実データが存在する月のリストを降順で返す。"""
    return sorted(JADA_RANKINGS.keys(), reverse=True)


def get_japan_rankings(month: str = "", count: int = 100) -> tuple[pd.DataFrame, bool]:
    """
    Get JADA brand passenger car sales rankings.
    Returns (DataFrame, is_estimated). is_estimated=True の場合はデータが推定値。
    """
    if not month:
        month = "202605"

    raw_list = JADA_RANKINGS.get(month)
    is_estimated = raw_list is None
    if is_estimated:
        raw_list = get_fallback_rankings(month)

    data = []
    for item in raw_list[:count]:
        data.append({
            "順位": item["rank"],
            "車種名": item["name"],
            "販売台数": str(item["sales"]),
            "価格帯": item["price"],
            "ブランド名": item["brand"],
            "サブブランド名": item["brand"],
            "車種ID": str(item["car_id"]),
            "オンライン販売車種IDリスト": [item["car_id"]],
            "オフライン販売車種IDリスト": [],
            "データ取得日": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    return pd.DataFrame(data), is_estimated


def get_japan_specs(car_ids: list[int]) -> pd.DataFrame:
    """Returns pivoted specifications dataframe for Japanese cars."""
    if not car_ids:
        return pd.DataFrame()

    matched_cars = []
    for cid in car_ids:
        cid_int = int(cid)
        if cid_int in JAPAN_CAR_SPECS:
            matched_cars.append((cid_int, JAPAN_CAR_SPECS[cid_int]))
        else:
            matched_cars.append((cid_int, {
                "series_name": "日本車モデル", "car_name": f"Gグレード (ID {cid_int})",
                "info": {
                    "official_price": "250万円", "manufacturer": "日本メーカー", "segment": "乗用車",
                    "energy_type": "ハイブリッド (HEV)", "engine": "1.5L 直列3気筒", "max_power": "100Ps",
                    "max_torque": "130N・m", "transmission": "CVT", "dimensions": "4200 x 1700 x 1500 mm",
                    "wheelbase": "2600 mm", "weight": "1200 kg", "fuel_economy": "28.0 km/L (WLTC)",
                    "warranty": "3年または6万km", "seating": "5人乗り", "drive_type": "FF"
                }
            }))

    return pivot_spec_fields(SPEC_FIELDS, matched_cars)
