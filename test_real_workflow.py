#!/usr/bin/env python3
"""
実環境テストスクリプト

実際のClaude Desktopと連携して自動化ワークフローをテストします。
"""

import sys
import time
from pathlib import Path
from automation_helper import AutomatedBridge, AutomationConfig


def test_real_automated_workflow():
    """実際のClaude Desktopと連携した自動化ワークフローのテスト"""
    print("=" * 60)
    print("  実環境テスト: 自動化ワークフロー")
    print("=" * 60)
    print()

    # 設定作成
    print("1. 設定ファイルの作成...")
    config = AutomationConfig()

    # 実環境テスト用の設定調整
    config.auto_launch_desktop = True  # Claude Desktopを自動起動
    config.launch_timeout = 30  # 起動タイムアウト30秒
    config.response_timeout = 300  # レスポンス待機5分（実環境テスト用）
    config.polling_interval = 2.0  # ポーリング間隔2秒

    print(f"   auto_launch_desktop: {config.auto_launch_desktop}")
    print(f"   launch_timeout: {config.launch_timeout}秒")
    print(f"   response_timeout: {config.response_timeout}秒")
    print()

    # テスト用ファイルの作成
    print("2. テスト用コードファイルの作成...")
    test_dir = Path.cwd() / "test_files"
    test_dir.mkdir(exist_ok=True)

    test_file = test_dir / "sample_code.py"
    test_file.write_text("""# サンプルコード
def slow_function(data):
    # パフォーマンス問題のあるコード
    result = []
    for item in data:
        for i in range(len(data)):
            result.append(item * i)
    return result

# 使用例
data = list(range(1000))
result = slow_function(data)
print(f"結果の要素数: {len(result)}")
""", encoding="utf-8")

    print(f"   作成されたファイル: {test_file}")
    print()

    # 自動化ブリッジの作成
    print("3. 自動化ブリッジの初期化...")
    bridge = AutomatedBridge(config)
    print("   ✅ 初期化完了")
    print()

    # ワークフロー実行
    print("4. 自動化ワークフローの実行...")
    print()
    print("   以下の問題についてClaude Desktopに相談します:")
    print("   ---")
    print("   タイトル: パフォーマンス改善が必要")
    print("   問題: slow_function が遅すぎる（O(n²)）")
    print("   試行: ループの最適化、リスト内包表記")
    print("   分析ファイル: sample_code.py")
    print("   ---")
    print()

    try:
        response = bridge.run_automated_workflow(
            title="パフォーマンス改善が必要",
            problem="""
            slow_function関数が非常に遅い:
            - 現状: 1000要素で数秒かかる
            - 計算量: O(n²)
            - 目標: O(n)またはそれ以下に改善
            """,
            tried=[
                "ループの最適化を試みた → まだ遅い",
                "リスト内包表記に変更 → 若干改善のみ"
            ],
            files_to_analyze=[str(test_file)]
        )

        print()
        print("=" * 60)
        print("  テスト結果")
        print("=" * 60)
        print()

        if response:
            print("✅ レスポンスを受信しました")
            print()
            print("レスポンスの内容:")
            print(f"  リクエストID: {response.get('request_id', 'N/A')}")
            print(f"  タイムスタンプ: {response.get('response_timestamp', 'N/A')}")

            analysis = response.get('analysis', {})
            if analysis:
                print()
                print("分析結果:")
                print(f"  根本原因: {analysis.get('root_cause', 'N/A')}")

                recommendations = analysis.get('recommendations', [])
                if recommendations:
                    print()
                    print("推奨事項:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"  {i}. {rec.get('title', 'N/A')}")
                        print(f"     {rec.get('description', 'N/A')}")

                steps = analysis.get('implementation_steps', [])
                if steps:
                    print()
                    print("実装ステップ:")
                    for i, step in enumerate(steps, 1):
                        print(f"  {i}. {step.get('description', 'N/A')}")

            print()
            print("🎉 自動化ワークフローが正常に完了しました！")
            return True
        else:
            print("⚠️  レスポンスを受信できませんでした")
            print()
            print("以下を確認してください:")
            print("  1. Claude Desktopが起動しているか")
            print("  2. help-requests/ディレクトリにリクエストファイルが作成されているか")
            print("  3. Claude Desktopでリクエストを分析し、レスポンスファイルを作成したか")
            return False

    except Exception as e:
        print()
        print("❌ エラーが発生しました:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # クリーンアップ
        print()
        print("5. クリーンアップ...")
        if test_file.exists():
            test_file.unlink()
            print(f"   削除: {test_file}")
        if test_dir.exists() and not list(test_dir.iterdir()):
            test_dir.rmdir()
            print(f"   削除: {test_dir}")
        print()


def test_manual_mode_comparison():
    """手動モードとの比較テスト"""
    print("=" * 60)
    print("  手動モードとの比較")
    print("=" * 60)
    print()

    from bridge_helper import ask_claude_desktop

    # 手動モードでリクエスト作成のみ
    print("手動モード: リクエスト作成のみ")
    request_id = ask_claude_desktop(
        title="手動モードテスト",
        problem="これは手動モードのテストです",
        tried=["自動モードと比較中"],
        files=[],
        error=""
    )

    print(f"✅ リクエストID: {request_id}")
    print()
    print("手動モードでは:")
    print("  1. リクエストファイルが作成される")
    print("  2. Claude Desktopを手動で起動する必要がある")
    print("  3. レスポンスファイルを手動で確認する必要がある")
    print("  4. 提案を手動で実装する必要がある")
    print()
    print("自動モードでは:")
    print("  1. リクエストファイルが作成される")
    print("  2. Claude Desktopが自動で起動される")
    print("  3. レスポンスが自動で検出される")
    print("  4. 提案が自動で実行される（バックアップ付き）")
    print()


if __name__ == "__main__":
    print()
    print("🚀 Claude Bridge 実環境テスト")
    print()

    # テスト実行
    print("テスト1: 自動化ワークフローの実環境テスト")
    print("-" * 60)
    test_result = test_real_automated_workflow()
    print()

    print("テスト2: 手動モードとの比較")
    print("-" * 60)
    test_manual_mode_comparison()
    print()

    # 結果サマリー
    print("=" * 60)
    print("  テスト結果サマリー")
    print("=" * 60)
    print()

    if test_result:
        print("✅ 自動化ワークフローが正常に動作しました")
        print()
        print("次のステップ:")
        print("  1. EXAMPLES.mdで実用例を確認")
        print("  2. 実際のプロジェクトで自動モードを試す")
        print("  3. 設定を自分のワークフローに合わせて調整")
        sys.exit(0)
    else:
        print("⚠️  一部のテストが完了しませんでした")
        print()
        print("トラブルシューティング:")
        print("  1. Claude Desktopが正しくインストールされているか確認")
        print("  2. automation_config.jsonの設定を確認")
        print("  3. help-requests/ディレクトリの権限を確認")
        sys.exit(1)
