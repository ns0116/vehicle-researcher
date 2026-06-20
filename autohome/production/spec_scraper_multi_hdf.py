import json
import requests
import pandas as pd
from pathlib import Path

# seriesid の範囲
series_id_start = 6900
series_id_end = 6911  # 6910 まで含むように 1 を加算

output_hdf_filename = Path(__file__).parent.parent / "all_series_car_specs.h5"

all_title_items = {} # すべての titlelist の item を保存する辞書 (titleid をキーとする)
all_series_data = {} # すべての seriesid のデータを保存する辞書 (seriesid をキーとする)

# 事前に titlelist を収集
for series_id in range(series_id_start, series_id_end):
    api_url = f"https://car-web-api.autohome.com.cn/car/param/getParamConf?mode=1&site=1&seriesid={series_id}"
    try:
        response = requests.get(api_url)
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

# 統合された header_items を生成 (itemid 順にソート)
sorted_title_ids = sorted(all_title_items.keys())
integrated_header_items = [all_title_items[title_id] for title_id in sorted_title_ids]

header_base = ["グレード名", "年代", "航続距離", "価格", "SeriesID"] # SeriesID カラムを追加
header_colors_exterior = ["外装色" + str(i+1) + "_" + color_key for i in range(11) for color_key in ["名前", "コード", "価格"]]
header_colors_interior = ["内装色" + str(i+1) + "_" + color_key for i in range(3) for color_key in ["名前", "コード", "価格"]]
csv_header = header_base + integrated_header_items + header_colors_exterior + header_colors_interior
unique_csv_header = list(dict.fromkeys(csv_header))  # 順序保持で重複削除

rows = [] # データ行を格納するリスト

try:
    with pd.HDFStore(output_hdf_filename, 'w') as hdf: # HDF5 ファイルを書き込みモードでオープン
        # データ書き込み (すべての seriesid をループ)
        for series_id in range(series_id_start, series_id_end):
            if series_id not in all_series_data: # データがない場合はスキップ
                continue

            result_data = all_series_data[series_id]

            for spec_data in result_data["datalist"]:
                row_base = [spec_data["specname"], spec_data["condition"][0] if spec_data["condition"] else "", spec_data["condition"][-1] if spec_data["condition"] else "", spec_data["minprice"], series_id] # series_id を追加
                row_items = [""] * len(integrated_header_items) # 統合されたヘッダーに合わせて空リストを作成
                item_dict = {item["titleid"]: item["itemname"] for group in result_data["titlelist"] for item in group["items"]} # 各 seriesid の item_dict を作成
    
                for i, item_name in enumerate(integrated_header_items): # 統合されたヘッダーでループ
                    title_id_to_find = None
                    for title_id, name in item_dict.items(): # 各 seriesid の item_dict で検索
                        if name == item_name:
                            title_id_to_find = title_id
                            break
                    if title_id_to_find and title_id_to_find <= len(spec_data["paramconflist"]) and spec_data["paramconflist"][title_id_to_find-1]:
                        row_items[i] = spec_data["paramconflist"][title_id_to_find-1].get("itemname", "")

                row_colors_exterior = []
                for color_data in spec_data["paramconflist"]:
                    if color_data["titleid"] == 199 and "colorinfo" in color_data and color_data["colorinfo"]["type"] == 1: # 外装色
                        for i, color in enumerate(color_data["colorinfo"]["list"]):
                            if i < 11:
                                row_colors_exterior.extend([color["name"], color["value"], color["price"]])
                row_colors_exterior.extend([""] * (len(header_colors_exterior) - len(row_colors_exterior)))

                row_colors_interior = []
                for color_data in spec_data["paramconflist"]:
                    if color_data["titleid"] == 200 and "colorinfo" in color_data and color_data["colorinfo"]["type"] == 2: # 内装色
                        for i, color in enumerate(color_data["colorinfo"]["list"]):
                            if i < 3:
                                row_colors_interior.extend([color["name"], color["value"], color["price"]])
                row_colors_interior.extend([""] * (len(header_colors_interior) - len(row_colors_interior)))

                rows.append(row_base + row_items + row_colors_exterior + row_colors_interior) # データ行をリストに追加

            print(f"SeriesID: {series_id} のデータを DataFrame に追加しました。")

        df = pd.DataFrame(rows, columns=unique_csv_header) # 重複削除後のヘッダーを使用 # 修正点
        hdf.put('car_specs', df, format='table', data_columns=True) # DataFrame を HDF5 ファイルに書き込み

    print(f"HDF5ファイル '{output_hdf_filename}' (統合titlelist, 全SeriesID) が生成されました。")
    print("スクレイピング完了")

except Exception as e: # HDF5 ファイル書き込み時のエラーなどをキャッチするため、try-except ブロックで囲む
    print(f"HDF5ファイル書き込みエラー: {e}")