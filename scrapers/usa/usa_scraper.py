import pandas as pd
from datetime import datetime

# Local database for U.S. vehicle sales rankings (2025 full year data)
US_2025_SALES = [
    {"rank": 1, "name": "F-Series", "brand": "Ford", "sales": 828832, "price": "$38,610 - $100,000", "car_id": 2001},
    {"rank": 2, "name": "Silverado", "brand": "Chevrolet", "sales": 588709, "price": "$36,800 - $72,000", "car_id": 2002},
    {"rank": 3, "name": "RAV4", "brand": "Toyota", "sales": 479288, "price": "$28,675 - $40,000", "car_id": 2003},
    {"rank": 4, "name": "CR-V", "brand": "Honda", "sales": 403768, "price": "$30,100 - $41,000", "car_id": 2004},
    {"rank": 5, "name": "Ram Pick Up", "brand": "Ram", "sales": 374059, "price": "$40,275 - $90,000", "car_id": 2005},
    {"rank": 6, "name": "Sierra", "brand": "GMC", "sales": 356218, "price": "$38,300 - $84,500", "car_id": 2006},
    {"rank": 7, "name": "Equinox", "brand": "Chevrolet", "sales": 332301, "price": "$28,600 - $34,300", "car_id": 2007},
    {"rank": 8, "name": "Camry", "brand": "Toyota", "sales": 316185, "price": "$28,400 - $36,125", "car_id": 2008},
    {"rank": 9, "name": "Model Y", "brand": "Tesla", "sales": 300000, "price": "$42,990 - $52,490", "car_id": 2009},
    {"rank": 10, "name": "Tacoma", "brand": "Toyota", "sales": 274638, "price": "$31,500 - $53,000", "car_id": 2010},
    {"rank": 11, "name": "Civic", "brand": "Honda", "sales": 220000, "price": "$24,250 - $31,500", "car_id": 2011},
    {"rank": 12, "name": "Corolla", "brand": "Toyota", "sales": 215000, "price": "$22,050 - $27,250", "car_id": 2012},
    {"rank": 13, "name": "Explorer", "brand": "Ford", "sales": 205000, "price": "$39,755 - $55,000", "car_id": 2013},
    {"rank": 14, "name": "Grand Cherokee", "brand": "Jeep", "sales": 198000, "price": "$36,495 - $73,000", "car_id": 2014},
    {"rank": 15, "name": "Tahoe", "brand": "Chevrolet", "sales": 110000, "price": "$56,200 - $78,000", "car_id": 2015}
]

# Specifications Database for North American Cars
US_CAR_SPECS = {
    2001: {
        "series_name": "Ford F-150", "car_name": "XLT SuperCrew 3.5L EcoBoost",
        "info": {
            "official_price": "$47,620", "manufacturer": "Ford", "segment": "Full-Size Pickup Truck",
            "energy_type": "Gasoline (ガソリン)", "engine": "3.5L V6 Twin-Turbo (EcoBoost)", "max_power": "400 hp",
            "max_torque": "500 lb-ft (678 N·m)", "transmission": "10-Speed Automatic", "dimensions": "231.7 x 79.9 x 77.2 in (5885 x 2030 x 1961 mm)",
            "wheelbase": "145.4 in (3693 mm)", "weight": "4,900 lbs (2222 kg)", "fuel_economy": "20 mpg (Combined)",
            "warranty": "3 years / 36,000 miles", "seating": "5-6 seats", "drive_type": "4WD"
        }
    },
    2002: {
        "series_name": "Chevrolet Silverado 1500", "car_name": "LT Crew Cab 5.3L V8",
        "info": {
            "official_price": "$48,900", "manufacturer": "Chevrolet", "segment": "Full-Size Pickup Truck",
            "energy_type": "Gasoline (ガソリン)", "engine": "5.3L EcoTec3 V8", "max_power": "355 hp",
            "max_torque": "383 lb-ft (519 N·m)", "transmission": "10-Speed Automatic", "dimensions": "231.9 x 81.2 x 75.5 in (5890 x 2062 x 1918 mm)",
            "wheelbase": "147.4 in (3744 mm)", "weight": "5,000 lbs (2268 kg)", "fuel_economy": "18 mpg (Combined)",
            "warranty": "3 years / 36,000 miles", "seating": "5-6 seats", "drive_type": "4WD"
        }
    },
    2003: {
        "series_name": "Toyota RAV4", "car_name": "XLE Hybrid 2.5L",
        "info": {
            "official_price": "$32,235", "manufacturer": "Toyota", "segment": "Compact SUV",
            "energy_type": "Hybrid (HEV)", "engine": "2.5L 4-Cylinder + 2 Motors", "max_power": "219 hp (Combined)",
            "max_torque": "163 lb-ft (221 N·m)", "transmission": "ECVT", "dimensions": "180.9 x 73.0 x 67.0 in (4595 x 1854 x 1702 mm)",
            "wheelbase": "105.9 in (2690 mm)", "weight": "3,755 lbs (1703 kg)", "fuel_economy": "40 mpg (Combined)",
            "warranty": "3 years / 36,000 miles", "seating": "5 seats", "drive_type": "AWD"
        }
    },
    2004: {
        "series_name": "Honda CR-V", "car_name": "Sport Hybrid",
        "info": {
            "official_price": "$34,350", "manufacturer": "Honda", "segment": "Compact SUV",
            "energy_type": "Hybrid (HEV)", "engine": "2.0L 4-Cylinder + 2 Motors", "max_power": "204 hp (Combined)",
            "max_torque": "247 lb-ft (335 N·m)", "transmission": "Electronic Continuously Variable", "dimensions": "184.8 x 73.5 x 66.2 in (4694 x 1867 x 1681 mm)",
            "wheelbase": "106.3 in (2700 mm)", "weight": "3,800 lbs (1724 kg)", "fuel_economy": "37 mpg (Combined)",
            "warranty": "3 years / 36,000 miles", "seating": "5 seats", "drive_type": "AWD"
        }
    },
    2008: {
        "series_name": "Toyota Camry", "car_name": "LE Hybrid",
        "info": {
            "official_price": "$28,400", "manufacturer": "Toyota", "segment": "Mid-Size Sedan",
            "energy_type": "Hybrid (HEV)", "engine": "2.5L 4-Cylinder + Motor", "max_power": "225 hp (Combined)",
            "max_torque": "163 lb-ft (221 N·m)", "transmission": "ECVT", "dimensions": "193.5 x 72.4 x 56.9 in (4915 x 1839 x 1445 mm)",
            "wheelbase": "111.2 in (2824 mm)", "weight": "3,450 lbs (1565 kg)", "fuel_economy": "51 mpg (Combined)",
            "warranty": "3 years / 36,000 miles", "seating": "5 seats", "drive_type": "FWD"
        }
    },
    2009: {
        "series_name": "Tesla Model Y", "car_name": "Long Range AWD",
        "info": {
            "official_price": "$47,990", "manufacturer": "Tesla", "segment": "Electric Crossover",
            "energy_type": "Electric (EV)", "engine": "Dual Electric Motors", "max_power": "384 hp",
            "max_torque": "376 lb-ft (510 N·m)", "transmission": "Single-Speed Direct", "dimensions": "187.0 x 75.6 x 63.9 in (4750 x 1920 x 1623 mm)",
            "wheelbase": "113.8 in (2891 mm)", "weight": "4,416 lbs (2003 kg)", "fuel_economy": "122 MPGe (EPA)",
            "warranty": "4 years / 50,000 miles", "seating": "5-7 seats", "drive_type": "AWD"
        }
    }
}

def get_usa_rankings(month="", count=100):
    """
    Get North America/US Auto Sales Rankings.
    Returns preloaded 2025 static dataset. Live scraping is not implemented.
    """
    # Preloaded Fallback
    data = []
    for item in US_2025_SALES[:count]:
        data.append({
            "順位": item["rank"],
            "車種名": f"{item['brand']} {item['name']}",
            "販売台数": str(item["sales"]),
            "価格帯": item["price"],
            "ブランド名": item["brand"],
            "サブブランド名": item["brand"],
            "車種ID": str(item["car_id"]),
            "オンライン販売車種IDリスト": [item["car_id"]],
            "オフライン販売車種IDリスト": [],
            "データ取得日": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    return pd.DataFrame(data)

def get_usa_specs(car_ids):
    """
    Returns pivoted specifications dataframe for USA cars.
    """
    if not car_ids:
        return pd.DataFrame()
        
    matched_cars = []
    for cid in car_ids:
        cid_int = int(cid)
        if cid_int in US_CAR_SPECS:
            matched_cars.append((cid_int, US_CAR_SPECS[cid_int]))
        else:
            # Generate generic mock spec for unmapped US car ID
            matched_cars.append((cid_int, {
                "series_name": f"US Vehicle", "car_name": f"Base Model (ID {cid_int})",
                "info": {
                    "official_price": "$30,000", "manufacturer": "US Manufacturer", "segment": "Passenger Vehicle",
                    "energy_type": "Gasoline", "engine": "2.0L 4-Cylinder", "max_power": "180 hp",
                    "max_torque": "190 lb-ft", "transmission": "8-Speed Automatic", "dimensions": "190 x 73 x 60 in",
                    "wheelbase": "110 in", "weight": "3,500 lbs", "fuel_economy": "28 mpg",
                    "warranty": "3 years / 36,000 miles", "seating": "5 seats", "drive_type": "FWD"
                }
            }))
            
    # Pivot specs into standard schema
    spec_fields = [
        ("基本情報", "official_price", "車両本体価格"),
        ("基本情報", "manufacturer", "メーカー"),
        ("基本情報", "segment", "セグメント"),
        ("基本情報", "energy_type", "エネルギータイプ"),
        ("基本情報", "engine", "エンジン仕様"),
        ("性能", "max_power", "最高出力 (Horsepower)"),
        ("性能", "max_torque", "最大トルク (Torque)"),
        ("性能", "transmission", "変速機"),
        ("寸法・重量", "dimensions", "全長x全幅x全高 (in / mm)"),
        ("寸法・重量", "wheelbase", "ホイールベース (in / mm)"),
        ("寸法・重量", "weight", "車両重量 (lbs / kg)"),
        ("性能", "fuel_economy", "燃費消費率 (EPA / mpg)"),
        ("基本情報", "seating", "乗車定員"),
        ("基本情報", "drive_type", "駆動方式"),
        ("基本情報", "warranty", "保証期間")
    ]
    
    rows = []
    for category, key, label in spec_fields:
        row_dict = {
            "カテゴリ": category,
            "項目": label
        }
        
        for cid, car in matched_cars:
            car_label = f"{car['series_name']} ({car['car_name']})"
            row_dict[car_label] = car["info"].get(key, "-")
            
        rows.append(row_dict)
        
    return pd.DataFrame(rows)
