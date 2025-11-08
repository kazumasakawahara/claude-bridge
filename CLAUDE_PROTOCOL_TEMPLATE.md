# Claude Code ⇄ Claude Desktop 連携プロトコル

## 概要

このプロジェクトでは、Claude Codeが困難に直面した時に、自動的にClaude Desktopに
ヘルプを求める仕組みを導入しています。

## いつヘルプを求めるべきか

以下のいずれかに該当する場合は、**即座に**ヘルプリクエストを作成してください：

### 🔴 必須レベル（絶対に申告）

1. **同じエラーが3回以上発生**
   - 同じアプローチで3回失敗したら、別の戦略が必要

2. **10分以上進展なし**
   - 複数の方法を試しても解決しない
   - ドキュメントを調べても答えが見つからない

3. **設計判断が必要**
   - 複数の実装方法があり、どれが最適か判断できない
   - アーキテクチャレベルの変更が必要そう
   - データモデルの根本的な見直しが必要

4. **影響範囲が不明確**
   - 変更が他の部分にどう影響するか予測困難
   - リファクタリングの安全性が確保できない

### 🟡 推奨レベル（判断に迷ったら申告）

5. **パフォーマンス問題**
   - 処理時間が想定の2倍以上
   - メモリ使用量が異常
   - クエリが遅すぎる

6. **複雑度の急上昇**
   - 関数が50行を超えた
   - ネストが4階層以上
   - 同じコードが3回以上重複

7. **テストが通らない**
   - テストを修正しても他のテストが壊れる
   - 根本原因が不明

## ヘルプリクエストの作成方法

### 基本的な使い方

```python
# プロジェクトルートで実行
import sys
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))
from bridge_helper import ask_claude_desktop

# ヘルプリクエスト作成
request_id = ask_claude_desktop(
    title="問題の簡潔なタイトル",
    problem="具体的な問題の説明（何が起きているか、何を達成したいか）",
    tried=[
        "試した方法1 → 結果1",
        "試した方法2 → 結果2",
        "試した方法3 → 結果3"
    ],
    files=["src/problem_file.py", "src/related_file.py"],
    error="エラーメッセージ（あれば）"
)
```

### プロジェクト固有の例

#### 例1: データベースクエリの問題
```python
ask_claude_desktop(
    title="Neo4jクエリのパフォーマンス問題",
    problem="get_support_network関数が5000ノードで10秒以上かかる。目標は3秒以内。",
    tried=[
        "インデックスをperson_idに追加 → 改善なし",
        "LIMIT句で制限 → データが不完全になる",
        "クエリを2つに分割 → さらに遅くなった"
    ],
    files=[
        "src/neo4j_queries.py",
        "src/models/support_network.py",
        "tests/performance_test.log"
    ],
    error="Query execution time: 12.3 seconds"
)
```

#### 例2: データモデルの設計問題
```python
ask_claude_desktop(
    title="エコマップのリレーション設計が複雑化",
    problem="Person-Service-Organization間のリレーションが多すぎて管理困難。正規化すべきか非正規化すべきか判断できない。",
    tried=[
        "完全正規化 → クエリが複雑すぎる",
        "非正規化 → データ重複が多い",
        "中間テーブル追加 → さらに複雑化"
    ],
    files=[
        "src/models/ecomap.py",
        "src/schema/graph_schema.py",
        "docs/current_design.md"
    ]
)
```

#### 例3: API統合の問題
```python
ask_claude_desktop(
    title="Google Sheets API認証エラーが解決しない",
    problem="credentials.jsonを使った認証が間欠的に失敗する。5回に1回は成功するが、原因不明。",
    tried=[
        "認証スコープを確認 → 正しい",
        "トークンを再生成 → 変化なし",
        "リトライロジック追加 → 根本解決にならない"
    ],
    files=[
        "src/google_sheets_client.py",
        "src/auth/credentials_manager.py",
        "logs/auth_errors.log"
    ],
    error="google.auth.exceptions.RefreshError: The credentials do not contain the necessary fields"
)
```

## Claude Desktop側の対応フロー

Claude Desktopでは、以下の手順で対応してください：

1. **リクエストファイルを読み込む**
   ```
   ~/AI-Workspace/claude-bridge/help-requests/req_YYYYMMDD_HHMMSS.json
   ```

2. **関連ファイルを分析**
   - リクエストに添付されたファイルを確認
   - プロジェクト全体の構造を理解

3. **回答ファイルを作成**
   ```json
   {
     "request_id": "req_YYYYMMDD_HHMMSS",
     "response_timestamp": "YYYYMMDD_HHMMSS",
     "analysis": {
       "root_cause": "根本原因の説明",
       "recommendations": [
         {
           "priority": 1,
           "title": "推奨事項1",
           "description": "具体的な説明",
           "code_example": "コード例（あれば）"
         }
       ]
     },
     "implementation_steps": [
       "ステップ1: 具体的な作業内容",
       "ステップ2: 具体的な作業内容"
     ],
     "code_files": {
       "src/filename.py": "改善されたコード全文"
     },
     "additional_notes": "追加の注意事項"
   }
   ```

4. **回答を保存**
   ```
   ~/AI-Workspace/claude-bridge/help-responses/req_YYYYMMDD_HHMMSS_response.json
   ```

## Claude Code側の回答確認

```python
from bridge_helper import ClaudeBridge

# 回答をチェック
bridge = ClaudeBridge()
response = bridge.check_response("req_YYYYMMDD_HHMMSS")

if response:
    # 推奨事項に従って実装
    print("実装開始...")
```

## 重要な原則

### ❌ やってはいけないこと

1. **無駄に時間を使わない**
   - 3回失敗したら諦めて申告
   - 10分以上悩んだら申告

2. **推測で実装しない**
   - 設計判断が必要なら申告
   - 影響範囲が不明なら申告

3. **複雑化させない**
   - コードが複雑すぎると感じたら申告
   - リファクタリングが必要そうなら申告

### ✅ やるべきこと

1. **早めに申告**
   - 迷ったら申告（コストは低い）
   - 手遅れになる前に申告

2. **具体的に説明**
   - 何を達成したいか明確に
   - 何を試したか詳細に
   - エラーメッセージは全文

3. **回答を活用**
   - 提案を理解してから実装
   - 段階的に実装
   - 結果を確認しながら進める

## トラブルシューティング

### ヘルプリクエストが作成できない

```bash
# bridge_helper.pyのパスを確認
ls ~/AI-Workspace/claude-bridge/bridge_helper.py

# Pythonパスを確認
python -c "import sys; print('\n'.join(sys.path))"
```

### 回答が見つからない

```python
# 未回答リクエスト一覧
from bridge_helper import ClaudeBridge
ClaudeBridge().list_pending_requests()
```

### 完了したリクエストをアーカイブ

```python
from bridge_helper import ClaudeBridge
ClaudeBridge().archive_completed("req_YYYYMMDD_HHMMSS")
```

## まとめ

このプロトコルの目的は：
- Claude Codeが無駄に時間を使わないこと
- 設計判断の質を上げること
- プロジェクトの進行を加速すること

**迷ったら申告！** これが最も重要な原則です。
