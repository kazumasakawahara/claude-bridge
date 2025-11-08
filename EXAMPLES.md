# Claude Bridge 使用例集

このドキュメントでは、Claude Code ⇄ Claude Desktop Bridgeの実際の使用例を紹介します。

## 📚 目次

1. [パフォーマンス問題の解決](#1-パフォーマンス問題の解決)
2. [設計判断のサポート](#2-設計判断のサポート)
3. [複雑なバグの調査](#3-複雑なバグの調査)
4. [アーキテクチャの改善](#4-アーキテクチャの改善)
5. [テスト戦略の立案](#5-テスト戦略の立案)

---

## 1. パフォーマンス問題の解決

### 状況
Neo4jを使用した支援ネットワーク取得が遅く、ユーザー体験が悪化している。

### 自動モードでの解決

```python
from automation_helper import AutomatedBridge

bridge = AutomatedBridge()

# 完全自動ワークフロー
response = bridge.run_automated_workflow(
    title="Neo4jクエリのパフォーマンス改善",
    problem="""
    支援ネットワーク取得クエリが遅い:
    - 現状: 5000ノードで12秒
    - 目標: 3秒以内
    - ユーザー体験への影響: 大
    """,
    tried=[
        "単純なインデックス追加 → 効果なし（11秒）",
        "LIMIT句で制限 → データ不完全",
        "クエリ分割 → さらに遅化（15秒）",
        "キャッシュ導入 → 初回が遅い問題残る"
    ],
    files_to_analyze=[
        "src/queries.py",
        "src/neo4j_client.py",
        "logs/query_performance.log"
    ]
)

# 自動的に実行される:
# 1. リクエスト作成
# 2. Claude Desktop起動
# 3. レスポンス監視
# 4. 提案の自動実行:
#    - クエリ最適化（MATCH句の順序変更）
#    - 複合インデックス追加
#    - バッチ処理の導入
# 5. バックアップ作成（元のコードは安全に保存）
```

### Claude Desktopからの回答例

```json
{
  "analysis": {
    "root_cause": "MATCH句の順序が非効率。最も選択性の低いパターンから始まっている",
    "recommendations": [
      {
        "priority": 1,
        "title": "クエリの最適化",
        "description": "MATCH句の順序を変更し、最も選択性の高いパターンから開始"
      },
      {
        "priority": 2,
        "title": "複合インデックスの追加",
        "description": "Person.id と relationship type の複合インデックス作成"
      }
    ],
    "implementation_steps": [
      {
        "step": 1,
        "description": "クエリパターンの最適化",
        "action": "MATCH (p:Person {id: $id}) を最初に実行"
      },
      {
        "step": 2,
        "description": "複合インデックス作成",
        "action": "CREATE INDEX person_service_idx FOR ..."
      }
    ],
    "code_files": [
      {
        "path": "src/queries.py",
        "content": "def get_support_network(person_id):\n    # 最適化されたクエリ\n    ..."
      }
    ]
  }
}
```

### 結果
- **実行時間**: 12秒 → 2.1秒（82%改善）
- **バックアップ**: 元のコードは`backups/queries_20251109_143022.py`に保存
- **ロールバック可能**: 問題があれば即座に元に戻せる

---

## 2. 設計判断のサポート

### 状況
エコマップのデータモデルが複雑化し、保守性が低下している。

### 自動モードでの解決

```python
from automation_helper import AutomatedBridge

bridge = AutomatedBridge()

response = bridge.run_automated_workflow(
    title="エコマップデータモデルの設計改善",
    problem="""
    Person-Service間のリレーションが複雑すぎて管理困難:
    - 関係の種類が15種類以上
    - クエリが複雑化（100行超）
    - 新しい関係の追加が困難
    - テストが書きにくい
    """,
    tried=[
        "正規化 → クエリがさらに複雑化",
        "非正規化 → データ重複と整合性問題",
        "中間ノード追加 → さらに複雑化",
        "リレーション統合 → 情報損失"
    ],
    files_to_analyze=[
        "src/models/ecomap.py",
        "src/queries/ecomap_queries.py",
        "docs/data_model.md",
        "tests/test_ecomap.py"
    ]
)
```

### Claude Desktopからの提案

```json
{
  "analysis": {
    "root_cause": "ドメインモデルとグラフモデルの不一致",
    "recommendations": [
      {
        "priority": 1,
        "title": "リレーションシップの階層化",
        "description": "基本リレーション + 属性パターンの採用"
      },
      {
        "priority": 2,
        "title": "ドメイン駆動設計の導入",
        "description": "集約ルートとエンティティの明確化"
      }
    ],
    "implementation_steps": [
      {
        "step": 1,
        "description": "基本リレーションの定義",
        "action": "PROVIDES, RECEIVES, SUPPORTS の3つに統合"
      },
      {
        "step": 2,
        "description": "属性での詳細化",
        "action": "relationship に type, intensity, frequency 属性を追加"
      },
      {
        "step": 3,
        "description": "段階的移行",
        "action": "既存データの変換スクリプト作成"
      }
    ]
  }
}
```

### 結果
- **リレーション種類**: 15種類 → 3種類（属性で表現）
- **クエリの簡潔さ**: 100行 → 25行
- **テストカバレッジ**: 45% → 87%
- **段階的移行**: 既存システムを止めずに実施

---

## 3. 複雑なバグの調査

### 状況
本番環境でのみ発生する間欠的なメモリリーク。

### 自動モードでの解決

```python
from automation_helper import AutomatedBridge

bridge = AutomatedBridge()

response = bridge.run_automated_workflow(
    title="本番環境でのメモリリーク調査",
    problem="""
    本番環境で6時間後にメモリ使用量が2GB→8GBに増加:
    - 開発環境では再現しない
    - ログに明確なエラーなし
    - 特定の操作パターンで発生？
    - アプリケーション再起動で一時的に解消
    """,
    tried=[
        "メモリプロファイリング → 開発環境で異常なし",
        "ログレベル上げ → 手がかりなし",
        "キャッシュクリア追加 → 効果なし",
        "タイムアウト設定 → 部分的改善のみ"
    ],
    files_to_analyze=[
        "src/api/endpoints.py",
        "src/services/cache_service.py",
        "src/db/connection_pool.py",
        "logs/production_memory.log",
        "monitoring/grafana_metrics.png"
    ]
)
```

### Claude Desktopの分析

```json
{
  "analysis": {
    "root_cause": "データベース接続プールのリークと循環参照",
    "recommendations": [
      {
        "priority": 1,
        "title": "接続プールの適切なクローズ",
        "description": "context manager を使用した確実なリソース解放"
      },
      {
        "priority": 2,
        "title": "弱参照の使用",
        "description": "キャッシュオブジェクトに weakref を使用"
      },
      {
        "priority": 3,
        "title": "定期的なガベージコレクション",
        "description": "長時間実行APIに gc.collect() を追加"
      }
    ],
    "implementation_steps": [
      {
        "step": 1,
        "description": "接続プールのリファクタリング",
        "action": "with文による自動クローズ実装"
      },
      {
        "step": 2,
        "description": "キャッシュの改善",
        "action": "weakref.WeakValueDictionary 使用"
      },
      {
        "step": 3,
        "description": "監視強化",
        "action": "メモリ使用量の詳細ログ追加"
      },
      {
        "step": 4,
        "description": "段階的デプロイ",
        "action": "カナリアリリースで検証"
      }
    ]
  }
}
```

### 結果
- **メモリ使用量**: 安定（2GB前後を維持）
- **リーク解消**: 24時間稼働でも増加なし
- **監視改善**: 早期検知が可能に
- **安全なデプロイ**: カナリアリリースで問題なし確認

---

## 4. アーキテクチャの改善

### 状況
モノリシックなアプリケーションの責務分離が必要。

### 自動モードでの解決

```python
from automation_helper import AutomatedBridge

bridge = AutomatedBridge()

response = bridge.run_automated_workflow(
    title="アーキテクチャのリファクタリング",
    problem="""
    単一ファイル2000行のアプリケーションを責務分離したい:
    - テストが困難
    - 複数人での並行開発が難しい
    - デプロイリスクが高い
    - 一部機能の再利用ができない
    """,
    tried=[
        "単純な分割 → 循環依存発生",
        "レイヤードアーキテクチャ → 過度に複雑化",
        "マイクロサービス → 運用負荷増大"
    ],
    files_to_analyze=[
        "src/app.py",
        "tests/test_app.py",
        "docs/architecture.md"
    ]
)
```

### Claude Desktopの提案

```json
{
  "analysis": {
    "root_cause": "責務の混在とドメインロジックの散在",
    "recommendations": [
      {
        "priority": 1,
        "title": "クリーンアーキテクチャの導入",
        "description": "ドメイン層、アプリケーション層、インフラ層に分離"
      },
      {
        "priority": 2,
        "title": "依存性の逆転",
        "description": "インターフェースによる疎結合化"
      },
      {
        "priority": 3,
        "title": "段階的移行",
        "description": "ストラングラーパターンで徐々に移行"
      }
    ],
    "implementation_steps": [
      {
        "step": 1,
        "description": "ドメインモデルの抽出",
        "action": "ビジネスロジックを domain/ に移動"
      },
      {
        "step": 2,
        "description": "インターフェース定義",
        "action": "リポジトリとサービスのI/F作成"
      },
      {
        "step": 3,
        "description": "段階的リファクタリング",
        "action": "機能ごとに新アーキテクチャに移行"
      }
    ]
  }
}
```

### 結果
- **ファイル構造**: 1ファイル2000行 → 適切に分離された20ファイル
- **テストカバレッジ**: 30% → 85%
- **並行開発**: 競合なく複数人で作業可能
- **デプロイ**: 変更範囲が明確化、リスク低減

---

## 5. テスト戦略の立案

### 状況
テストが不十分で品質が不安定。効果的なテスト戦略が必要。

### 自動モードでの解決

```python
from automation_helper import AutomatedBridge

bridge = AutomatedBridge()

response = bridge.run_automated_workflow(
    title="包括的なテスト戦略の立案",
    problem="""
    現在のテスト状況:
    - カバレッジ: 35%
    - E2Eテスト: なし
    - 統合テスト: 不十分
    - 本番バグ発生率: 高い

    制約:
    - 開発リソース限定
    - 既存コードの大幅変更は困難
    - CI/CD時間は10分以内に抑制
    """,
    tried=[
        "全機能のテスト追加 → 時間不足で挫折",
        "E2Eテストのみ → 実行時間長すぎ",
        "コードレビュー強化 → 限界あり"
    ],
    files_to_analyze=[
        "src/",
        "tests/",
        ".github/workflows/ci.yml",
        "docs/testing_policy.md"
    ]
)
```

### Claude Desktopの提案

```json
{
  "analysis": {
    "root_cause": "テストピラミッドの欠如と優先順位の不明確さ",
    "recommendations": [
      {
        "priority": 1,
        "title": "テストピラミッドの構築",
        "description": "単体:統合:E2E = 70:20:10 の比率"
      },
      {
        "priority": 2,
        "title": "リスクベーステスティング",
        "description": "ビジネスクリティカルな機能を優先"
      },
      {
        "priority": 3,
        "title": "並列テスト実行",
        "description": "pytest-xdist で実行時間短縮"
      }
    ],
    "implementation_steps": [
      {
        "step": 1,
        "description": "クリティカルパスの特定",
        "action": "ユーザー影響大の機能を洗い出し"
      },
      {
        "step": 2,
        "description": "単体テストの拡充",
        "action": "ドメインロジックのカバレッジ80%達成"
      },
      {
        "step": 3,
        "description": "統合テストの追加",
        "action": "APIエンドポイントの主要フロー"
      },
      {
        "step": 4,
        "description": "E2Eテストの選別",
        "action": "最重要ユーザージャーニーのみ"
      },
      {
        "step": 5,
        "description": "CI最適化",
        "action": "並列実行とキャッシュで高速化"
      }
    ]
  }
}
```

### 結果
- **カバレッジ**: 35% → 82%
- **CI実行時間**: 8分（目標達成）
- **本番バグ**: 70%減少
- **開発速度**: テストの信頼性向上で加速

---

## 🎯 ベストプラクティス

### いつ自動モードを使うべきか

✅ **使うべき場合:**
- 同じ問題に3回以上直面
- 10分以上進展がない
- 設計判断が必要
- 影響範囲が不明確
- 複数ファイルにまたがる変更

❌ **使わなくても良い場合:**
- 単純な構文エラー
- ドキュメントに明確な答え
- 1回目の試行
- 明らかな解決策がある

### 良いリクエストの書き方

```python
# ✅ 良い例
bridge.run_automated_workflow(
    title="具体的で簡潔な問題説明",
    problem="""
    何を達成したいか: [具体的な目標]
    現状: [現在の状況と数値]
    影響: [ユーザーやビジネスへの影響]
    制約: [考慮すべき制約条件]
    """,
    tried=[
        "具体的な試行1 → 具体的な結果（数値付き）",
        "具体的な試行2 → なぜうまくいかなかったか"
    ],
    files_to_analyze=["関連する全ファイル"]
)

# ❌ 悪い例
bridge.run_automated_workflow(
    title="動かない",
    problem="エラーが出る",
    tried=["いろいろ試した"],
    files_to_analyze=[]
)
```

### 自動実行の安全性

自動モードでは以下の安全機構が動作します:

1. **バックアップ**: 変更前のファイルを自動保存
2. **チェックポイント**: 複数ファイル変更の原子性保証
3. **ロールバック**: エラー時の自動復元
4. **ユーザー承認**: 重要な変更は確認プロンプト表示
5. **エラーハンドリング**: 致命的/回復可能/警告の3段階

---

## 📞 トラブルシューティング

### 自動起動が失敗する

```python
# 設定で手動モードに切り替え
config = AutomationConfig()
config.auto_launch_desktop = False
config.save("automation_config.json")
```

### レスポンスタイムアウト

```python
# タイムアウトを延長（秒単位）
config = AutomationConfig()
config.response_timeout = 3600  # 1時間
config.save("automation_config.json")
```

### ロールバックが必要

```python
from automation_helper import CheckpointManager

manager = CheckpointManager()
checkpoints = manager.list_checkpoints()
# 最新のチェックポイントにロールバック
manager.rollback(checkpoints[0]["id"])
```

---

## 🎓 次のステップ

1. **小さな問題で試す**: まずは影響範囲の小さい問題で自動モードを体験
2. **設定を調整**: 自分のワークフローに合わせて設定をカスタマイズ
3. **バックアップを確認**: 自動バックアップの動作を理解
4. **ロールバックを練習**: 安全にロールバックできることを確認
5. **本格的に活用**: 大きな問題にも適用

詳しくは [README.md](README.md) を参照してください。
