"""
自動化機能のテストスイート

このモジュールは、Claude Code ⇄ Claude Desktop Bridgeの
自動化機能に対するユニットテストを提供します。
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestAutomationConfig(unittest.TestCase):
    """自動化設定データ管理機能のテスト"""

    def setUp(self):
        """各テストの前に一時ディレクトリを作成"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config_file = self.test_dir / "automation_config.json"

    def tearDown(self):
        """各テストの後に一時ディレクトリを削除"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_default_config_values(self):
        """デフォルト設定値が正しく定義されていることを確認"""
        from automation_helper import AutomationConfig

        config = AutomationConfig()

        # デフォルト値の検証
        self.assertEqual(config.enabled, True)
        self.assertEqual(config.auto_launch_desktop, True)
        self.assertEqual(config.desktop_app_name, "Claude")
        self.assertEqual(config.launch_timeout, 10)
        self.assertEqual(config.response_timeout, 1800)
        self.assertEqual(config.polling_interval, 1)
        self.assertEqual(config.auto_execute_proposals, False)
        self.assertEqual(config.create_backups, True)
        self.assertEqual(config.max_retries, 3)

    def test_load_config_from_file(self):
        """JSONファイルから設定を読み込めることを確認"""
        from automation_helper import AutomationConfig

        # テスト用の設定ファイルを作成
        test_config = {
            "enabled": False,
            "auto_launch_desktop": False,
            "desktop_app_name": "TestApp",
            "launch_timeout": 15,
            "response_timeout": 3600,
            "polling_interval": 2,
            "auto_execute_proposals": True,
            "create_backups": False,
            "max_retries": 5
        }
        self.config_file.write_text(json.dumps(test_config), encoding="utf-8")

        # 設定ファイルから読み込み
        config = AutomationConfig(str(self.config_file))

        # 読み込まれた値の検証
        self.assertEqual(config.enabled, False)
        self.assertEqual(config.auto_launch_desktop, False)
        self.assertEqual(config.desktop_app_name, "TestApp")
        self.assertEqual(config.launch_timeout, 15)
        self.assertEqual(config.response_timeout, 3600)
        self.assertEqual(config.polling_interval, 2)
        self.assertEqual(config.auto_execute_proposals, True)
        self.assertEqual(config.create_backups, False)
        self.assertEqual(config.max_retries, 5)

    def test_create_default_config_if_not_exists(self):
        """設定ファイルが存在しない場合、デフォルト設定ファイルを生成することを確認"""
        from automation_helper import AutomationConfig

        # 存在しないファイルパスで初期化
        config = AutomationConfig(str(self.config_file))

        # ファイルが生成されたことを確認
        self.assertTrue(self.config_file.exists())

        # 生成されたファイルの内容を確認
        saved_config = json.loads(self.config_file.read_text(encoding="utf-8"))
        self.assertEqual(saved_config["enabled"], True)
        self.assertEqual(saved_config["desktop_app_name"], "Claude")

    def test_config_validation_type_check(self):
        """設定値の型チェックが正しく機能することを確認"""
        from automation_helper import AutomationConfig

        # 不正な型の設定ファイルを作成
        invalid_config = {
            "enabled": "true",  # 文字列(boolであるべき)
            "launch_timeout": "10",  # 文字列(intであるべき)
            "polling_interval": -1  # 負の値(正の値であるべき)
        }
        self.config_file.write_text(json.dumps(invalid_config), encoding="utf-8")

        # 設定読み込み時にデフォルト値が使用されることを確認
        config = AutomationConfig(str(self.config_file))

        # 不正な値はデフォルト値で上書きされる
        self.assertEqual(config.enabled, True)
        self.assertEqual(config.launch_timeout, 10)
        self.assertEqual(config.polling_interval, 1)

    def test_config_save_to_file(self):
        """設定をファイルに保存できることを確認"""
        from automation_helper import AutomationConfig

        config = AutomationConfig()
        config.enabled = False
        config.auto_launch_desktop = False

        # ファイルに保存
        config.save(str(self.config_file))

        # ファイルから読み込んで確認
        loaded_config = json.loads(self.config_file.read_text(encoding="utf-8"))
        self.assertEqual(loaded_config["enabled"], False)
        self.assertEqual(loaded_config["auto_launch_desktop"], False)

    def test_config_partial_override(self):
        """一部の設定値のみを上書きできることを確認"""
        from automation_helper import AutomationConfig

        # 一部の設定のみ含むファイル
        partial_config = {
            "enabled": False,
            "launch_timeout": 20
        }
        self.config_file.write_text(json.dumps(partial_config), encoding="utf-8")

        config = AutomationConfig(str(self.config_file))

        # 指定された値は上書き、その他はデフォルト
        self.assertEqual(config.enabled, False)
        self.assertEqual(config.launch_timeout, 20)
        self.assertEqual(config.desktop_app_name, "Claude")  # デフォルト値
        self.assertEqual(config.polling_interval, 1)  # デフォルト値


class TestAutomationState(unittest.TestCase):
    """自動化状態データ構造のテスト"""

    def test_initial_state(self):
        """初期状態が正しく設定されることを確認"""
        from automation_helper import AutomationState

        state = AutomationState("req_test_123")

        self.assertEqual(state.request_id, "req_test_123")
        self.assertEqual(state.state, "pending")
        self.assertIsNotNone(state.started_at)
        self.assertEqual(state.desktop_launched, False)
        self.assertEqual(state.response_received, False)
        self.assertEqual(state.execution_started, False)
        self.assertEqual(state.errors, [])
        self.assertEqual(state.can_cancel, True)

    def test_state_transitions(self):
        """状態遷移が正しく機能することを確認"""
        from automation_helper import AutomationState

        state = AutomationState("req_test_123")

        # pending → launching
        state.state = "launching"
        self.assertEqual(state.state, "launching")

        # launching → waiting_response
        state.state = "waiting_response"
        state.desktop_launched = True
        self.assertEqual(state.state, "waiting_response")
        self.assertTrue(state.desktop_launched)

        # waiting_response → executing
        state.state = "executing"
        state.response_received = True
        state.execution_started = True
        self.assertEqual(state.state, "executing")

        # executing → completed
        state.state = "completed"
        state.can_cancel = False
        self.assertEqual(state.state, "completed")
        self.assertFalse(state.can_cancel)

    def test_error_recording(self):
        """エラー記録が正しく機能することを確認"""
        from automation_helper import AutomationState

        state = AutomationState("req_test_123")

        # エラーを追加
        state.add_error("起動エラー")
        state.add_error("タイムアウトエラー")

        self.assertEqual(len(state.errors), 2)
        self.assertEqual(state.errors[0], "起動エラー")
        self.assertEqual(state.errors[1], "タイムアウトエラー")

    def test_to_dict(self):
        """辞書形式への変換が正しく機能することを確認"""
        from automation_helper import AutomationState

        state = AutomationState("req_test_123")
        state.state = "executing"
        state.desktop_launched = True
        state.add_error("テストエラー")

        state_dict = state.to_dict()

        self.assertEqual(state_dict["request_id"], "req_test_123")
        self.assertEqual(state_dict["state"], "executing")
        self.assertTrue(state_dict["desktop_launched"])
        self.assertIn("テストエラー", state_dict["errors"])


class TestExecutionResult(unittest.TestCase):
    """実行結果データ構造のテスト"""

    def test_successful_result(self):
        """成功結果が正しく記録されることを確認"""
        from automation_helper import ExecutionResult

        result = ExecutionResult("req_test_123", success=True)

        self.assertEqual(result.request_id, "req_test_123")
        self.assertTrue(result.success)
        self.assertEqual(result.steps_completed, 0)
        self.assertEqual(result.steps_total, 0)
        self.assertEqual(result.files_modified, [])
        self.assertEqual(result.backups_created, [])
        self.assertEqual(result.errors, [])
        self.assertFalse(result.rollback_available)

    def test_failed_result_with_errors(self):
        """失敗結果とエラー情報が正しく記録されることを確認"""
        from automation_helper import ExecutionResult

        result = ExecutionResult("req_test_123", success=False)
        result.add_error({"type": "FileError", "message": "ファイルが見つかりません"})

        self.assertFalse(result.success)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0]["type"], "FileError")

    def test_progress_tracking(self):
        """進捗追跡が正しく機能することを確認"""
        from automation_helper import ExecutionResult

        result = ExecutionResult("req_test_123")
        result.steps_total = 5

        # ステップを進める
        result.steps_completed = 1
        self.assertEqual(result.steps_completed, 1)

        result.steps_completed = 3
        self.assertEqual(result.steps_completed, 3)

        result.steps_completed = 5
        self.assertEqual(result.steps_completed, 5)

    def test_file_tracking(self):
        """ファイル変更の追跡が正しく機能することを確認"""
        from automation_helper import ExecutionResult

        result = ExecutionResult("req_test_123", success=True)

        # ファイル変更を記録
        result.add_modified_file("/path/to/file1.py")
        result.add_modified_file("/path/to/file2.py")

        # バックアップを記録
        result.add_backup("/backup/file1.py.bak")

        self.assertEqual(len(result.files_modified), 2)
        self.assertEqual(len(result.backups_created), 1)
        self.assertIn("/path/to/file1.py", result.files_modified)

    def test_rollback_availability(self):
        """ロールバック可能性の管理が正しく機能することを確認"""
        from automation_helper import ExecutionResult

        result = ExecutionResult("req_test_123")

        # バックアップがあればロールバック可能
        result.add_backup("/backup/file.bak")
        result.rollback_available = True
        self.assertTrue(result.rollback_available)

        # ロールバック実行後は不可
        result.rollback_available = False
        self.assertFalse(result.rollback_available)

    def test_to_dict(self):
        """辞書形式への変換が正しく機能することを確認"""
        from automation_helper import ExecutionResult

        result = ExecutionResult("req_test_123", success=True)
        result.steps_completed = 3
        result.steps_total = 5
        result.add_modified_file("/path/to/file.py")
        result.add_error({"type": "WarningError", "message": "警告メッセージ"})

        result_dict = result.to_dict()

        self.assertEqual(result_dict["request_id"], "req_test_123")
        self.assertTrue(result_dict["success"])
        self.assertEqual(result_dict["steps_completed"], 3)
        self.assertEqual(result_dict["steps_total"], 5)
        self.assertIn("/path/to/file.py", result_dict["files_modified"])
        self.assertEqual(len(result_dict["errors"]), 1)


if __name__ == "__main__":
    unittest.main()
