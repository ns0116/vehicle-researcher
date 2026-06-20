# Web_Scraping Project

各自動車データソースのスクレイパー集。

## 構造

```
Web_Scraping/
├── autohome/
│   ├── production/
│   │   ├── spec_scraper_multi_hdf.py  # メインスクレイパー（HDF5出力）
│   │   └── read_hdf.py                # HDF5読み込みユーティリティ
│   ├── archive/
│   │   ├── spec_scraper.py            # 旧CSV版
│   │   ├── spec_scraper_multi.py      # 旧マルチシリーズCSV版
│   │   ├── spec_scraper_multi_test.py # テスト版
│   │   ├── spec_scraper_multi_pkl.py  # 旧Pickle版
│   │   └── read_pkl.py                # Pickle読み込みユーティリティ
│   ├── trash/                         # 廃棄済みファイル
│   └── all_series_car_specs.h5        # 出力データ（HDF5）
└── dongchedi/
    ├── production/
    │   └── ranking_scraper.py         # 販売台数ランキングスクレイパー
    └── car_sales_ranking.csv          # 出力データ
```

## 実行方法

各スクリプトはファイルの場所基準でパスを解決するため、どのディレクトリからでも実行可能。

```bash
# autohome スペックデータ取得
python autohome/production/spec_scraper_multi_hdf.py

# dongchedi 販売ランキング取得
python dongchedi/production/ranking_scraper.py
```
