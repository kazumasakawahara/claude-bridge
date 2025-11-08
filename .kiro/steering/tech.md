# 技術スタック (Technology Stack)

## アーキテクチャ

### 全体構成
```
[Claude Code] → [File System] ← [Claude Desktop]
       ↓              ↓                ↓
  リクエスト作成   JSON通信      分析・レスポンス
       ↓              ↓                ↓
  実装実行      永続化・追跡      推奨事項提供
```

### 設計パターン
- **ファイルベースメッセージング**: JSONファイルを介した非同期通信
- **ディレクトリベース状態管理**: help-requests, help-responses, archive
- **ステートレス設計**: 各操作は独立して実行可能
- **手動トリガー**: Claude Desktopへの通知は手動（将来的に自動化可能）

### アーキテクチャの利点
1. **シンプルさ**: 複雑なネットワーク通信を回避
2. **信頼性**: ファイルシステムベースで安定
3. **デバッグ容易性**: すべてのやり取りが可視化
4. **永続化自動**: ファイルとして自然に保存

## 言語とランタイム

### Python
- **バージョン**: Python 3.7+ (型ヒント使用のため)
- **実行環境**: Claude Code環境のPython

### 標準ライブラリのみ使用
```python
import json          # リクエスト/レスポンスのシリアライズ
from datetime import datetime  # タイムスタンプ生成
from pathlib import Path       # ファイルシステム操作
from typing import Optional    # 型ヒント
import sys          # パス管理
import shutil       # アーカイブ機能
```

### 外部依存関係
**なし** - 標準ライブラリのみで動作

#### 依存関係管理の方針
- 外部ライブラリは原則追加しない
- セットアップの簡易性を最優先
- 高い互換性を維持

## 開発環境

### 必須ツール
- Python 3.7以上（型ヒント使用）
- Claude Code（リクエスト作成側）
- Claude Desktop（分析・レスポンス作成側）

### 推奨環境
- macOS（開発・テスト環境）
- ターミナル（コマンド実行）
- テキストエディタ（JSONファイル確認用）

### セットアップ手順
```bash
# 1. ディレクトリ確認
ls ~/AI-Workspace/claude-bridge/

# 2. テスト実行
cd ~/AI-Workspace/claude-bridge
python test_bridge.py --full

# 3. プロジェクトへの追加
cd ~/Projects/your-project
cat ~/AI-Workspace/claude-bridge/CLAUDE_PROTOCOL_TEMPLATE.md >> CLAUDE.md
```

## 共通コマンド

### テスト関連
```bash
# 完全なテストフロー
python test_bridge.py --full

# リクエスト作成テスト
python test_bridge.py --create

# 未回答リスト表示
python test_bridge.py --list

# 回答確認
python test_bridge.py --check req_YYYYMMDD_HHMMSS

# サンプル回答作成
python test_bridge.py --sample req_YYYYMMDD_HHMMSS
```

### 運用コマンド
```python
# リクエスト作成
from bridge_helper import ask_claude_desktop
ask_claude_desktop(
    title="問題タイトル",
    problem="問題の説明",
    tried=["試行1", "試行2"],
    files=["file1.py", "file2.py"],
    error="エラーメッセージ"
)

# 回答確認
from bridge_helper import ClaudeBridge
bridge = ClaudeBridge()
response = bridge.check_response("req_YYYYMMDD_HHMMSS")

# 未回答リスト
bridge.list_pending_requests()

# アーカイブ
bridge.archive_completed("req_YYYYMMDD_HHMMSS")
```

### エイリアス設定（推奨）
```bash
# ~/.zshrc または ~/.bashrc に追加
alias check-help="python ~/AI-Workspace/claude-bridge/test_bridge.py --list"
alias bridge-test="python ~/AI-Workspace/claude-bridge/test_bridge.py --full"

# 反映
source ~/.zshrc
```

## 環境変数

### 現在使用している変数
**なし** - 現在はハードコードされた設定を使用

### 将来的な環境変数（拡張ポイント）
```bash
# カスタムベースパス
export CLAUDE_BRIDGE_HOME="$HOME/custom-path/claude-bridge"

# 自動起動フラグ
export CLAUDE_BRIDGE_AUTO_OPEN="true"

# 通知方法設定
export CLAUDE_BRIDGE_NOTIFY="terminal"  # または "macos", "none"

# デバッグモード
export CLAUDE_BRIDGE_DEBUG="true"
```

### 設定ファイル（将来的な拡張）
```json
// ~/.claude-bridge-config.json (将来実装予定)
{
  "base_path": "~/AI-Workspace/claude-bridge",
  "auto_open_desktop": false,
  "notification_method": "terminal",
  "archive_after_days": 30,
  "max_pending_requests": 10
}
```

## ポート設定
**該当なし** - ファイルベース通信のためポートは使用しない

## データフォーマット

### リクエストJSON形式
```json
{
  "request_id": "req_YYYYMMDD_HHMMSS",
  "timestamp": "YYYYMMDD_HHMMSS",
  "title": "問題のタイトル",
  "problem": "具体的な問題の説明",
  "tried": ["試行1", "試行2"],
  "files_to_analyze": ["file1.py", "file2.py"],
  "error_messages": "エラーメッセージ",
  "context": "追加のコンテキスト",
  "project_root": "/path/to/project",
  "status": "pending"
}
```

### レスポンスJSON形式
```json
{
  "request_id": "req_YYYYMMDD_HHMMSS",
  "response_timestamp": "YYYYMMDD_HHMMSS",
  "analysis": {
    "root_cause": "根本原因の説明",
    "recommendations": [
      {
        "priority": 1,
        "title": "推奨事項のタイトル",
        "description": "詳細な説明",
        "code_example": "コード例"
      }
    ]
  },
  "implementation_steps": [
    "ステップ1",
    "ステップ2"
  ],
  "code_files": {
    "file.py": "改善されたコード"
  },
  "additional_notes": "追加の注意事項"
}
```

## セキュリティ考慮事項

### 現在の実装
- ローカルファイルシステムのみ使用
- ネットワーク通信なし
- ユーザーのホームディレクトリに配置

### セキュリティベストプラクティス
1. **機密情報の扱い**
   - APIキーやパスワードをリクエストに含めない
   - 環境変数の内容は含めない
   - データベース接続情報は除外

2. **ファイルパーミッション**
   - デフォルトのユーザーパーミッションを使用
   - 必要に応じて `chmod 600` で制限

3. **コードレビュー**
   - 分析用ファイルに機密情報が含まれていないか確認
   - レスポンスに機密情報が含まれていないか確認

## パフォーマンス特性

### 実行時間
- リクエスト作成: < 1秒
- レスポンス確認: < 0.1秒
- 未回答リスト表示: < 0.5秒
- アーカイブ: < 1秒

### ファイルサイズ
- リクエストJSON: 通常 < 10KB
- レスポンスJSON: 通常 < 50KB
- 分析用ファイル: プロジェクト依存

### スケーラビリティ
- 想定リクエスト数: 1日あたり 0-10件
- ファイルシステムベースのため、数百件まで問題なく処理可能
- 大量のリクエストが発生する場合は定期的なアーカイブを推奨

## トラブルシューティング

### よくある問題と解決方法

#### ImportError: No module named 'bridge_helper'
```python
# 解決方法: パスを追加
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))
```

#### ファイルが見つからない
```bash
# 解決方法: ディレクトリ構造を確認
ls -la ~/AI-Workspace/claude-bridge/
ls -la ~/AI-Workspace/claude-bridge/help-requests/
ls -la ~/AI-Workspace/claude-bridge/help-responses/
```

#### 回答ファイルが作成されない
```bash
# 解決方法: 未回答リクエストを確認
python test_bridge.py --list
# Claude Desktopでレスポンスを作成したか確認
```

### デバッグツール
```python
# デバッグ情報の表示
from bridge_helper import ClaudeBridge
bridge = ClaudeBridge()
print(f"Requests path: {bridge.requests_path}")
print(f"Responses path: {bridge.responses_path}")
print(f"Archive path: {bridge.archive_path}")

# ディレクトリ内容確認
import os
print(os.listdir(bridge.requests_path))
print(os.listdir(bridge.responses_path))
```
