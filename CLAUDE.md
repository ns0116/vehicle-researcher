# vehicle-researcher — Claude Context

中国・日本・北米市場の新車販売ランキング取得とスペック横並び比較を行う Streamlit アプリ。

## スタック

- Python / Streamlit
- `app.py` がエントリーポイント
- `scrapers/china/`（懂车帝 Dongchedi API）、`scrapers/japan/`（JADA）、`scrapers/usa/`（GoodCarBadCar）にスクレイパーを市場別に分離
- `scrapers/manager.py` が横断的にスクレイパーを呼び出す
- `_archive/` は旧実装（autohome, dongchedi の旧版）。参照専用、編集しない

## 実行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 注意点

- 各市場のスクレイパーは外部サイトのHTML/API構造に依存する。取得失敗時はまずサイト側の構造変更を疑う
- 新しい市場・データソースを追加する場合は `scrapers/<market>/` に既存市場と同じ構成で追加する

## データソースの既知の制限

- 日本市場: `202604`/`202605` の2ヶ月分のみ実績値、それ以外はモックデータ
- 米国市場: 2025年通年の静的データで月別フィルターが機能しない
- 中国市場: 非公開の内部API（懂车帝）を使用しており、予告なく仕様変更・遮断されうる
- データが更新されない・空になる場合、まずこの制限を疑う（実装バグと誤診断しない）。詳細は README.md 参照
