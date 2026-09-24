# AUDIT.md — vehicle-researcher

作成日: 2026-09-24
更新日: 2026-09-24（対応状況追記）

## 対応状況（2026-09-24）

- ✅ **対応済み**: CLAUDE.mdに「データソースの既知の制限」（日本は2ヶ月分のみ実績値／米国は2025年通年固定／中国は非公開APIで予告なく変更されうる）を追記。
- ✅ **対応済み（監査時の見落とし修正）**: `.gitignore:16` で `CLAUDE.md` が除外され一度もコミットされていないことが判明（監査本文では未指摘）。内容に機密情報・ローカル絶対パスが無いことを確認の上、`.gitignore` から除外し追跡対象化した。
- 未対応: テスト実行コマンドの追記、キャッシュ挙動の言及、クラウドサンドボックスでの動作確認手順、Pythonバージョン要件の明記は今回のスコープ外（下記「改善提案」参照、実装は未着手）。

## プロンプト監査結果

対象ファイル: `CLAUDE.md`（プロジェクトルート、24行）。`.claude/agents`・`.claude/skills`・`.claude/commands`・`.claude/rules` は存在しない。

### 良い点
- 短く要点のみ（スタック／実行／注意点の3セクション）で、トークン消費は最小限。冗長な記述は見当たらない。
- 記載されているディレクトリ構成（`scrapers/china`, `scrapers/japan`, `scrapers/usa`, `scrapers/manager.py`）は実際のファイル構成と一致しており、古くなった情報や矛盾は無い。
- `_archive/` を「参照専用、編集しない」と明記しているのは、エージェントが誤って旧実装を触るのを防ぐ良いガードレール。

### 抜けているコンテキスト（改善余地）
1. **データの既知の制限がCLAUDE.mdに無い**。README.md には以下が詳細に書かれているが、CLAUDE.md は参照していない:
   - 日本市場データは `202604`/`202605` の2ヶ月分のみ実績値で、それ以外はモック（README.md:39-42）
   - 米国市場データは2025年通年の静的データで月別フィルターが機能しない（README.md:44-47）
   - 中国市場は非公開内部APIで予告なく仕様変更・遮断されうる（README.md:49-52）
   - このため、エージェントが「データが更新されない／空になる」を実装バグと誤診断し、不要な修正を加えるリスクがある。CLAUDE.mdの「注意点」に一行でも要約を足すべき。
2. **テスト実行コマンドがCLAUDE.mdに無い**。`pytest tests/` はREADME.mdにのみ記載（README.md:110-113）。CLAUDE.mdはREADMEを読む前提を明示していないため、CLAUDE.mdだけ見て作業するとテストの存在に気づかない可能性がある。
3. **キャッシュ挙動への言及が無い**。README.md:57 に「取得済みデータは1時間キャッシュされる」とあるが、CLAUDE.mdに記載が無く、スクレイパー修正後に「変更が反映されない」と誤解される恐れがある。
4. Python バージョン要件の明記が無い（CLAUDE.md・README.md・requirements.txt いずれにも無し）。実害は小さいが、環境構築の再現性のためにあると親切。

### 曖昧さ・矛盾
特になし。指示は具体的で解釈のブレは小さい。

## ローカル依存リスト

コードベース全体を横断的に確認したが、Windowsローカルパス（`D:\`, `C:\Users\`）、WSLパス（`/mnt/`）、NASのUNCパス、ローカルDB・ローカル専用CLIツールへの依存は**見つからなかった**。

- 外部ネットワーク依存（ローカル専用ではないが要注意）:
  - `scrapers/china/ranking_scraper.py:9` — `API_BASE_URL = "https://www.dongchedi.com/motor/pc/car/rank_data"`（懂车帝の非公開内部API。クラウドサンドボックスから到達可能かはネットワークポリシー次第。中国側のボット検出でブロックされる可能性はローカル/クラウド問わず既知のリスク）
  - `scrapers/china/spec_scraper.py:40`, `scrapers/china/ranking_scraper.py:21` — `requests.get(...)` による外部HTTPアクセス
- `README.md:108` — `http://localhost:8501` はローカルでの起動確認手順の説明のみで、コード上のハードコードではない（Streamlitの既定ポート表記）。クラウドサンドボックスではブラウザでGUIを目視確認できない点に注意（後述の改善提案）。
- `_archive/` 配下（参照専用・非実行対象）にのみ `Path(__file__).parent` ベースの相対パス処理があり、絶対パスのハードコードは無い（`_archive/autohome/production/spec_scraper_multi_hdf.py:120`, `_archive/dongchedi/production/ranking_scraper.py:9` など）。
- `conftest.py:4` — `sys.path.insert(0, str(Path(__file__).parent))` は相対パスで問題なし。

全体として、このプロジェクトはクラウドサンドボックスとの親和性が高い（相対パス・標準ライブラリ中心・ローカルサービス非依存）。

## 改善提案（優先度付き）

**高**
- CLAUDE.mdに「データソースの既知の制限」（JADA実績値は2ヶ月分のみ／米国は2025年通年固定／中国は非公開APIで予告なく変更されうる）を1〜3行で要約し、README.mdへのリンクを添える。誤診断による不要な"修正"を防ぐ。

**中**
- CLAUDE.mdに `pytest tests/` の実行コマンドを追記し、README依存を減らす。
- クラウドサンドボックスでの動作確認手順を追記する。Streamlit はGUIを目視できないため、`streamlit run app.py --server.headless true` で起動し `curl -sI http://localhost:8501` でHTTP応答を確認する、といった非対話的な検証方法をCLAUDE.mdまたはREADMEに明記すると、クラウドセッションでの動作確認がしやすくなる。
- 1時間キャッシュの挙動（README.md:57）をCLAUDE.mdにも一言追記。

**低**
- Pythonバージョン要件（例: 3.11+）をrequirements.txtまたはCLAUDE.mdに明記。
