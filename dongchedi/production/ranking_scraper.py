import requests
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

# 定数の定義
RANK_DATA_TYPE_SALES = 11
OUTPUT_DIR = Path(__file__).parent.parent
CSV_FILENAME = "car_sales_ranking.csv"
API_BASE_URL = "https://www.dongchedi.com/motor/pc/car/rank_data"

def fetch_car_sales_ranking_json(url, params=None): # params引数を追加、デフォルト値はNone
    """
    指定されたURLから自動車販売台数ランキングのJSONデータを取得する。

    Args:
        url (str): APIエンドポイントのURL
        params (dict, optional): URLに付与するクエリパラメータ (デフォルト: None)

    Returns:
        dict: JSONレスポンス (辞書型)。
              リクエスト失敗、JSONデコード失敗時は None を返す。
    """
    try:
        response = requests.get(url, params=params) # requests.get() に params を渡す
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSONデコードエラー: {e}")
        return None

def parse_ranking_data(json_data):
    """
    JSONデータから自動車販売台数ランキング情報を解析し、Pandas DataFrameを作成する。
    """
    if json_data is None or json_data.get('status') != 0:
        print("有効なJSONデータがありません。statusコードを確認してください。")
        return None

    ranking_list = json_data.get('data', {}).get('list', [])
    if not ranking_list:
        print("ランキングデータが見つかりませんでした。'data.list' が空です。")
        return None

    data = []
    for item in ranking_list:
        data.append({
            "順位": item.get('rank'),
            "車種名": item.get('series_name'),
            "販売台数": item.get('count'),
            "価格帯": item.get('price'),
            "ディーラー価格帯": item.get('dealer_price'),
            "最低価格": item.get('min_price'),
            "最高価格": item.get('max_price'),
            "ブランド名": item.get('brand_name'),
            "サブブランド名": item.get('sub_brand_name'),
            "車種イメージURL": item.get('image'),
            "画像数": item.get('series_pic_count'),
            "レビュー数": item.get('car_review_count'),
            "車種ID": item.get('series_id'),
            "ブランドID": item.get('brand_id'),
            "サブブランドID": item.get('sub_brand_id'),
            "オンライン販売車種IDリスト": item.get('online_car_ids'),
            "オフライン販売車種IDリスト": item.get('offline_car_ids'),
            "前回の順位": item.get('last_rank'),
            "データ取得日": datetime.now().strftime('%Y-%m-%d %H:%M:%S') # データフレームに列を追加
        })

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_filepath = OUTPUT_DIR / CSV_FILENAME

    # API URLを組み立て
    params = {
        "aid": 1839,
        "app_name": "auto_web_pc",
        "city_name": "%E5%8C%97%E4%BA%AC",
        "count": 5000, # count は一旦小さくしておく (ページング未実装のため)
        "offset": "",
        "month": "",
        "new_energy_type": "",
        "rank_data_type": RANK_DATA_TYPE_SALES,
        "brand_id": "",
        "price": "",
        "manufacturer": "",
        "series_type": "",
        "nation": 0
    }
    car_sales_ranking_api_url = API_BASE_URL
    json_response = fetch_car_sales_ranking_json(car_sales_ranking_api_url, params=params) # params を渡す
    ranking_df = parse_ranking_data(json_response)

    if ranking_df is not None:
        ranking_df.to_csv(csv_filepath, index=False, encoding="utf-8-sig")
        print(f"自動車販売台数ランキングをCSVファイル '{csv_filepath}' に出力しました。")
        print("\n**備考:**")
        print(f"* データ取得日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"* ランキングタイプ: 指定されたURLのパラメータに基づいています (rank_data_type={RANK_DATA_TYPE_SALES})")
        print("* データはAPIから取得した時点のものです。")
    else:
        print("ランキングデータの取得に失敗しました。")