import json
import requests
import pandas as pd
from pathlib import Path

def scrape_autohome_specs(series_ids, output_hdf_path=None):
    """
    指定された series_ids の自動車スペックデータをAutohome APIから取得し、DataFrameを返す。
    output_hdf_path が指定された場合は HDF5 ファイルに書き込む。
    """
    all_title_items = {} # すべての titlelist の item を保存する辞書 (titleid をキーとする)
    all_series_data = {} # すべての seriesid のデータを保存する辞書 (seriesid をキーとする)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    # 事前に titlelist を収集
    for series_id in series_ids:
        api_url = f"https://car-web-api.autohome.com.cn/car/param/getParamConf?mode=1&site=1&seriesid={series_id}"
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data["returncode"] == 0 and data["result"] and data["result"]["titlelist"]:
                all_series_data[series_id] = data["result"] # データを保存
                for group in data["result"]["titlelist"]:
                    for item in group["items"]:
                        all_title_items[item["titleid"]] = item["itemname"] # itemname を辞書に保存 (重複は上書きされる)
            else:
                print(f"APIエラーまたはデータなし (seriesid: {series_id}): {data.get('message', 'Unknown Error')}")
        except requests.exceptions.RequestException as e:
            print(f"APIリクエストエラー (seriesid: {series_id}): {e}")
        except json.JSONDecodeError as e:
            print(f"JSONデコードエラー (seriesid: {series_id}): {e}")
        except Exception as e:
            print(f"予期せぬエラー (seriesid: {series_id}): {e}")

    if not all_series_data:
        print("データが取得できませんでした。")
        return pd.DataFrame()

    # 統合された header_items を生成 (itemid 順にソート)
    sorted_title_ids = sorted(all_title_items.keys())
    integrated_header_items = [all_title_items[title_id] for title_id in sorted_title_ids]

    header_base = ["グレード名", "年代", "航続距離", "価格", "SeriesID"] # SeriesID カラムを追加
    header_colors_exterior = ["外装色" + str(i+1) + "_" + color_key for i in range(11) for color_key in ["名前", "コード", "価格"]]
    header_colors_interior = ["内装色" + str(i+1) + "_" + color_key for i in range(3) for color_key in ["名前", "コード", "価格"]]
    csv_header = header_base + integrated_header_items + header_colors_exterior + header_colors_interior
    unique_csv_header = list(dict.fromkeys(csv_header))  # 順序保持で重複削除

    rows = [] # データ辞書を格納するリスト

    # データ組み立て (すべての seriesid をループ)
    for series_id in series_ids:
        if series_id not in all_series_data: # データがない場合はスキップ
            continue

        result_data = all_series_data[series_id]
        item_dict = {item["titleid"]: item["itemname"] for group in result_data["titlelist"] for item in group["items"]} # 各 seriesid の item_dict を作成

        for spec_data in result_data["datalist"]:
            row_dict = {}
            row_dict["グレード名"] = spec_data.get("specname", "")
            row_dict["年代"] = spec_data["condition"][0] if spec_data.get("condition") else ""
            row_dict["航続距離"] = spec_data["condition"][-1] if spec_data.get("condition") else ""
            row_dict["価格"] = spec_data.get("minprice", 0)
            row_dict["SeriesID"] = series_id

            # paramconflist のマッピング
            for param in spec_data.get("paramconflist", []):
                title_id = param.get("titleid")
                if title_id in item_dict:
                    item_name = item_dict[title_id]
                    row_dict[item_name] = param.get("itemname", "")

            # 外装色
            for color_data in spec_data.get("paramconflist", []):
                if color_data.get("titleid") == 199 and color_data.get("colorinfo") and color_data["colorinfo"].get("type") == 1:
                    for i, color in enumerate(color_data["colorinfo"].get("list", [])):
                        if i < 11:
                            row_dict[f"外装色{i+1}_名前"] = color.get("name", "")
                            row_dict[f"外装色{i+1}_コード"] = color.get("value", "")
                            row_dict[f"外装色{i+1}_価格"] = color.get("price", "")

            # 内装色
            for color_data in spec_data.get("paramconflist", []):
                if color_data.get("titleid") == 200 and color_data.get("colorinfo") and color_data["colorinfo"].get("type") == 2:
                    for i, color in enumerate(color_data["colorinfo"].get("list", [])):
                        if i < 3:
                            row_dict[f"内装色{i+1}_名前"] = color.get("name", "")
                            row_dict[f"内装色{i+1}_コード"] = color.get("value", "")
                            row_dict[f"内装色{i+1}_価格"] = color.get("price", "")

            rows.append(row_dict)

        print(f"SeriesID: {series_id} のデータを DataFrame に追加しました。")

    # DataFrameの作成と列の再配置
    df = pd.DataFrame(rows)
    df = df.reindex(columns=unique_csv_header).fillna("")

    if output_hdf_path:
        try:
            output_hdf_path = Path(output_hdf_path)
            with pd.HDFStore(output_hdf_path, 'w') as hdf: # HDF5 ファイルを書き込みモードでオープン
                hdf.put('car_specs', df, format='fixed') # DataFrame を HDF5 ファイルに書き込み
            print(f"HDF5ファイル '{output_hdf_path}' (統合titlelist, 全SeriesID) が生成されました。")
        except Exception as e:
            print(f"HDF5ファイル書き込みエラー: {e}")

    return df

if __name__ == "__main__":
    # 動作確認用のメイン処理
    series_id_start = 6900
    series_id_end = 6911  # 6910 まで含むように 1 を加算
    series_ids = list(range(series_id_start, series_id_end))
    output_hdf_filename = Path(__file__).parent.parent / "all_series_car_specs.h5"

    df = scrape_autohome_specs(series_ids, output_hdf_filename)
    print(f"取得件数: {len(df)}")
    print("スクレイピング完了")