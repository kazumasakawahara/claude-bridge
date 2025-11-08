# Claude Code ⇄ Claude Desktop Bridge

Claude CodeとClaude Desktopの連携を支援するシステムです。

## 🎯 目的

Claude Codeが実装に困難を感じた時、自動的にClaude Desktopに助けを求められる仕組みを提供します。

## 📁 ディレクトリ構造

```
~/AI-Workspace/claude-bridge/
├── bridge_helper.py              # 手動モード用ヘルパー関数
├── automation_helper.py          # 自動モード用ヘルパー関数（新機能）
├── automation_config.json        # 自動化設定ファイル（オプション）
├── configure.py                  # 設定管理CLIツール
├── dashboard.py                  # ステータスダッシュボード
├── install.sh                    # インストールスクリプト
├── CLAUDE_PROTOCOL_TEMPLATE.md   # プロジェクトのCLAUDE.mdに追加するテンプレート
├── README.md                     # このファイル
├── EXAMPLES.md                   # 使用例集
├── requirements.txt              # 依存関係リスト
├── test_bridge.py                # 手動モードテスト
├── test_automation.py            # 自動モードテスト（76テスト）
├── manual_test.py                # 手動テストシナリオ（4シナリオ）
├── performance_test.py           # パフォーマンステスト（5ベンチマーク）
├── help-requests/                # Claude Codeからのリクエスト
│   ├── req_20250104_143022.json
│   └── req_20250104_143022/      # 分析用ファイル
├── help-responses/               # Claude Desktopからの回答
│   └── req_20250104_143022_response.json
├── backups/                      # ファイルバックアップ（自動生成）
├── checkpoints/                  # チェックポイント（自動生成）
├── logs/                         # エラーログ（自動生成）
│   └── security/                 # セキュリティ監査ログ
└── archive/                      # 完了したリクエスト
```

## 🚀 セットアップ（すでに完了）

すでにセットアップは完了しています！

## 📝 使い方

このシステムには**手動モード**と**自動モード（新機能）**の2つの使い方があります。

### 🤖 自動モード（推奨）

完全自動化されたワークフローで、Claude Desktopの起動からレスポンスの監視、提案の実行まで自動化されています。

#### セットアップ

**方法1: CLIツールを使用（推奨）**

```bash
cd ~/AI-Workspace/claude-bridge/

# 対話的な設定
python3 configure.py

# クイックセットアップ（デフォルト値使用）
python3 configure.py --quick

# 現在の設定を確認
python3 configure.py --show
```

**方法2: Pythonコードで設定**

```python
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))

from automation_helper import AutomatedBridge, AutomationConfig

# 設定ファイルの作成（初回のみ）
config = AutomationConfig()
config.save("automation_config.json")
```

#### 基本的な使い方

```python
from automation_helper import AutomatedBridge

# 自動化ブリッジを作成
bridge = AutomatedBridge()

# 完全自動ワークフロー実行
response = bridge.run_automated_workflow(
    title="パフォーマンス改善が必要",
    problem="データ取り込みに5分かかる。目標は30秒以内。",
    tried=[
        "バッチサイズ変更 → 効果なし",
        "並列処理 → メモリ不足"
    ],
    files_to_analyze=["src/loader.py", "src/client.py"]
)

# 自動的に以下が実行されます:
# 1. リクエストファイルの作成
# 2. Claude Desktopの起動
# 3. レスポンスの監視（最大30分）
# 4. 提案の実行とバックアップ
# 5. エラー時の自動ロールバック
```

#### 設定オプション

`automation_config.json`で以下をカスタマイズ可能:

```json
{
    "enabled": true,
    "auto_launch_desktop": true,
    "launch_timeout": 60,
    "response_timeout": 1800,
    "polling_interval": 1.0,
    "max_launch_retries": 3,
    "retry_delay": 1
}
```

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `enabled` | `true` | 自動化機能の有効/無効 |
| `auto_launch_desktop` | `true` | Claude Desktopの自動起動 |
| `launch_timeout` | `60` | 起動タイムアウト（秒） |
| `response_timeout` | `1800` | レスポンス待機時間（秒） |
| `polling_interval` | `1.0` | ポーリング間隔（秒） |
| `max_launch_retries` | `3` | 最大起動リトライ回数 |
| `retry_delay` | `1` | リトライ間隔（秒） |

#### 手動フォールバック

自動起動が失敗した場合、手動モードに自動切り替え:

```python
# 自動起動失敗時の表示例
⚠️ Claude Desktopの自動起動に失敗しました。
手動で起動してください:
  1. Claude Desktopを開く
  2. 以下のファイルを分析: ~/AI-Workspace/claude-bridge/help-requests/req_XXX.json
```

### ✋ 手動モード

従来の手動ワークフロー。細かい制御が必要な場合に使用します。

### Claude Code側

#### 1. ヘルプリクエストの作成

```python
# プロジェクト内で
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))

from bridge_helper import ask_claude_desktop

# ヘルプを求める
request_id = ask_claude_desktop(
    title="Neo4jクエリが遅い",
    problem="5000ノードで10秒以上かかる。目標は3秒以内。",
    tried=[
        "インデックス追加 → 効果なし",
        "LIMIT句追加 → データ不完全",
        "クエリ分割 → さらに遅化"
    ],
    files=["src/queries.py", "src/models.py"],
    error="Query execution time: 12.3s"
)

# request_idが返される（例: req_20250104_143022）
```

実行すると、以下が自動的に行われます：
1. ヘルプリクエストファイル作成
2. 分析が必要なファイルをコピー
3. Claude Desktopへの指示を表示

#### 2. 回答の確認

```python
from bridge_helper import ClaudeBridge

bridge = ClaudeBridge()
response = bridge.check_response("req_20250104_143022")

if response:
    # 回答の内容を確認
    print(response)
```

#### 3. 未回答リクエストの確認

```python
from bridge_helper import ClaudeBridge

ClaudeBridge().list_pending_requests()
```

### Claude Desktop側

#### 1. リクエストの確認

Claude Codeからメッセージが表示されたら、以下を実行：

```
ヘルプリクエストの分析をお願いします。
以下のファイルを確認してください:

~/AI-Workspace/claude-bridge/help-requests/req_20250104_143022.json
```

#### 2. 分析と回答

リクエストを読み、以下の形式で回答ファイルを作成：

```json
{
  "request_id": "req_20250104_143022",
  "response_timestamp": "20250104_144530",
  "analysis": {
    "root_cause": "クエリのMATCH句の順序が非効率",
    "recommendations": [
      {
        "priority": 1,
        "title": "クエリの最適化",
        "description": "MATCH句の順序を変更し、早期フィルタリング",
        "code_example": "MATCH (p:Person {id: $person_id})-[r]-(s:Service) RETURN..."
      },
      {
        "priority": 2,
        "title": "複合インデックスの追加",
        "description": "Person.idとrelationship typeの複合インデックス",
        "code_example": "CREATE INDEX FOR (p:Person) ON (p.id)"
      }
    ]
  },
  "implementation_steps": [
    "1. src/queries.pyのget_support_network関数を修正",
    "2. Neo4jに複合インデックスを追加",
    "3. テストで性能確認（3秒以内を目標）",
    "4. エラーハンドリングを追加"
  ],
  "code_files": {
    "src/queries.py": "# 最適化されたコード\ndef get_support_network(person_id):\n    query = \"\"\"\n    MATCH (p:Person {id: $person_id})-[r]-(s:Service)\n    RETURN p, r, s\n    LIMIT 100\n    \"\"\"\n    ..."
  },
  "additional_notes": "インデックス作成後はウォームアップクエリを1回実行することを推奨"
}
```

保存先:
```
~/AI-Workspace/claude-bridge/help-responses/req_20250104_143022_response.json
```

## 💡 ベストプラクティス

### いつヘルプを求めるべきか

✅ **すぐに求める:**
- 同じエラーが3回以上
- 10分以上進展なし
- 設計判断が必要
- 影響範囲が不明

❌ **求める必要なし:**
- 単純な構文エラー
- ドキュメントに明確な答え
- 1回目の試行

### 良いリクエストの例

```python
ask_claude_desktop(
    title="具体的で簡潔なタイトル",
    problem="何を達成したいか + 現状の詳細",
    tried=[
        "具体的な試行1 → 具体的な結果",
        "具体的な試行2 → 具体的な結果"
    ],
    files=["関連する全ファイル"],
    error="完全なエラーメッセージ"
)
```

### 悪いリクエストの例

```python
ask_claude_desktop(
    title="動かない",  # ❌ 不明確
    problem="エラーが出る",  # ❌ 具体性なし
    tried=["いろいろ試した"],  # ❌ 詳細なし
    files=[],  # ❌ ファイルなし
    error=""  # ❌ エラーなし
)
```

## 🔧 トラブルシューティング

### ImportError: No module named 'bridge_helper'

```python
# パスを追加
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))
```

または、プロジェクトのCLAUDE.mdに以下を追加：

```markdown
## Python環境設定

プロジェクト開始時に以下を実行：

```python
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))
```
```

### 回答ファイルが見つからない

```python
# 未回答リクエスト確認
from bridge_helper import ClaudeBridge
ClaudeBridge().list_pending_requests()
```

### 古いリクエストの整理

```python
# 完了したリクエストをアーカイブ
from bridge_helper import ClaudeBridge
ClaudeBridge().archive_completed("req_20250104_143022")
```

## 📊 ワークフロー図

```
[Claude Code] 
    ↓ 困難に直面
    ↓ ask_claude_desktop()
    ↓
[help-requests/req_XXX.json] 作成
    ↓
[Kazumasa] 手動でClaude Desktopに伝える
    ↓
[Claude Desktop] 分析
    ↓ 回答作成
    ↓
[help-responses/req_XXX_response.json] 作成
    ↓
[Claude Code] check_response()
    ↓ 回答に基づいて実装
    ↓
[完了] → archive
```

## 🎓 実例

### 例1: パフォーマンス問題

**Claude Code:**
```python
ask_claude_desktop(
    title="WAM NETデータ取り込みが遅い",
    problem="500施設のデータ取り込みに5分かかる。目標は30秒以内。",
    tried=[
        "バッチサイズ変更 → 効果なし",
        "並列処理 → メモリ不足",
        "インデックス追加 → 若干改善（4分）"
    ],
    files=[
        "src/wamnet_loader.py",
        "src/neo4j_client.py",
        "logs/import_performance.log"
    ]
)
```

**Claude Desktop回答:**
- 根本原因: トランザクションが細かすぎる
- 推奨: バッチトランザクション（100件単位）
- 実装手順: 詳細なコード例付き

**結果:** 30秒以内に改善

### 例2: 設計問題

**Claude Code:**
```python
ask_claude_desktop(
    title="エコマップのデータモデル設計",
    problem="Person-Service間のリレーションが複雑すぎて管理困難",
    tried=[
        "正規化 → クエリ複雑化",
        "非正規化 → データ重複",
        "中間ノード追加 → さらに複雑化"
    ],
    files=[
        "src/models/ecomap.py",
        "docs/data_model.md"
    ]
)
```

**Claude Desktop回答:**
- ドメイン駆動設計の提案
- グラフモデルの再構築
- 段階的移行プラン

## 🛠️ 管理ツール

### インストールスクリプト

新規インストールやセットアップの自動化:

```bash
cd ~/AI-Workspace/claude-bridge/
./install.sh
```

機能:
- ディレクトリ構造の自動作成
- 依存関係のインストール
- 初期設定ファイルの作成
- セットアップ検証

### ステータスダッシュボード

システムの実行状況を可視化:

```bash
# 全ての情報を表示
python3 dashboard.py

# 未回答リクエストのみ
python3 dashboard.py --pending

# エラーサマリーのみ
python3 dashboard.py --errors

# システムヘルスチェック
python3 dashboard.py --health

# 自動化ステータス
python3 dashboard.py --automation
```

表示内容:
- 📊 システム統計（リクエスト数、レスポンス数、ディスク使用量）
- 🤖 自動化ステータス（有効/無効、設定内容）
- ⏳ 未回答リクエスト（作成日時、経過時間）
- ✅ 最近完了したリクエスト（推奨事項数、コード有無）
- ⚠️  エラーサマリー（過去24時間のエラー分類）
- 🏥 システムヘルスチェック（必須ファイル/ディレクトリ確認）

### セキュリティ監査

ファイル操作の安全性を確認:

```python
from automation_helper import SecurityAuditor, AutomationConfig

config = AutomationConfig()
auditor = SecurityAuditor(config)

# パスの安全性チェック
is_safe, reason = auditor.is_path_safe(Path("/path/to/file"))

# ファイル操作の監査
result = auditor.audit_file_operation(
    operation="write",
    file_path=Path("/path/to/file"),
    scan_content=True  # ファイル内容もスキャン
)

# バッチ操作の監査
batch_result = auditor.audit_batch_operations([
    {"operation": "write", "path": "/path/to/file1"},
    {"operation": "read", "path": "/path/to/file2"}
])

# 監査レポートの生成
report = auditor.generate_audit_report([result])
print(report)
```

検出内容:
- 🚨 システムディレクトリへのアクセス
- 🔑 資格情報のハードコーディング（パスワード、APIキー等）
- ⚠️  危険なコマンドパターン（rm -rf、sudo等）
- 📦 大きなファイルサイズ（10MB以上）
- 🔗 シンボリックリンクの使用

## 📞 サポート

問題があれば、以下を確認：
1. `~/AI-Workspace/claude-bridge/` の存在確認
2. `bridge_helper.py` の存在確認
3. Pythonパスの設定確認

## 🎯 まとめ

このシステムにより：
- ✅ Claude Codeは無駄な時間を使わない
- ✅ 適切なタイミングでエスカレーション
- ✅ Claude Desktopの分析力を活用
- ✅ プロジェクトの進行が加速

**迷ったら申告！これが最も重要な原則です。**
