# vehicle-researcher — Claude Context

中国・日本・北米市場の新車販売ランキング取得とスペック横並び比較を行う Streamlit アプリ。

## スタック

- Python / Streamlit
- `app.py` がエントリーポイント
- `scrapers/china/`（懂车帝 Dongchedi API）、`scrapers/japan/`（JADA）、`scrapers/usa/`（GoodCarBadCar）にスクレイパーを市場別に分離
- `scrapers/manager.py` が横断的にスクレイパーを呼び出す
- `_archive/` は旧実装（autohome, dongchedi の旧版）。参照専用、編集しない

## 実行

Python 3.9 以上（`list[int]` 等の組み込みジェネリクスを使用。2026-10-04 に 3.12 で動作確認）。

```bash
pip install -r requirements.txt
streamlit run app.py
pytest tests/          # ユニットテスト（外部サイトにはアクセスしない）
```

ブラウザを使わずに起動を確かめる場合（クラウド等）:

```bash
streamlit run app.py --server.headless true --server.port 8501 &
curl -s http://localhost:8501/_stcore/health   # "ok" なら起動成功
```

`health` が ok でも、スクレイパーが外部サイトから取得できているかは別（`pytest` も通信をモックするので確かめられない）。取得の確認は画面で行う。

## 注意点

- 各市場のスクレイパーは外部サイトのHTML/API構造に依存する。取得失敗時はまずサイト側の構造変更を疑う
- 新しい市場・データソースを追加する場合は `scrapers/<market>/` に既存市場と同じ構成で追加する

## データソースの既知の制限

- 日本市場: `202604`/`202605` の2ヶ月分のみ実績値、それ以外はモックデータ
- 米国市場: 2025年通年の静的データで月別フィルターが機能しない
- 中国市場: 非公開の内部API（懂车帝）を使用しており、予告なく仕様変更・遮断されうる
- 取得結果は `app.py` の `@st.cache_data(ttl=3600)` で 1 時間キャッシュされる。スクレイパーを直しても画面が変わらないときは、サイドバーの「キャッシュをクリア」で消してから確かめる
- データが更新されない・空になる場合、まずこの制限を疑う（実装バグと誤診断しない）。詳細は README.md 参照
