# 🎉 Claude Bridge セットアップ完了

おめでとうございます！Claude Code ⇄ Claude Desktop の連携システムが構築されました。

## 📦 作成されたファイル

```text
~/Ai-Workspace/claude-bridge/
├── bridge_helper.py                  # ✅ ヘルパー関数
├── CLAUDE_PROTOCOL_TEMPLATE.md       # ✅ CLAUDE.mdテンプレート
├── README.md                         # ✅ 詳細ドキュメント
├── test_bridge.py                    # ✅ テストスクリプト
├── QUICKSTART.md                     # ✅ このファイル
├── help-requests/                    # ✅ リクエスト格納先
├── help-responses/                   # ✅ 回答格納先
└── archive/                          # ✅ アーカイブ
```

## 🚀 今すぐ試す（3ステップ）

### ステップ1: テスト実行

ターミナルで以下を実行：

```bash
cd ~/Ai-Workspace/claude-bridge
python test_bridge.py --full
```

これにより：

1. テストリクエストが作成される
2. サンプル回答が生成される
3. 回答の読み込みが確認される

### ステップ2: 既存プロジェクトに追加

例: kitakyu-netプロジェクト

```bash
# プロジェクトのCLAUDE.mdに追加
cd ~/Projects/kitakyu-net
cat ~/Ai-Workspace/claude-bridge/CLAUDE_PROTOCOL_TEMPLATE.md >> CLAUDE.md
```

または、CLAUDE.mdを開いて手動で内容をコピー＆ペースト。

### ステップ3: 実際に使ってみる

Claude Codeで実装中に困難に直面したら：

```python
# プロジェクト内で
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "Ai-Workspace/claude-bridge"))

from bridge_helper import ask_claude_desktop

request_id = ask_claude_desktop(
    title="問題のタイトル",
    problem="具体的な問題の説明",
    tried=["試したこと1", "試したこと2"],
    files=["src/file1.py", "src/file2.py"],
    error="エラーメッセージ"
)
```

## 💡 実践例

### 例1: Neo4jのパフォーマンス問題

**Claude Code (kitakyu-netプロジェクト内):**

```python
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "Ai-Workspace/claude-bridge"))
from bridge_helper import ask_claude_desktop

ask_claude_desktop(
    title="施設検索クエリが遅い",
    problem="5000施設のデータで検索に10秒以上かかる。目標は3秒以内。",
    tried=[
        "インデックス追加 → 効果なし",
        "LIMIT句追加 → データ不完全",
        "クエリ分割 → さらに遅化"
    ],
    files=[
        "src/wamnet_loader.py",
        "src/neo4j_queries.py",
        "tests/performance_test.log"
    ],
    error="Query execution time: 12.3 seconds"
)
```

→ 画面に表示される指示に従ってClaude Desktopを開く

**Claude Desktop:**

```text
ヘルプリクエストの分析をお願いします。
以下のファイルを確認してください:

~/Ai-Workspace/claude-bridge/help-requests/req_20250104_143022.json
```

→ 分析結果を `help-responses/req_20250104_143022_response.json` に保存

**Claude Code:**

```python
from bridge_helper import ClaudeBridge
response = ClaudeBridge().check_response("req_20250104_143022")
# 回答に基づいて実装
```

## 📋 よくある質問

### Q1: いつヘルプを求めるべき？

**A:** 以下のいずれか：

- 同じエラーが3回以上
- 10分以上進展なし
- 設計判断が必要
- 影響範囲が不明

### Q2: ファイルをどこに配置すれば？

**A:** どのプロジェクトからでも使えます：

```python
# どこからでもアクセス可能
import sys
from pathlib import Path
sys.path.append(str(Path.home() / "Ai-Workspace/claude-bridge"))
from bridge_helper import ask_claude_desktop
```

### Q3: Claude Desktopへの通知を自動化できる？

**A:** 現時点では手動ですが、以下で効率化：

```bash
# ターミナルエイリアスを追加
echo 'alias check-help="python ~/Ai-Workspace/claude-bridge/test_bridge.py --list"' >> ~/.zshrc
source ~/.zshrc

# 使用
check-help  # 未回答リクエスト一覧
```

### Q4: 複数プロジェクトで同時に使える？

**A:** はい！リクエストには `project_root` が記録されるので混乱しません。

## 🎯 次のステップ

### 1. 実際のプロジェクトで使う

```bash
cd ~/Projects/kitakyu-net  # または他のプロジェクト
# CLAUDE.mdにプロトコルを追加
cat ~/Ai-Workspace/claude-bridge/CLAUDE_PROTOCOL_TEMPLATE.md >> CLAUDE.md
```

### 2. Claude Codeに慣れさせる

CLAUDE.mdの最後に以下を追加：

```markdown
## 重要: ヘルプリクエストシステム

このプロジェクトでは、困難に直面した時に自動的に
Claude Desktopに助けを求めるシステムを使用します。

詳細は上記の「Claude Code ⇄ Claude Desktop 連携プロトコル」を参照。

**必ず覚えること:**
- 3回失敗したら即座にヘルプリクエスト
- 10分以上悩んだら即座にヘルプリクエスト
- 設計判断が必要なら即座にヘルプリクエスト
```

### 3. ワークフローに組み込む

毎日の作業開始時：

```bash
cd ~/Ai-Workspace/claude-bridge
python test_bridge.py --list  # 未回答確認
```

毎日の作業終了時：

```python
# 完了したリクエストをアーカイブ
from bridge_helper import ClaudeBridge
bridge = ClaudeBridge()
# bridge.archive_completed("req_XXXXXX")
```

## 📚 詳細ドキュメント

- **README.md**: 全体の説明と詳細な使い方
- **CLAUDE_PROTOCOL_TEMPLATE.md**: プロジェクトに追加するテンプレート
- **test_bridge.py**: テストとサンプル

## 🎊 完成

これで、Claude CodeとClaude Desktopの効率的な連携が可能になりました。

**ポイント:**

1. 迷ったら即座にヘルプリクエスト
2. 無駄に時間を使わない
3. 設計の質が上がる
4. プロジェクトが加速する

質問があれば、Claude Desktopでこのドキュメントを開いて相談してください！
