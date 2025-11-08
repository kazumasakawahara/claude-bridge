#!/usr/bin/env python3
"""
手動テストスクリプト

Claude Code ⇄ Claude Desktop Bridgeの手動テストシナリオを実行します。
"""

import sys
from pathlib import Path
from automation_helper import (
    AutomationConfig,
    DesktopLauncher,
    ResponseMonitor,
    AutomatedBridge,
    ProposalExecutor,
    ErrorHandler,
    CheckpointManager
)


def print_header(title: str):
    """ヘッダーを表示"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_scenario_1_config_management():
    """シナリオ1: 設定管理のテスト"""
    print_header("シナリオ1: 設定管理")

    # 1. デフォルト設定の作成
    print("1. デフォルト設定を作成...")
    config = AutomationConfig()
    print(f"   auto_launch_desktop: {config.auto_launch_desktop}")
    print(f"   launch_timeout: {config.launch_timeout}")
    print(f"   response_timeout: {config.response_timeout}")

    # 2. 設定の検証
    print("\n2. 設定を検証...")
    is_valid = config.validate_config()
    print(f"   検証結果: {'✅ 有効' if is_valid else '❌ 無効'}")

    # 3. 設定の変更
    print("\n3. 設定を変更...")
    config.auto_launch_desktop = False
    config.launch_timeout = 30
    print(f"   auto_launch_desktop: {config.auto_launch_desktop}")
    print(f"   launch_timeout: {config.launch_timeout}")

    print("\n✅ シナリオ1完了")
    return True


def test_scenario_2_error_handling():
    """シナリオ2: エラーハンドリングのテスト"""
    print_header("シナリオ2: エラーハンドリング")

    config = AutomationConfig()
    handler = ErrorHandler(config)

    # 1. 警告レベルエラー
    print("1. 警告レベルエラーのテスト...")
    error = ValueError("Invalid input")
    can_continue = handler.handle_error(error, "validation")
    print(f"   継続可能: {can_continue}")

    # 2. 回復可能エラー
    print("\n2. 回復可能エラーのテスト...")
    error = FileNotFoundError("config.json not found")
    can_continue = handler.handle_error(error, "file_operation")
    print(f"   継続可能: {can_continue}")

    # 3. 致命的エラー
    print("\n3. 致命的エラーのテスト...")
    error = MemoryError("Out of memory")
    can_continue = handler.handle_error(error, "system_crash")
    print(f"   継続可能: {can_continue}")

    print("\n✅ シナリオ2完了")
    return True


def test_scenario_3_checkpoint_rollback():
    """シナリオ3: チェックポイントとロールバックのテスト"""
    print_header("シナリオ3: チェックポイントとロールバック")

    import tempfile
    import shutil

    config = AutomationConfig()
    manager = CheckpointManager(config)

    # テストファイル作成
    temp_dir = Path(tempfile.mkdtemp())
    test_file = temp_dir / "test_file.txt"

    try:
        # 1. 初期ファイル作成
        print("1. テストファイルを作成...")
        test_file.write_text("Original content v1", encoding="utf-8")
        print(f"   内容: {test_file.read_text(encoding='utf-8')}")

        # 2. チェックポイント作成
        print("\n2. チェックポイントを作成...")
        checkpoint_id = manager.create_checkpoint(
            files=[str(test_file)],
            description="Before modification"
        )
        print(f"   チェックポイントID: {checkpoint_id}")

        # 3. ファイル変更
        print("\n3. ファイルを変更...")
        test_file.write_text("Modified content v2", encoding="utf-8")
        print(f"   新しい内容: {test_file.read_text(encoding='utf-8')}")

        # 4. ロールバック
        print("\n4. ロールバックを実行...")
        result = manager.rollback(checkpoint_id)
        print(f"   ロールバック結果: {'✅ 成功' if result else '❌ 失敗'}")

        # 5. 復元確認
        print("\n5. 復元を確認...")
        restored_content = test_file.read_text(encoding="utf-8")
        print(f"   復元された内容: {restored_content}")
        print(f"   復元成功: {'✅ はい' if restored_content == 'Original content v1' else '❌ いいえ'}")

        print("\n✅ シナリオ3完了")
        return True

    finally:
        # クリーンアップ
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def test_scenario_4_proposal_execution():
    """シナリオ4: 提案実行のテスト"""
    print_header("シナリオ4: 提案実行")

    config = AutomationConfig()
    executor = ProposalExecutor(config)

    # モックレスポンス
    mock_response = {
        "analysis": {
            "recommendations": [
                {"title": "Optimize Query", "description": "Add index to users table"},
                {"title": "Cache Results", "description": "Implement Redis caching"}
            ],
            "implementation_steps": [
                {"step": 1, "description": "Create index", "action": "ALTER TABLE users ADD INDEX"},
                {"step": 2, "description": "Setup Redis", "action": "Install redis-py"},
                {"step": 3, "description": "Implement cache", "action": "Add cache decorator"}
            ],
            "code_files": []
        }
    }

    # 1. 推奨事項の表示
    print("1. 提案サマリーを表示...")
    executor.show_proposal_summary(mock_response)

    # 2. 実装ステップの抽出
    print("\n2. 実装ステップを抽出...")
    steps = executor.extract_implementation_steps(mock_response)
    print(f"   ステップ数: {len(steps)}")

    # 3. ステップの実行（デモ）
    print("\n3. 実装ステップを実行...")
    results = executor.execute_all_steps(steps)
    print(f"   実行結果: {len([r for r in results if r])}/{len(results)} 成功")

    print("\n✅ シナリオ4完了")
    return True


def run_all_scenarios():
    """全シナリオを実行"""
    print_header("手動テストシナリオ実行開始")

    scenarios = [
        ("設定管理", test_scenario_1_config_management),
        ("エラーハンドリング", test_scenario_2_error_handling),
        ("チェックポイント/ロールバック", test_scenario_3_checkpoint_rollback),
        ("提案実行", test_scenario_4_proposal_execution)
    ]

    results = []
    for name, scenario_func in scenarios:
        try:
            result = scenario_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ シナリオ '{name}' でエラー: {e}")
            results.append((name, False))

    # 結果サマリー
    print_header("テスト結果サマリー")
    for name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"  {name}: {status}")

    success_count = sum(1 for _, result in results if result)
    total_count = len(results)

    print(f"\n総合結果: {success_count}/{total_count} シナリオ成功")

    if success_count == total_count:
        print("\n🎉 全シナリオが成功しました！")
        return 0
    else:
        print("\n⚠️  一部のシナリオが失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_scenarios())
