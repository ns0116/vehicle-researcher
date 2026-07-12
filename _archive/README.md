# _archive

このディレクトリには過去の開発用スクリプトが保管されています。**本番アプリケーション (`app.py`) からは参照されません。**

| ディレクトリ | 内容 |
|---|---|
| `dongchedi/production/` | 懂车帝向けのオリジナルスクレイパー（HDF5なし版）。現在の `scrapers/china/` の元になったコード。 |
| `autohome/production/` | 自動車之家向けスクレイパー（HDF5/PyTables 出力版）。`tables` パッケージに依存するため本番からは除外。 |

> **注意**: `autohome/` 配下のコードは `tables` (PyTables/HDF5) に依存しています。実行する場合は `pip install tables` が別途必要です。
