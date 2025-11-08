# 実環境テストガイド

Claude Bridge自動化機能の実環境テスト手順書です。

## 📋 テスト準備

### 前提条件

1. ✅ Claude Desktopがインストールされている
2. ✅ macOS環境（Claude Desktop自動起動機能）
3. ✅ Python 3.7以上
4. ✅ `~/AI-Workspace/claude-bridge/`ディレクトリが存在

### セットアップ確認

```bash
cd ~/AI-Workspace/claude-bridge/

# ファイルの存在確認
ls -la automation_helper.py
ls -la test_real_workflow.py

# Pythonバージョン確認
python3 --version
```

---

## 🧪 テスト1: 自動テストスイート

### 単体テスト（76テスト）

```bash
cd ~/AI-Workspace/claude-bridge/
python3 test_automation.py
```

**期待される結果:**
```
Ran 76 tests in X.XXXs
OK
```

### 手動テストシナリオ（4シナリオ）

```bash
python3 manual_test.py
```

**期待される結果:**
```
総合結果: 4/4 シナリオ成功
🎉 全シナリオが成功しました！
```

### パフォーマンステスト（5ベンチマーク）

```bash
python3 performance_test.py
```

**期待される結果:**
```
総合結果: 4/5 テスト合格
⚠️  一部のテストが不合格です
```

**注意:** 要件6.1（起動検知性能）は実際のアプリケーション起動なしでは不合格になります。これは正常です。

---

## 🚀 テスト2: 実環境ワークフロー

### 準備ステップ

1. **設定ファイルの作成**

```python
# Python対話モードで実行
python3
```

```python
from automation_helper import AutomationConfig

config = AutomationConfig()
config.save("automation_config.json")
exit()
```

2. **設定の確認**

```bash
cat automation_config.json
```

期待される内容:
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

### テスト実行

#### オプション1: 自動テストスクリプト使用

```bash
python3 test_real_workflow.py
```

**このスクリプトは以下を実行します:**
1. テスト用コードファイルの作成
2. 自動化ブリッジの初期化
3. Claude Desktopへのリクエスト送信
4. レスポンスの監視
5. 結果の表示

**注意:** 実際のClaude Desktopとの連携テストのため、以下が必要です:
- Claude Desktopが起動可能な状態
- レスポンスファイルを手動で作成するか、Claude Desktopで分析

#### オプション2: 手動での実行

1. **Pythonスクリプト作成**

```python
# test_manual_run.py
from automation_helper import AutomatedBridge

bridge = AutomatedBridge()

response = bridge.run_automated_workflow(
    title="実環境テスト",
    problem="これは自動化機能の実環境テストです",
    tried=["単体テスト完了", "ドキュメント作成完了"],
    files_to_analyze=[]
)

if response:
    print("✅ 成功: レスポンスを受信")
    print(response)
else:
    print("⚠️  レスポンスなし")
```

2. **実行**

```bash
python3 test_manual_run.py
```

3. **Claude Desktopでの操作**

自動起動が失敗した場合、手動で以下を実行:

```
Claude Desktopを開いて以下を入力:

ヘルプリクエストの分析をお願いします。
~/AI-Workspace/claude-bridge/help-requests/req_XXXXXXXX_XXXXXX.json
```

4. **レスポンスファイルの作成**

Claude Desktopで分析後、以下の形式でレスポンスを作成:

```json
{
  "request_id": "req_XXXXXXXX_XXXXXX",
  "response_timestamp": "YYYYMMDD_HHMMSS",
  "analysis": {
    "root_cause": "テスト用の分析",
    "recommendations": [
      {
        "priority": 1,
        "title": "テスト推奨事項1",
        "description": "これはテストです"
      }
    ],
    "implementation_steps": [
      {
        "step": 1,
        "description": "テストステップ1",
        "action": "何もしない"
      }
    ],
    "code_files": []
  }
}
```

保存先: `~/AI-Workspace/claude-bridge/help-responses/req_XXXXXXXX_XXXXXX_response.json`

---

## ✅ テスト3: バックアップとロールバック

### バックアップ機能のテスト

1. **テストファイル作成**

```bash
cd ~/AI-Workspace/claude-bridge/
echo "# Original content" > test_backup.py
```

2. **バックアップテスト実行**

```python
from automation_helper import ProposalExecutor, AutomationConfig

config = AutomationConfig()
executor = ProposalExecutor(config)

# バックアップ作成
backup_path = executor.create_backup("test_backup.py")
print(f"バックアップ作成: {backup_path}")

# ファイル変更
with open("test_backup.py", "w") as f:
    f.write("# Modified content")

# バックアップ確認
print(f"元のファイル: {open('test_backup.py').read()}")
print(f"バックアップ: {open(backup_path).read()}")
```

**期待される結果:**
- `backups/`ディレクトリにバックアップファイルが作成される
- タイムスタンプ付きのファイル名（例: `test_backup_20251109_143022.py`）

### ロールバック機能のテスト

```python
from automation_helper import CheckpointManager, AutomationConfig

config = AutomationConfig()
manager = CheckpointManager(config)

# テストファイル作成
with open("test_rollback.py", "w") as f:
    f.write("# Original")

# チェックポイント作成
checkpoint_id = manager.create_checkpoint(
    files=["test_rollback.py"],
    description="Test checkpoint"
)
print(f"チェックポイント作成: {checkpoint_id}")

# ファイル変更
with open("test_rollback.py", "w") as f:
    f.write("# Modified")

# ロールバック
result = manager.rollback(checkpoint_id)
print(f"ロールバック: {'成功' if result else '失敗'}")

# 復元確認
content = open("test_rollback.py").read()
print(f"ファイル内容: {content}")
assert content == "# Original", "ロールバック失敗"
print("✅ ロールバックテスト成功")
```

---

## 🔍 テスト4: エラーハンドリング

### エラー分類のテスト

```python
from automation_helper import ErrorHandler, AutomationConfig

config = AutomationConfig()
handler = ErrorHandler(config)

# 警告レベルエラー
error = ValueError("Invalid input")
can_continue = handler.handle_error(error, "validation")
print(f"警告エラー: 継続可能={can_continue}")

# 回復可能エラー
error = FileNotFoundError("config.json")
can_continue = handler.handle_error(error, "file_operation")
print(f"回復可能エラー: 継続可能={can_continue}")

# 致命的エラー
error = MemoryError("Out of memory")
can_continue = handler.handle_error(error, "system_crash")
print(f"致命的エラー: 継続可能={can_continue}")
```

**期待される結果:**
- 警告エラー: `True`（継続可能）
- 回復可能エラー: `True`（継続可能）
- 致命的エラー: `False`（継続不可）

### エラーログの確認

```bash
ls -la logs/
cat logs/error_*.log | tail -20
```

---

## 📊 テスト結果の確認

### チェックリスト

- [ ] 単体テスト: 76/76 合格
- [ ] 手動テスト: 4/4 シナリオ成功
- [ ] パフォーマンステスト: 4/5 合格（要件6.1は除く）
- [ ] 実環境ワークフロー: レスポンス受信成功
- [ ] バックアップ: 正常に作成される
- [ ] ロールバック: 正常に復元される
- [ ] エラーハンドリング: 適切に分類される
- [ ] ログ: エラー情報が記録される

### トラブルシューティング

#### 問題1: Claude Desktopが起動しない

**原因:** アプリケーションパスが正しくない、または権限がない

**解決策:**
```python
# 設定で手動モードに切り替え
config = AutomationConfig()
config.auto_launch_desktop = False
config.save("automation_config.json")
```

#### 問題2: レスポンスタイムアウト

**原因:** レスポンスファイルの作成に時間がかかっている

**解決策:**
```python
# タイムアウトを延長
config = AutomationConfig()
config.response_timeout = 3600  # 1時間
config.save("automation_config.json")
```

#### 問題3: ImportError

**原因:** Pythonパスが正しく設定されていない

**解決策:**
```python
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))
```

#### 問題4: PermissionError

**原因:** ディレクトリやファイルの権限が不足

**解決策:**
```bash
chmod -R u+w ~/AI-Workspace/claude-bridge/
```

---

## 🎯 成功基準

以下の条件を満たせばテスト成功です:

1. **自動テスト**:
   - 単体テスト: 100% 合格
   - 手動テスト: 100% 成功
   - パフォーマンステスト: 80% 合格

2. **実環境テスト**:
   - リクエストファイルが正しく作成される
   - レスポンスファイルが検出される
   - バックアップが正常に動作する

3. **安全機構**:
   - ロールバックが正常に動作する
   - エラーが適切に分類される
   - ログが正しく記録される

---

## 📝 次のステップ

テストが成功したら:

1. ✅ [EXAMPLES.md](EXAMPLES.md)で実用例を確認
2. ✅ 実際のプロジェクトで小さな問題から試す
3. ✅ 設定を自分のワークフローに合わせて調整
4. ✅ フィードバックを記録して改善

テストで問題が見つかったら:

1. ❌ エラーログを確認（`logs/`ディレクトリ）
2. ❌ 設定を見直す（`automation_config.json`）
3. ❌ トラブルシューティングセクションを参照
4. ❌ 必要に応じて手動モードに切り替え
