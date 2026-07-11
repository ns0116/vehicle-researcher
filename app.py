import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

# スクレイパーマネージャーのインポート
from scrapers.manager import get_market_rankings, get_market_specs
from scrapers.japan.jada_scraper import get_available_months

# ページ基本設定
st.set_page_config(
    page_title="Vehicle Researcher | 車両リサーチハブ",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# プレミアムなデザインを適用するカスタムCSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap');
    
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Outfit', 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
        padding: 30px;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        opacity: 0.85;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 180, 219, 0.4);
        color: white;
        border: none;
    }
    .card-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #0083b0;
        margin-bottom: 20px;
    }
    /* ダークモードの対応 */
    @media (prefers-color-scheme: dark) {
        .card-container {
            background-color: #1e222b;
            border-left: 5px solid #00b4db;
        }
    }
</style>
""", unsafe_allow_html=True)

# アプリヘッダー
st.markdown("""
<div class="main-header">
    <h1>🚗 Vehicle Researcher</h1>
    <p>グローバル自動車市場（中国・日本・北米）の新車販売ランキングや車両諸元（スペック）をインタラクティブに比較・分析します</p>
</div>
""", unsafe_allow_html=True)

# サイドバーによるナビゲーションと市場設定
st.sidebar.title("設定")
selected_market_label = st.sidebar.selectbox("対象市場 (Target Market)", ["中国 (China)", "日本 (Japan)", "北米 (North America)"])
market = selected_market_label.split(" ")[0] # "中国", "日本", "北米" を抽出

page = st.sidebar.radio("機能", ["販売台数ランキング", "車両諸元（スペック）比較"])

# Excelダウンロード用ヘルパー関数
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

if page == "販売台数ランキング":
    st.header(f"📈 {market} 新車販売台数ランキング")
    
    # 市場に応じた説明文
    if market == "中国":
        st.markdown("中国市場（懂车帝 API）の月次ランキング。エネルギータイプやボディスタイルで絞り込み可能です。")
    elif market == "日本":
        st.markdown("日本市場（自販連 JADA発表）の新車乗用車ブランド通称名別販売台数ランキング。")
    else:
        st.markdown("北米市場（GoodCarBadCar発表）の新車モデル別年間販売台数ランキング。")
        
    # フィルター設定 (3カラム表示)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if market == "中国":
            # 年月のリスト（過去12ヶ月）
            current_year = datetime.now().year
            current_month = datetime.now().month
            months = []
            for i in range(12):
                m = current_month - i
                y = current_year
                if m <= 0:
                    m += 12
                    y -= 1
                months.append(f"{y}{m:02d}")
            months.insert(0, "") # 最新のオプション
            selected_month = st.selectbox("対象年月 (YYYYMM)", months, index=1, help="過去の販売ランキングを取得する場合は年月を選択してください。")
        elif market == "日本":
            available_months = get_available_months()
            selected_month = st.selectbox("対象年月 (YYYYMM)", available_months, index=0, help="JADA公表データを表示します。")
        else:
            selected_month = st.selectbox("対象期間", ["2025年 通年（静的データ）"], index=0)
            
    with col2:
        if market == "中国":
            energy_options = {
                "すべてのエネルギータイプ (燃油+新エネルギー)": "",
                "EV / 纯电动 (純電気自動車)": "1",
                "PHEV / 插电式混动 (プラグインハイブリッド)": "2",
                "REEV / 增程式 (レンジエクステンダー)": "3"
            }
            selected_energy_label = st.selectbox("パワートレイン / エネルギータイプ", list(energy_options.keys()), index=0)
            selected_energy = energy_options[selected_energy_label]
        else:
            st.selectbox("エネルギータイプ", ["制限なし"], disabled=True)
            selected_energy = ""
            
    with col3:
        default_limit = 200 if market == "中国" else 20
        limit = st.number_input("最大取得件数", min_value=10, max_value=5000, value=default_limit, step=10)

    # 詳細フィルターオプション (中国市場のみ)
    selected_series = ""
    if market == "中国":
        with st.expander("🔍 詳細取得フィルター"):
            series_type_options = {
                "すべてのボディタイプ": "",
                "セダン / 轿车 (Sedan)": "1",
                "SUV": "2",
                "MPV": "3"
            }
            selected_series_label = st.selectbox("ボディタイプ", list(series_type_options.keys()), index=0)
            selected_series = series_type_options[selected_series_label]

    if st.button("🔍 ランキングデータを取得"):
        with st.spinner(f"{market}のデータを取得中..."):
            df, is_estimated = get_market_rankings(
                market=market,
                month=selected_month,
                energy_type=selected_energy,
                series_type=selected_series,
                count=int(limit)
            )

            if df is not None and not df.empty:
                # セッションステートへの保存時に市場タグを含めてキーに格納
                st.session_state["sales_data"] = df
                st.session_state["sales_market"] = market
                st.session_state["selected_month_label"] = selected_month or "最新"
                st.session_state["sales_is_estimated"] = is_estimated
                st.success(f"成功: {len(df)} 件のモデル情報を取得しました！")
            else:
                st.error("データの取得に失敗したか、データが存在しませんでした。条件を変更して再度お試しください。")

    # セッションデータがあり、かつ選択市場と合致する場合は表示
    if "sales_data" in st.session_state and st.session_state.get("sales_market") == market:
        df_raw = st.session_state["sales_data"]
        month_label = st.session_state.get("selected_month_label", "最新")
        if st.session_state.get("sales_is_estimated"):
            st.warning("⚠️ このデータは JADA 公式数値ではなく、推定値です。")
        
        # インタラクティブな絞り込みフィルターを表示
        st.subheader("🔍 表示フィルター (瞬時に絞り込み)")
        col_filt1, col_filt2 = st.columns(2)
        with col_filt1:
            # ブランド名での絞り込みマルチセレクト
            unique_brands = sorted(df_raw["ブランド名"].dropna().unique())
            selected_brands = st.multiselect(
                "ブランド名で表示を絞り込み",
                options=unique_brands,
                default=[],
                help="選択したブランドの車両のみを表示します（未選択時はすべて表示）。"
            )
        with col_filt2:
            # 車種名・モデル名キーワード検索
            search_keyword = st.text_input(
                "車種名やモデル名で絞り込み",
                value="",
                placeholder="例: Tesla, BYD, ヤリス, F-Series"
            )
            
        # フィルター適用
        df_filtered = df_raw.copy()
        if selected_brands:
            df_filtered = df_filtered[df_filtered["ブランド名"].isin(selected_brands)]
        if search_keyword:
            df_filtered = df_filtered[
                df_filtered["車種名"].str.contains(search_keyword, case=False, na=False) |
                df_filtered["ブランド名"].str.contains(search_keyword, case=False, na=False) |
                df_filtered["サブブランド名"].str.contains(search_keyword, case=False, na=False)
            ]
            
        # 表示列の選択フィルター
        all_cols = list(df_filtered.columns)
        default_cols = ["順位", "車種名", "ブランド名", "販売台数", "価格帯"]
        default_selection = [c for c in default_cols if c in all_cols]
        
        selected_cols = st.multiselect(
            "表示するカラム（列）を選択してください",
            options=all_cols,
            default=default_selection,
            help="チェックボックスで表示・非表示を切り替えられます。"
        )
        
        # 簡易統計情報 (絞り込み後のデータに基づく)
        st.subheader("📊 クイック統計")
        stat1, stat2, stat3 = st.columns(3)
        with stat1:
            st.metric("表示モデル数", len(df_filtered))
        with stat2:
            sales_series = pd.to_numeric(df_filtered["販売台数"], errors='coerce').dropna()
            st.metric("総販売台数 (表示分)", f"{int(sales_series.sum()):,} 台")
        with stat3:
            top_brand = df_filtered["ブランド名"].value_counts().index[0] if not df_filtered.empty else "N/A"
            st.metric("最多掲載ブランド", top_brand)
            
        # データテーブルの表示
        st.subheader("📋 販売ランキングデータ一覧")
        st.info("💡 表の左端のチェックボックスを選択（複数可）すると、選択した車両のスペック比較表が下に自動的に表示されます。")
        
        # 表示対象のカラムのみに制限する
        df_display = df_filtered[selected_cols] if selected_cols else df_filtered
        
        # 行選択可能なデータフレームを表示 (選択保持を防ぐためキーを一意にする)
        event = st.dataframe(
            df_display,
            use_container_width=True,
            on_select="rerun",
            selection_mode="multi-row",
            key=f"ranking_df_{market}_{month_label}_{selected_energy}_{selected_series}_{len(df_filtered)}"
        )
        
        # ダウンロードボタン
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_data = df_filtered.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV形式でダウンロード",
                data=csv_data,
                file_name=f"sales_ranking_{market}_{month_label}.csv",
                mime='text/csv'
            )
        with col_dl2:
            try:
                excel_data = to_excel(df_filtered)
                st.download_button(
                    label="📥 Excel形式でダウンロード",
                    data=excel_data,
                    file_name=f"sales_ranking_{market}_{month_label}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            except Exception as e:
                st.warning(f"Excelダウンロードの準備中にエラーが発生しました: {e}")
                
        # スペック比較表示（行が選択されている場合）
        selected_rows = []
        if event and hasattr(event, "selection"):
            if isinstance(event.selection, dict):
                selected_rows = event.selection.get("rows", [])
            else:
                selected_rows = getattr(event.selection, "rows", [])
                
        if selected_rows:
            st.markdown("---")
            st.subheader("🚗 選択された車両のスペック（諸元）比較")
            
            selected_df = df_filtered.iloc[selected_rows]
            
            # 各車種の最初のオンライン販売車種ID（トリムID）を収集
            car_ids = []
            for idx, row in selected_df.iterrows():
                online_ids = row.get("オンライン販売車種IDリスト")
                offline_ids = row.get("オフライン販売車種IDリスト")
                
                cid = None
                if isinstance(online_ids, list) and online_ids:
                    cid = online_ids[0]
                elif isinstance(offline_ids, list) and offline_ids:
                    cid = offline_ids[0]
                    
                if cid:
                    car_ids.append(cid)
                    
            if car_ids:
                with st.spinner(f"{market}スペックデータを取得中..."):
                    specs_df = get_market_specs(market, car_ids)
                    
                    if specs_df is not None and not specs_df.empty:
                        # 転置表示の切替
                        transpose_opt = st.checkbox("表を転置する（車種を列にする）", value=True, key=f"rank_transpose_{market}")
                        
                        if transpose_opt:
                            display_specs = specs_df.copy()
                            display_specs["項目"] = display_specs["カテゴリ"] + " - " + display_specs["項目"]
                            display_specs = display_specs.drop(columns=["カテゴリ"]).set_index("項目").T
                            st.dataframe(display_specs, use_container_width=True)
                        else:
                            st.dataframe(specs_df, use_container_width=True)
                            
                        # スペック表ダウンロード
                        col_spec_dl1, col_spec_dl2 = st.columns(2)
                        with col_spec_dl1:
                            csv_specs = specs_df.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="📥 スペック比較表をCSVでダウンロード",
                                data=csv_specs,
                                file_name=f"specs_comparison_{market}.csv",
                                mime='text/csv'
                            )
                        with col_spec_dl2:
                            try:
                                excel_specs = to_excel(specs_df)
                                st.download_button(
                                    label="📥 スペック比較表をExcelでダウンロード",
                                    data=excel_specs,
                                    file_name=f"specs_comparison_{market}.xlsx",
                                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                )
                            except Exception as e:
                                st.warning(f"Excelダウンロードの準備中にエラーが発生しました: {e}")
                    else:
                        st.error("スペックデータの取得に失敗しました。")
            else:
                st.warning("選択した車種に対応する具体的な車両IDが見つかりませんでした。")
                
        # 棒グラフの表示
        st.subheader(f"📊 販売台数上位10モデルの比較 ({market})")
        if df_filtered.empty:
            st.info("絞り込み結果が0件のため、グラフを表示できません。")
        else:
            chart_df = df_filtered.copy()
            chart_df["販売台数"] = pd.to_numeric(chart_df["販売台数"], errors='coerce')
            top10 = chart_df.nlargest(10, "販売台数")
            st.bar_chart(data=top10, x="車種名", y="販売台数", color="#0083b0")

else: # 車両諸元（スペック）比較
    st.header(f"⚙️ {market} 車両諸元（スペック）比較")
    
    st.markdown(f"""
    選択された市場（{market}）の車両詳細スペックを取得し、横並びで比較します。
    車両ID（コンマ区切りで複数指定可能）を直接入力して実行してください。
    """)
    
    # プリセット表示（市場ごと）
    if market == "中国":
        st.markdown("""
        <div class="card-container">
            <strong>💡 中国モデルのトリムIDプリセット:</strong><br/>
            <ul>
                <li><strong>Xiaomi SU7 後駆標準版 (EV):</strong> 255153</li>
                <li><strong>Xiaomi SU7 Max 四駆超長航版 (EV):</strong> 255155</li>
                <li><strong>Tesla Model Y 後輪駆動版 (EV):</strong> 255110</li>
                <li><strong>Tesla Model Y Long Range (EV):</strong> 255111</li>
                <li><strong>Geely Galaxy Xingyuan 310km 向往版:</strong> 259371</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        default_ids = "255153, 255110"
        input_help = "懂车帝の車両スペックURLに含まれるIDを入力してください (例: params-carIds-255153)"
    elif market == "日本":
        st.markdown("""
        <div class="card-container">
            <strong>💡 日本（JDM）モデルの車両IDプリセット:</strong><br/>
            <ul>
                <li><strong>トヨタ ヤリス (HYBRID G):</strong> 1001</li>
                <li><strong>トヨタ カローラ (HYBRID G):</strong> 1002</li>
                <li><strong>トヨタ シエンタ (HEV 5人乗り):</strong> 1004</li>
                <li><strong>ホンダ フリード (e:HEV AIR):</strong> 1006</li>
                <li><strong>トヨタ アルファード (HYBRID Z):</strong> 1007</li>
                <li><strong>トヨタ アクア (Zグレード HEV):</strong> 1010</li>
                <li><strong>日産 ノート (e-POWER X):</strong> 1013</li>
                <li><strong>トヨタ プリウス (2.0L HEV):</strong> 1014</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        default_ids = "1001, 1002, 1014"
        input_help = "プリセットにある代表車両IDをコンマ区切りで入力してください"
    else:
        st.markdown("""
        <div class="card-container">
            <strong>💡 北米（US）モデルの車両IDプリセット:</strong><br/>
            <ul>
                <li><strong>Ford F-150 (3.5L EcoBoost Pickup):</strong> 2001</li>
                <li><strong>Chevrolet Silverado 1500 (5.3L V8 Pickup):</strong> 2002</li>
                <li><strong>Toyota RAV4 (2.5L Hybrid Compact SUV):</strong> 2003</li>
                <li><strong>Honda CR-V (Sport Hybrid SUV):</strong> 2004</li>
                <li><strong>Toyota Camry (LE Hybrid Sedan):</strong> 2008</li>
                <li><strong>Tesla Model Y (Long Range AWD EV):</strong> 2009</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        default_ids = "2001, 2003, 2009"
        input_help = "北米プリセットにある代表車両IDをコンマ区切りで入力してください"
        
    # 車両ID入力
    car_input = st.text_input("車両IDを入力 (複数指定する場合はコンマで区切る)", default_ids, help=input_help)
    
    transpose_opt = st.checkbox("表を転置する（車種を列にする）", value=True, help="表を転置すると、複数の車両スペックを横並びで比較しやすくなります。")
    
    if st.button("⚙️ スペックを取得して比較"):
        try:
            # トリムIDのパース
            car_ids = [int(cid.strip()) for cid in car_input.split(",") if cid.strip().isdigit()]
            
            if not car_ids:
                st.error("有効な数値車両IDを1つ以上入力してください。")
            else:
                with st.spinner(f"{len(car_ids)} 台のスペックを{market}データから取得中..."):
                    df = get_market_specs(market, car_ids)
                    
                    if df is not None and not df.empty:
                        st.session_state["manual_spec_data"] = df
                        st.session_state["manual_spec_market"] = market
                        st.session_state["manual_spec_ids"] = car_ids
                        st.success(f"成功: {len(car_ids)} 台の車両スペックを取得しました！")
                    else:
                        st.error("スペックデータを取得できませんでした。")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            
    # スペックデータの表示
    if "manual_spec_data" in st.session_state and st.session_state.get("manual_spec_market") == market:
        df = st.session_state["manual_spec_data"]
        spec_ids = st.session_state["manual_spec_ids"]
        
        st.subheader("📋 スペック（諸元）比較表")
        
        if transpose_opt:
            display_df = df.copy()
            display_df["項目"] = display_df["カテゴリ"] + " - " + display_df["項目"]
            display_df = display_df.drop(columns=["カテゴリ"]).set_index("項目").T
            st.dataframe(display_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)
            
        # ダウンロードボタン
        col_dl_s1, col_dl_s2 = st.columns(2)
        with col_dl_s1:
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 スペック表をCSVでダウンロード",
                data=csv_data,
                file_name=f"manual_specs_{market}_{'_'.join(map(str, spec_ids))}.csv",
                mime='text/csv'
            )
        with col_dl_s2:
            try:
                excel_data = to_excel(df)
                st.download_button(
                    label="📥 スペック表をExcelでダウンロード",
                    data=excel_data,
                    file_name=f"manual_specs_{market}_{'_'.join(map(str, spec_ids))}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            except Exception as e:
                st.warning(f"Excelダウンロードの準備中にエラーが発生しました: {e}")
