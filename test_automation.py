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
from automation_helper import (
    AutomationConfig,
    AutomationState,
    ExecutionResult,
    DesktopLauncher,
    ResponseMonitor,
    AutomatedBridge,
    ProposalExecutor,  # Task 5用
    ErrorHandler,  # Task 6用
    CheckpointManager  # Task 6用
)


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


class TestDesktopLauncher(unittest.TestCase):
    """Claude Desktop起動機能のテスト"""

    def test_launch_success(self):
        """アプリケーションが正常に起動することを確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        launcher = DesktopLauncher(config)

        # subprocess.runをモック化
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            success = launcher.launch()

            # 起動成功を確認
            self.assertTrue(success)
            # 正しいコマンドが実行されたことを確認
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            self.assertEqual(call_args[0], "/usr/bin/open")
            self.assertEqual(call_args[1], "-a")
            self.assertEqual(call_args[2], "Claude")

    def test_launch_failure(self):
        """アプリケーション起動が失敗することを確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        launcher = DesktopLauncher(config)

        # subprocess.runが失敗するようモック化
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=1)

            success = launcher.launch()

            # 起動失敗を確認
            self.assertFalse(success)

    def test_launch_exception(self):
        """起動時の例外処理を確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        launcher = DesktopLauncher(config)

        # subprocess.runが例外を投げるようモック化
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Command not found")

            success = launcher.launch()

            # 例外を適切に処理して失敗を返すことを確認
            self.assertFalse(success)

    def test_is_running_success(self):
        """アプリケーションが実行中であることを確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        launcher = DesktopLauncher(config)

        # pgrep コマンドが成功(プロセスが見つかった)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            is_running = launcher.is_running()

            # 実行中を確認
            self.assertTrue(is_running)
            # pgrepコマンドが実行されたことを確認
            call_args = mock_run.call_args[0][0]
            self.assertEqual(call_args[0], "pgrep")
            self.assertEqual(call_args[1], "-x")
            self.assertEqual(call_args[2], "Claude")

    def test_is_running_not_found(self):
        """アプリケーションが実行されていないことを確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        launcher = DesktopLauncher(config)

        # pgrep コマンドが失敗(プロセスが見つからない)
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=1)

            is_running = launcher.is_running()

            # 実行されていないことを確認
            self.assertFalse(is_running)

    def test_wait_until_ready_success(self):
        """起動完了まで待機する機能を確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        config.launch_timeout = 2  # 短いタイムアウトでテスト
        launcher = DesktopLauncher(config)

        # is_runningが最初はFalse、次にTrueを返すようモック化
        with patch.object(launcher, "is_running") as mock_is_running:
            mock_is_running.side_effect = [False, False, True]

            # time.sleepをモック化して高速化
            with patch("time.sleep"):
                success = launcher.wait_until_ready()

                # 起動完了を確認
                self.assertTrue(success)
                # is_runningが複数回呼ばれたことを確認
                self.assertEqual(mock_is_running.call_count, 3)

    def test_wait_until_ready_timeout(self):
        """起動タイムアウトを確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        config.launch_timeout = 1  # 短いタイムアウト
        launcher = DesktopLauncher(config)

        # is_runningが常にFalseを返すようモック化
        with patch.object(launcher, "is_running") as mock_is_running:
            mock_is_running.return_value = False

            # time.sleepをモック化
            with patch("time.sleep"):
                success = launcher.wait_until_ready()

                # タイムアウトで失敗することを確認
                self.assertFalse(success)

    def test_launch_with_retry_success_first_attempt(self):
        """初回の試行で起動成功することを確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        launcher = DesktopLauncher(config)

        # launchとwait_until_readyが成功するようモック化
        with patch.object(launcher, "launch") as mock_launch:
            with patch.object(launcher, "wait_until_ready") as mock_wait:
                mock_launch.return_value = True
                mock_wait.return_value = True

                success = launcher.launch_with_retry()

                # 起動成功を確認
                self.assertTrue(success)
                # 1回だけ試行されたことを確認
                self.assertEqual(mock_launch.call_count, 1)
                self.assertEqual(mock_wait.call_count, 1)

    def test_launch_with_retry_success_second_attempt(self):
        """2回目の試行で起動成功することを確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        launcher = DesktopLauncher(config)

        # 1回目は失敗、2回目は成功
        with patch.object(launcher, "launch") as mock_launch:
            with patch.object(launcher, "wait_until_ready") as mock_wait:
                mock_launch.side_effect = [False, True]
                mock_wait.return_value = True

                # time.sleepをモック化
                with patch("time.sleep"):
                    success = launcher.launch_with_retry()

                    # 起動成功を確認
                    self.assertTrue(success)
                    # 2回試行されたことを確認
                    self.assertEqual(mock_launch.call_count, 2)

    def test_launch_with_retry_all_attempts_fail(self):
        """すべての試行が失敗することを確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        config.max_retries = 3
        launcher = DesktopLauncher(config)

        # すべての試行で失敗
        with patch.object(launcher, "launch") as mock_launch:
            mock_launch.return_value = False

            # time.sleepをモック化
            with patch("time.sleep"):
                success = launcher.launch_with_retry()

                # 起動失敗を確認
                self.assertFalse(success)
                # max_retries回試行されたことを確認
                self.assertEqual(mock_launch.call_count, 3)

    def test_launch_with_retry_respects_retry_interval(self):
        """リトライ間隔が正しく適用されることを確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        config.max_retries = 2
        launcher = DesktopLauncher(config)

        # すべて失敗させる
        with patch.object(launcher, "launch") as mock_launch:
            mock_launch.return_value = False

            # time.sleepをモック化して呼び出しを記録
            with patch("time.sleep") as mock_sleep:
                launcher.launch_with_retry()

                # 1回目の失敗後に1秒待機したことを確認
                mock_sleep.assert_called_with(1)

    def test_manual_fallback_message(self):
        """手動フォールバックメッセージが表示されることを確認"""
        from automation_helper import DesktopLauncher, AutomationConfig

        config = AutomationConfig()
        launcher = DesktopLauncher(config)

        # 標準出力をキャプチャ
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            launcher.show_manual_fallback_message()

            output = captured_output.getvalue()

            # メッセージに必要な要素が含まれていることを確認
            self.assertIn("手動", output)
            self.assertIn("起動", output)
            self.assertIn(config.desktop_app_name, output)

        finally:
            sys.stdout = sys.__stdout__


class TestResponseMonitor(unittest.TestCase):
    """レスポンス監視機能のテスト"""

    def setUp(self):
        """各テストの前に一時ディレクトリを作成"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.response_file = self.test_dir / "response.json"

    def tearDown(self):
        """各テストの後に一時ディレクトリを削除"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_check_for_response_file_not_exists(self):
        """レスポンスファイルが存在しない場合を確認"""
        from automation_helper import ResponseMonitor, AutomationConfig

        config = AutomationConfig()
        monitor = ResponseMonitor(config, str(self.response_file))

        # ファイルが存在しないことを確認
        exists = monitor.check_for_response()

        self.assertFalse(exists)

    def test_check_for_response_file_exists(self):
        """レスポンスファイルが存在する場合を確認"""
        from automation_helper import ResponseMonitor, AutomationConfig

        config = AutomationConfig()
        monitor = ResponseMonitor(config, str(self.response_file))

        # ファイルを作成
        self.response_file.write_text("{}", encoding="utf-8")

        # ファイルが存在することを確認
        exists = monitor.check_for_response()

        self.assertTrue(exists)

    def test_wait_for_response_success(self):
        """レスポンスファイルが作成されるまで待機することを確認"""
        from automation_helper import ResponseMonitor, AutomationConfig

        config = AutomationConfig()
        config.response_timeout = 2  # 短いタイムアウト
        monitor = ResponseMonitor(config, str(self.response_file))

        # check_for_responseが最初はFalse、次にTrueを返すようモック化
        with patch.object(monitor, "check_for_response") as mock_check:
            mock_check.side_effect = [False, False, True]

            # time.sleepをモック化して高速化
            with patch("time.sleep"):
                success = monitor.wait_for_response()

                # レスポンス検出成功を確認
                self.assertTrue(success)
                # check_for_responseが複数回呼ばれたことを確認
                self.assertEqual(mock_check.call_count, 3)

    def test_wait_for_response_timeout(self):
        """タイムアウトを確認"""
        from automation_helper import ResponseMonitor, AutomationConfig

        config = AutomationConfig()
        config.response_timeout = 1  # 短いタイムアウト
        monitor = ResponseMonitor(config, str(self.response_file))

        # check_for_responseが常にFalseを返すようモック化
        with patch.object(monitor, "check_for_response") as mock_check:
            mock_check.return_value = False

            # time.sleepをモック化
            with patch("time.sleep"):
                success = monitor.wait_for_response()

                # タイムアウトで失敗することを確認
                self.assertFalse(success)

    def test_polling_interval(self):
        """ポーリング間隔が正しく適用されることを確認"""
        from automation_helper import ResponseMonitor, AutomationConfig

        config = AutomationConfig()
        config.polling_interval = 1
        config.response_timeout = 3
        monitor = ResponseMonitor(config, str(self.response_file))

        # check_for_responseが常にFalseを返すようモック化
        with patch.object(monitor, "check_for_response") as mock_check:
            mock_check.return_value = False

            # time.sleepをモック化して呼び出しを記録
            with patch("time.sleep") as mock_sleep:
                monitor.wait_for_response()

                # polling_interval秒で待機したことを確認
                mock_sleep.assert_called_with(config.polling_interval)

    def test_read_response_success(self):
        """レスポンスファイルを正常に読み込めることを確認"""
        from automation_helper import ResponseMonitor, AutomationConfig

        config = AutomationConfig()
        monitor = ResponseMonitor(config, str(self.response_file))

        # テスト用のレスポンスファイルを作成
        test_response = {
            "status": "success",
            "implementation_steps": ["Step 1", "Step 2"],
            "code_files": [{"path": "test.py", "content": "print('hello')"}]
        }
        self.response_file.write_text(json.dumps(test_response), encoding="utf-8")

        # レスポンスを読み込み
        response = monitor.read_response()

        # 正しく読み込まれたことを確認
        self.assertIsNotNone(response)
        self.assertEqual(response["status"], "success")
        self.assertEqual(len(response["implementation_steps"]), 2)

    def test_read_response_file_not_found(self):
        """レスポンスファイルが存在しない場合を確認"""
        from automation_helper import ResponseMonitor, AutomationConfig

        config = AutomationConfig()
        monitor = ResponseMonitor(config, str(self.response_file))

        # ファイルが存在しない状態で読み込み
        response = monitor.read_response()

        # Noneが返されることを確認
        self.assertIsNone(response)

    def test_read_response_invalid_json(self):
        """無効なJSONファイルの場合を確認"""
        from automation_helper import ResponseMonitor, AutomationConfig

        config = AutomationConfig()
        monitor = ResponseMonitor(config, str(self.response_file))

        # 無効なJSONファイルを作成
        self.response_file.write_text("{ invalid json", encoding="utf-8")

        # レスポンスを読み込み
        response = monitor.read_response()

        # Noneが返されることを確認
        self.assertIsNone(response)

    def test_cancel_monitoring(self):
        """監視のキャンセルが機能することを確認"""
        from automation_helper import ResponseMonitor, AutomationConfig

        config = AutomationConfig()
        config.response_timeout = 10
        monitor = ResponseMonitor(config, str(self.response_file))

        # check_for_responseが常にFalseを返すようモック化
        with patch.object(monitor, "check_for_response") as mock_check:
            mock_check.return_value = False

            # キャンセルフラグを設定
            monitor.cancelled = True

            # time.sleepをモック化
            with patch("time.sleep"):
                success = monitor.wait_for_response()

                # キャンセルで失敗することを確認
                self.assertFalse(success)


class TestAutomatedBridge(unittest.TestCase):
    """自動化ブリッジの統合テスト"""

    def setUp(self):
        """各テストの前に一時ディレクトリを作成"""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """各テストの後に一時ディレクトリを削除"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_automated_bridge_initialization(self):
        """AutomatedBridgeが正しく初期化されることを確認"""
        from automation_helper import AutomatedBridge, AutomationConfig

        config = AutomationConfig()
        bridge = AutomatedBridge(config)

        # 設定が正しく設定されていることを確認
        self.assertIsNotNone(bridge.config)
        self.assertIsNotNone(bridge.launcher)
        # monitorは初期化時はNone（create_automated_request後に設定される）
        self.assertIsNone(bridge.monitor)
        self.assertIsNone(bridge.current_request_id)

    def test_automated_bridge_inherits_from_claude_bridge(self):
        """AutomatedBridgeがClaudeBridgeを継承していることを確認"""
        from automation_helper import AutomatedBridge, AutomationConfig
        from bridge_helper import ClaudeBridge

        config = AutomationConfig()
        bridge = AutomatedBridge(config)

        # ClaudeBridgeのインスタンスであることを確認
        self.assertIsInstance(bridge, ClaudeBridge)

    def test_create_automated_request(self):
        """自動化リクエストが作成されることを確認"""
        from automation_helper import AutomatedBridge, AutomationConfig

        config = AutomationConfig()
        bridge = AutomatedBridge(config)

        # リクエスト作成
        request_id = bridge.create_automated_request(
            title="Test Request",
            problem="Test problem",
            tried=["Method 1"],
            files_to_analyze=[]
        )

        # リクエストIDが返されることを確認
        self.assertIsNotNone(request_id)
        self.assertTrue(request_id.startswith("req_"))

    def test_run_automated_workflow_success(self):
        """完全自動化ワークフローが正常に実行されることを確認"""
        from automation_helper import AutomatedBridge, AutomationConfig

        config = AutomationConfig()
        bridge = AutomatedBridge(config)

        # 各ステップをモック化
        with patch.object(bridge.launcher, "launch_with_retry") as mock_launch:
            with patch.object(bridge, "create_automated_request") as mock_request:
                mock_launch.return_value = True
                mock_request.return_value = "req_test_123"

                # ワークフロー実行
                result = bridge.run_automated_workflow(
                    title="Test",
                    problem="Test problem",
                    tried=["Method 1"],
                    files_to_analyze=[]
                )

                # 成功することを確認
                self.assertIsNotNone(result)
                self.assertEqual(result["request_id"], "req_test_123")

    def test_show_manual_file_transfer_instructions(self):
        """手動ファイル転送の指示が表示されることを確認"""
        from automation_helper import AutomatedBridge, AutomationConfig

        config = AutomationConfig()
        bridge = AutomatedBridge(config)

        # 標準出力をキャプチャ
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            bridge.show_manual_file_transfer_instructions("req_test_123")

            output = captured_output.getvalue()

            # メッセージに必要な要素が含まれていることを確認
            self.assertIn("req_test_123", output)
            self.assertIn("手動", output)
            self.assertIn("ファイル", output)

        finally:
            sys.stdout = sys.__stdout__


class TestProposalExecutor(unittest.TestCase):
    """提案実行機能のテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.config = AutomationConfig()
        self.executor = ProposalExecutor(self.config)
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """テスト後のクリーンアップ"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_executor_initialization(self):
        """ProposalExecutorが正しく初期化されることを確認"""
        self.assertIsNotNone(self.executor.config)
        self.assertIsNotNone(self.executor.backup_dir)
        self.assertTrue(self.executor.backup_dir.exists())

    def test_extract_implementation_steps(self):
        """レスポンスからimplementation_stepsを抽出できることを確認"""
        response = {
            "analysis": {
                "implementation_steps": [
                    {"step": 1, "description": "Step 1", "action": "Do something"},
                    {"step": 2, "description": "Step 2", "action": "Do more"}
                ]
            }
        }

        steps = self.executor.extract_implementation_steps(response)

        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0]["step"], 1)
        self.assertEqual(steps[1]["description"], "Step 2")

    def test_extract_implementation_steps_no_steps(self):
        """implementation_stepsがない場合を確認"""
        response = {"analysis": {}}

        steps = self.executor.extract_implementation_steps(response)

        self.assertEqual(len(steps), 0)

    def test_execute_step(self):
        """個別ステップの実行を確認"""
        step = {
            "step": 1,
            "description": "テストステップ",
            "action": "テストアクションを実行"
        }

        result = self.executor.execute_step(step, 1, 3)

        self.assertTrue(result)

    def test_execute_all_steps(self):
        """全ステップの順次実行を確認"""
        steps = [
            {"step": 1, "description": "Step 1", "action": "Action 1"},
            {"step": 2, "description": "Step 2", "action": "Action 2"},
            {"step": 3, "description": "Step 3", "action": "Action 3"}
        ]

        results = self.executor.execute_all_steps(steps)

        self.assertEqual(len(results), 3)
        self.assertTrue(all(results))

    def test_create_backup(self):
        """ファイルのバックアップが作成されることを確認"""
        # テスト用ファイル作成
        test_file = self.temp_dir / "test_code.py"
        test_file.write_text("# Original content", encoding="utf-8")

        # バックアップ作成
        backup_path = self.executor.create_backup(str(test_file))

        # バックアップが存在することを確認
        self.assertIsNotNone(backup_path)
        self.assertTrue(Path(backup_path).exists())

        # バックアップ内容が元のファイルと一致することを確認
        backup_content = Path(backup_path).read_text(encoding="utf-8")
        self.assertEqual(backup_content, "# Original content")

    def test_apply_code_file(self):
        """コードファイルの適用を確認"""
        # テスト用ファイル作成
        test_file = self.temp_dir / "test_code.py"
        test_file.write_text("# Original content", encoding="utf-8")

        # 新しい内容
        new_content = "# Updated content"

        # ファイル適用
        result = self.executor.apply_code_file(
            str(test_file),
            new_content
        )

        # 適用成功を確認
        self.assertTrue(result)

        # ファイル内容が更新されていることを確認
        updated_content = test_file.read_text(encoding="utf-8")
        self.assertEqual(updated_content, new_content)

    def test_extract_code_files(self):
        """レスポンスからcode_filesを抽出できることを確認"""
        response = {
            "analysis": {
                "code_files": [
                    {"path": "src/main.py", "content": "# Main file"},
                    {"path": "src/utils.py", "content": "# Utils file"}
                ]
            }
        }

        code_files = self.executor.extract_code_files(response)

        self.assertEqual(len(code_files), 2)
        self.assertEqual(code_files[0]["path"], "src/main.py")
        self.assertEqual(code_files[1]["content"], "# Utils file")

    def test_apply_all_code_files(self):
        """全コードファイルの適用を確認"""
        # テスト用ファイル作成
        file1 = self.temp_dir / "file1.py"
        file2 = self.temp_dir / "file2.py"
        file1.write_text("# Original 1", encoding="utf-8")
        file2.write_text("# Original 2", encoding="utf-8")

        code_files = [
            {"path": str(file1), "content": "# Updated 1"},
            {"path": str(file2), "content": "# Updated 2"}
        ]

        # 全ファイル適用
        results = self.executor.apply_all_code_files(code_files)

        # 全て成功することを確認
        self.assertEqual(len(results), 2)
        self.assertTrue(all(results))

        # ファイル内容が更新されていることを確認
        self.assertEqual(file1.read_text(encoding="utf-8"), "# Updated 1")
        self.assertEqual(file2.read_text(encoding="utf-8"), "# Updated 2")

    def test_show_proposal_summary(self):
        """提案のサマリー表示を確認"""
        response = {
            "analysis": {
                "recommendations": [
                    {"title": "Recommendation 1", "description": "Do this"},
                    {"title": "Recommendation 2", "description": "Do that"}
                ],
                "implementation_steps": [
                    {"step": 1, "description": "Step 1"},
                    {"step": 2, "description": "Step 2"}
                ],
                "code_files": [
                    {"path": "file1.py", "content": "content1"},
                    {"path": "file2.py", "content": "content2"}
                ]
            }
        }

        # サマリー表示（出力のみ確認）
        self.executor.show_proposal_summary(response)

    @patch('builtins.input', return_value='y')
    def test_request_user_approval_accepted(self, mock_input):
        """ユーザー承認が受け入れられることを確認"""
        result = self.executor.request_user_approval("Test proposal")
        self.assertTrue(result)

    @patch('builtins.input', return_value='n')
    def test_request_user_approval_rejected(self, mock_input):
        """ユーザー承認が拒否されることを確認"""
        result = self.executor.request_user_approval("Test proposal")
        self.assertFalse(result)

    @patch('builtins.input', return_value='Y')
    def test_request_user_approval_uppercase(self, mock_input):
        """ユーザー承認が大文字Yで受け入れられることを確認"""
        result = self.executor.request_user_approval("Test proposal")
        self.assertTrue(result)


class TestErrorHandler(unittest.TestCase):
    """エラーハンドリング機能のテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.config = AutomationConfig()
        self.handler = ErrorHandler(self.config)
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """テスト後のクリーンアップ"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_error_handler_initialization(self):
        """ErrorHandlerが正しく初期化されることを確認"""
        self.assertIsNotNone(self.handler.config)
        self.assertIsNotNone(self.handler.log_dir)
        self.assertTrue(self.handler.log_dir.exists())

    def test_classify_error_critical(self):
        """致命的エラーの分類を確認"""
        error = Exception("Critical system failure")
        severity = self.handler.classify_error(error, "system_crash")
        self.assertEqual(severity, "critical")

    def test_classify_error_recoverable(self):
        """回復可能エラーの分類を確認"""
        error = FileNotFoundError("File not found")
        severity = self.handler.classify_error(error, "file_operation")
        self.assertEqual(severity, "recoverable")

    def test_classify_error_warning(self):
        """警告レベルエラーの分類を確認"""
        error = ValueError("Invalid value")
        severity = self.handler.classify_error(error, "validation")
        self.assertEqual(severity, "warning")

    def test_log_error(self):
        """エラーログ記録を確認"""
        error = Exception("Test error")
        log_file = self.handler.log_error(
            error=error,
            context="test_context",
            severity="critical"
        )

        # ログファイルが作成されていることを確認
        self.assertIsNotNone(log_file)
        self.assertTrue(Path(log_file).exists())

        # ログ内容を確認
        log_content = Path(log_file).read_text(encoding="utf-8")
        self.assertIn("Test error", log_content)
        self.assertIn("critical", log_content)
        self.assertIn("test_context", log_content)

    def test_handle_error_critical(self):
        """致命的エラーのハンドリングを確認"""
        error = Exception("Critical error")
        result = self.handler.handle_error(
            error=error,
            context="critical_operation",
            raise_on_critical=False
        )

        self.assertFalse(result)  # 致命的エラーはFalseを返す

    def test_handle_error_recoverable(self):
        """回復可能エラーのハンドリングを確認"""
        error = FileNotFoundError("File not found")
        result = self.handler.handle_error(
            error=error,
            context="file_operation"
        )

        self.assertTrue(result)  # 回復可能エラーはTrueを返す


class TestCheckpointManager(unittest.TestCase):
    """チェックポイントとロールバック機能のテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.config = AutomationConfig()
        self.manager = CheckpointManager(self.config)
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """テスト後のクリーンアップ"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_checkpoint_manager_initialization(self):
        """CheckpointManagerが正しく初期化されることを確認"""
        self.assertIsNotNone(self.manager.config)
        self.assertIsNotNone(self.manager.checkpoint_dir)
        self.assertTrue(self.manager.checkpoint_dir.exists())

    def test_create_checkpoint(self):
        """チェックポイントの作成を確認"""
        # テスト用ファイル作成
        test_file1 = self.temp_dir / "file1.py"
        test_file2 = self.temp_dir / "file2.py"
        test_file1.write_text("# Content 1", encoding="utf-8")
        test_file2.write_text("# Content 2", encoding="utf-8")

        files = [str(test_file1), str(test_file2)]

        # チェックポイント作成
        checkpoint_id = self.manager.create_checkpoint(
            files=files,
            description="Test checkpoint"
        )

        # チェックポイントIDが返されることを確認
        self.assertIsNotNone(checkpoint_id)

        # チェックポイントディレクトリが存在することを確認
        checkpoint_path = self.manager.checkpoint_dir / checkpoint_id
        self.assertTrue(checkpoint_path.exists())

    def test_rollback_checkpoint(self):
        """チェックポイントのロールバックを確認"""
        # テスト用ファイル作成
        test_file = self.temp_dir / "test.py"
        test_file.write_text("# Original", encoding="utf-8")

        # チェックポイント作成
        checkpoint_id = self.manager.create_checkpoint(
            files=[str(test_file)],
            description="Before change"
        )

        # ファイル変更
        test_file.write_text("# Modified", encoding="utf-8")
        self.assertEqual(test_file.read_text(encoding="utf-8"), "# Modified")

        # ロールバック実行
        result = self.manager.rollback(checkpoint_id)
        self.assertTrue(result)

        # ファイルが元に戻っていることを確認
        self.assertEqual(test_file.read_text(encoding="utf-8"), "# Original")

    def test_delete_new_files_on_rollback(self):
        """ロールバック時に新規ファイルが削除されることを確認"""
        # 既存ファイル作成
        existing_file = self.temp_dir / "existing.py"
        existing_file.write_text("# Existing", encoding="utf-8")

        # チェックポイント作成
        checkpoint_id = self.manager.create_checkpoint(
            files=[str(existing_file)],
            description="Before new files"
        )

        # 新規ファイル作成
        new_file = self.temp_dir / "new.py"
        new_file.write_text("# New file", encoding="utf-8")
        self.assertTrue(new_file.exists())

        # ロールバック実行（新規ファイルのパスを渡す）
        result = self.manager.rollback(
            checkpoint_id,
            new_files=[str(new_file)]
        )
        self.assertTrue(result)

        # 新規ファイルが削除されていることを確認
        self.assertFalse(new_file.exists())

        # 既存ファイルは残っていることを確認
        self.assertTrue(existing_file.exists())

    def test_list_checkpoints(self):
        """チェックポイント一覧の取得を確認"""
        # チェックポイント作成
        test_file = self.temp_dir / "test.py"
        test_file.write_text("# Test", encoding="utf-8")

        cp1 = self.manager.create_checkpoint([str(test_file)], "Checkpoint 1")

        # 異なるタイムスタンプを確保するため少し待機
        import time
        time.sleep(1)

        cp2 = self.manager.create_checkpoint([str(test_file)], "Checkpoint 2")

        # 一覧取得
        checkpoints = self.manager.list_checkpoints()

        # 作成したチェックポイントが含まれることを確認
        self.assertGreaterEqual(len(checkpoints), 2)


class TestAutomationModeManager(unittest.TestCase):
    """自動化モード管理機能のテスト"""

    def test_toggle_automation_mode(self):
        """自動化モードの切り替えを確認"""
        config = AutomationConfig()

        # 初期状態（自動化有効）
        self.assertTrue(config.auto_launch_desktop)

        # 自動化を無効化
        config.auto_launch_desktop = False
        self.assertFalse(config.auto_launch_desktop)

        # 自動化を有効化
        config.auto_launch_desktop = True
        self.assertTrue(config.auto_launch_desktop)

    def test_automated_bridge_with_manual_mode(self):
        """AutomatedBridgeが手動モードで動作することを確認"""
        config = AutomationConfig()
        config.auto_launch_desktop = False  # 手動モード

        bridge = AutomatedBridge(config)

        # 設定が反映されていることを確認
        self.assertFalse(bridge.config.auto_launch_desktop)

    @patch.object(DesktopLauncher, 'launch_with_retry', return_value=False)
    def test_fallback_to_manual_mode_on_launch_failure(self, mock_launch):
        """起動失敗時に手動モードにフォールバックすることを確認"""
        config = AutomationConfig()
        config.auto_launch_desktop = True

        bridge = AutomatedBridge(config)

        # リクエスト作成
        request_id = bridge.create_automated_request(
            title="Test",
            problem="Test problem",
            tried=["Test tried"],
            files_to_analyze=[]
        )

        # ワークフロー実行（起動が失敗するのでmanual_modeになるはず）
        result = bridge.run_automated_workflow(
            title="Test",
            problem="Test problem",
            tried=["Test tried"],
            files_to_analyze=[]
        )

        # 手動モードにフォールバックしたことを確認
        self.assertIsNotNone(result)
        self.assertEqual(result.get("status"), "manual_mode")


if __name__ == "__main__":
    unittest.main()
