# プロジェクト構造 (Project Structure)

## ルートディレクトリ構成

```
~/AI-Workspace/claude-bridge/
├── .kiro/                        # Kiro仕様駆動開発ディレクトリ
│   ├── steering/                # ステアリングドキュメント
│   │   ├── product.md          # 製品概要
│   │   ├── tech.md             # 技術スタック
│   │   └── structure.md        # プロジェクト構造（このファイル）
│   └── specs/                   # 仕様書（機能別）
│       └── [feature-name]/     # 機能別仕様ディレクトリ
│           ├── requirements.md
│           ├── design.md
│           └── tasks.md
│
├── bridge_helper.py             # コアロジック - ClaudeBridgeクラス
├── test_bridge.py               # テストスイート - 完全なテストフロー
├── CLAUDE.md                    # プロジェクト指示書 - Kiro開発ガイド
├── README.md                    # 詳細ドキュメント - 使用方法と実例
├── QUICKSTART.md                # クイックスタートガイド - 3ステップセットアップ
├── CLAUDE_PROTOCOL_TEMPLATE.md  # プロトコルテンプレート - 他プロジェクト用
│
├── help-requests/               # リクエスト格納ディレクトリ
│   ├── req_YYYYMMDD_HHMMSS.json           # リクエストメタデータ
│   └── req_YYYYMMDD_HHMMSS/               # 分析用ファイルコピー
│       └── [copied-files]
│
├── help-responses/              # レスポンス格納ディレクトリ
│   └── req_YYYYMMDD_HHMMSS_response.json  # Claude Desktopからの回答
│
└── archive/                     # 完了リクエストのアーカイブ
    └── req_YYYYMMDD_HHMMSS/    # アーカイブされたリクエスト
        ├── req_YYYYMMDD_HHMMSS.json
        ├── req_YYYYMMDD_HHMMSS_response.json
        └── [copied-files]
```

## サブディレクトリ構造の詳細

### .kiro/ - Kiro仕様駆動開発
```
.kiro/
├── steering/              # プロジェクト全体のガイダンス
│   ├── product.md        # 製品概要、価値提案、ユースケース
│   ├── tech.md           # 技術スタック、アーキテクチャ、環境
│   └── structure.md      # プロジェクト構造、コード組織化
│
└── specs/                 # 機能別仕様書
    └── [feature-name]/   # 各機能のディレクトリ
        ├── requirements.md  # 要件定義
        ├── design.md        # 技術設計
        └── tasks.md         # 実装タスク
```

**役割**:
- `steering/`: AI開発者への常時ロードされるコンテキスト
- `specs/`: 機能別の詳細仕様と進捗管理

### help-requests/ - リクエスト管理
```
help-requests/
├── req_20250104_143022.json        # リクエストメタデータ
├── req_20250104_143022/            # 分析用ファイル
│   ├── queries.py                  # コピーされたファイル1
│   └── models.py                   # コピーされたファイル2
├── req_20250105_091530.json
└── req_20250105_091530/
    └── config.yaml
```

**命名規則**: `req_YYYYMMDD_HHMMSS`
- YYYY: 年（4桁）
- MM: 月（2桁）
- DD: 日（2桁）
- HH: 時（24時間制、2桁）
- MM: 分（2桁）
- SS: 秒（2桁）

### help-responses/ - レスポンス管理
```
help-responses/
├── req_20250104_143022_response.json
├── req_20250105_091530_response.json
└── ...
```

**命名規則**: `req_YYYYMMDD_HHMMSS_response.json`
- リクエストIDに `_response` サフィックスを追加

### archive/ - アーカイブ
```
archive/
└── req_20250104_143022/
    ├── req_20250104_143022.json          # 元のリクエスト
    ├── req_20250104_143022_response.json # レスポンス
    ├── queries.py                        # 分析用ファイル
    └── models.py
```

**役割**:
- 完了したリクエスト・レスポンスの永続保存
- 知識ベースとしての再利用
- プロジェクト履歴の追跡

## コード組織化パターン

### bridge_helper.py の構造
```python
"""
モジュールレベルdocstring
- 目的の説明
- 使用方法の概要
"""

# インポート（標準ライブラリのみ）
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class ClaudeBridge:
    """メインクラス - すべての機能を提供"""

    def __init__(self):
        """パス設定とディレクトリ初期化"""
        ...

    def create_help_request(self, ...):
        """リクエスト作成のコアロジック"""
        ...

    def check_response(self, request_id: str):
        """レスポンス確認ロジック"""
        ...

    def list_pending_requests(self):
        """未回答リクエスト一覧"""
        ...

    def archive_completed(self, request_id: str):
        """アーカイブ機能"""
        ...


# 便利な関数（短縮版）
def ask_claude_desktop(...):
    """簡易インターフェース"""
    bridge = ClaudeBridge()
    return bridge.create_help_request(...)


if __name__ == "__main__":
    # テスト・デモコード
    ...
```

### test_bridge.py の構造
```python
"""
テストスイート
- 各機能のテスト関数
- 完全なフローテスト
"""

# インポート
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))
from bridge_helper import ask_claude_desktop, ClaudeBridge


def test_create_request():
    """リクエスト作成テスト"""
    ...

def test_check_response(request_id: str):
    """レスポンス確認テスト"""
    ...

def test_list_pending():
    """未回答リスト表示テスト"""
    ...

def create_sample_response(request_id: str):
    """サンプルレスポンス作成"""
    ...

def run_full_test():
    """完全なテストフロー"""
    ...


if __name__ == "__main__":
    # コマンドライン引数処理
    import argparse
    ...
```

## ファイル命名規則

### Python ファイル
- **モジュール**: `snake_case.py`
  - 例: `bridge_helper.py`, `test_bridge.py`
- **クラス**: `PascalCase`
  - 例: `ClaudeBridge`
- **関数**: `snake_case`
  - 例: `create_help_request()`, `ask_claude_desktop()`
- **変数**: `snake_case`
  - 例: `request_id`, `response_file`

### Markdown ファイル
- **ドキュメント**: `UPPERCASE.md` または `lowercase.md`
  - 主要: `README.md`, `CLAUDE.md`, `QUICKSTART.md`
  - ステアリング: `product.md`, `tech.md`, `structure.md`

### JSON ファイル
- **リクエスト**: `req_YYYYMMDD_HHMMSS.json`
- **レスポンス**: `req_YYYYMMDD_HHMMSS_response.json`

### ディレクトリ
- **小文字 + ハイフン**: `help-requests/`, `help-responses/`
- **ドット接頭辞**: `.kiro/`（隠しディレクトリ）

## インポート組織化

### プロジェクトからの使用
```python
# プロジェクト内のどこからでも使用可能
import sys
from pathlib import Path

# パスを追加
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))

# インポート
from bridge_helper import ask_claude_desktop, ClaudeBridge
```

### CLAUDE.md への追加（推奨）
```markdown
## Python環境設定

プロジェクト開始時に以下を実行：

\`\`\`python
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))
\`\`\`
```

## 主要なアーキテクチャ原則

### 1. シンプルさ優先
- 外部依存なし
- 標準ライブラリのみ
- 複雑な設定不要

**理由**: セットアップの簡易性と互換性の高さ

### 2. ファイルベース通信
- JSON形式のメッセージ
- ディレクトリベースの状態管理
- 手動トリガー（将来的に自動化可能）

**理由**:
- デバッグが容易
- 永続化が自動
- ネットワーク不要

### 3. ステートレス設計
- 各操作は独立
- 依存関係なし
- 再実行可能

**理由**:
- 信頼性が高い
- テストが容易
- エラーリカバリが簡単

### 4. 型ヒントの活用
```python
def create_help_request(
    self,
    title: str,
    problem: str,
    tried: list[str],
    files_to_analyze: list[str],
    error_messages: str = "",
    context: str = ""
) -> str:
    ...
```

**理由**:
- コードの意図を明確化
- IDEサポートの向上
- バグの早期発見

### 5. エラーハンドリング
```python
try:
    content = full_path.read_text(encoding="utf-8")
    dest.write_text(content, encoding="utf-8")
except Exception as e:
    print(f"⚠️  {file_path} のコピーに失敗: {e}")
```

**理由**:
- 部分的な失敗を許容
- ユーザーへの明確なフィードバック
- システムの継続動作

### 6. ユーザビリティ重視
```python
print(f"""
{'='*60}
🚨 ヘルプリクエスト作成完了
{'='*60}

リクエストID: {request_id}
タイトル: {title}

📁 作成されたファイル:
   - リクエスト: {request_file}
   - 分析用ファイル: {len(copied_files)}個
...
""")
```

**理由**:
- 次のステップが明確
- 学習曲線が緩やか
- エラーが少ない

## コードレビューチェックリスト

### 新規コード追加時
- [ ] 型ヒントを使用しているか
- [ ] docstringが明確か
- [ ] エラーハンドリングが適切か
- [ ] ユーザーへのフィードバックが十分か
- [ ] 標準ライブラリのみを使用しているか

### ファイル追加時
- [ ] 命名規則に従っているか
- [ ] 適切なディレクトリに配置されているか
- [ ] ドキュメントを更新したか
- [ ] テストを追加したか

### リファクタリング時
- [ ] 既存の機能を壊していないか
- [ ] test_bridge.py でテストしたか
- [ ] ドキュメントを更新したか
- [ ] 下位互換性を保っているか

## ベストプラクティス

### ファイル操作
```python
# Good: pathlibを使用
from pathlib import Path
file_path = Path.home() / "AI-Workspace/claude-bridge" / "file.json"
content = file_path.read_text(encoding="utf-8")

# Bad: 文字列結合
import os
file_path = os.path.join(os.path.expanduser("~"), "AI-Workspace", "claude-bridge", "file.json")
with open(file_path, 'r') as f:
    content = f.read()
```

### JSON処理
```python
# Good: ensure_ascii=False で日本語を保持
json.dumps(data, indent=2, ensure_ascii=False)

# Bad: ensure_asciiのデフォルト（True）でエスケープされる
json.dumps(data, indent=2)
```

### ディレクトリ作成
```python
# Good: parents=True, exist_ok=True
path.mkdir(parents=True, exist_ok=True)

# Bad: 親ディレクトリがないとエラー
path.mkdir()
```

### タイムスタンプ
```python
# Good: 統一されたフォーマット
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Bad: 異なるフォーマットの混在
timestamp = datetime.now().isoformat()
```
