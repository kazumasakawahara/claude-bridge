"""
自動化機能のヘルパーモジュール

Claude Code ⇄ Claude Desktop Bridgeの自動化機能を提供します。
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class AutomationConfig:
    """
    自動化設定を管理するクラス

    設定ファイルの読み込み、デフォルト値の提供、設定の保存を行います。
    """

    # デフォルト設定値
    DEFAULT_CONFIG = {
        "enabled": True,
        "auto_launch_desktop": True,
        "desktop_app_name": "Claude",
        "launch_timeout": 10,
        "response_timeout": 1800,
        "polling_interval": 1,
        "auto_execute_proposals": False,
        "create_backups": True,
        "max_retries": 3
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        自動化設定を初期化

        Args:
            config_path: 設定ファイルのパス(Noneの場合はデフォルト値を使用)
        """
        # デフォルト値で初期化
        self.enabled = self.DEFAULT_CONFIG["enabled"]
        self.auto_launch_desktop = self.DEFAULT_CONFIG["auto_launch_desktop"]
        self.desktop_app_name = self.DEFAULT_CONFIG["desktop_app_name"]
        self.launch_timeout = self.DEFAULT_CONFIG["launch_timeout"]
        self.response_timeout = self.DEFAULT_CONFIG["response_timeout"]
        self.polling_interval = self.DEFAULT_CONFIG["polling_interval"]
        self.auto_execute_proposals = self.DEFAULT_CONFIG["auto_execute_proposals"]
        self.create_backups = self.DEFAULT_CONFIG["create_backups"]
        self.max_retries = self.DEFAULT_CONFIG["max_retries"]

        # 設定ファイルが指定されている場合は読み込み
        if config_path:
            self._load_from_file(config_path)

    def _load_from_file(self, config_path: str):
        """
        設定ファイルから設定を読み込む

        Args:
            config_path: 設定ファイルのパス
        """
        path = Path(config_path)

        # ファイルが存在しない場合はデフォルト設定で作成
        if not path.exists():
            self.save(config_path)
            return

        try:
            # JSONファイルを読み込み
            config_data = json.loads(path.read_text(encoding="utf-8"))

            # 各設定値を検証して設定
            self._apply_config(config_data)

        except Exception as e:
            print(f"⚠️ 設定ファイルの読み込みに失敗しました: {e}")
            print(f"デフォルト設定を使用します")

    def _apply_config(self, config_data: Dict[str, Any]):
        """
        設定データを適用(型チェック付き)

        Args:
            config_data: 設定データの辞書
        """
        # enabledの検証と設定
        if "enabled" in config_data:
            if isinstance(config_data["enabled"], bool):
                self.enabled = config_data["enabled"]

        # auto_launch_desktopの検証と設定
        if "auto_launch_desktop" in config_data:
            if isinstance(config_data["auto_launch_desktop"], bool):
                self.auto_launch_desktop = config_data["auto_launch_desktop"]

        # desktop_app_nameの検証と設定
        if "desktop_app_name" in config_data:
            if isinstance(config_data["desktop_app_name"], str):
                self.desktop_app_name = config_data["desktop_app_name"]

        # launch_timeoutの検証と設定
        if "launch_timeout" in config_data:
            if isinstance(config_data["launch_timeout"], int) and config_data["launch_timeout"] > 0:
                self.launch_timeout = config_data["launch_timeout"]

        # response_timeoutの検証と設定
        if "response_timeout" in config_data:
            if isinstance(config_data["response_timeout"], int) and config_data["response_timeout"] > 0:
                self.response_timeout = config_data["response_timeout"]

        # polling_intervalの検証と設定
        if "polling_interval" in config_data:
            if isinstance(config_data["polling_interval"], (int, float)) and config_data["polling_interval"] > 0:
                self.polling_interval = config_data["polling_interval"]

        # auto_execute_proposalsの検証と設定
        if "auto_execute_proposals" in config_data:
            if isinstance(config_data["auto_execute_proposals"], bool):
                self.auto_execute_proposals = config_data["auto_execute_proposals"]

        # create_backupsの検証と設定
        if "create_backups" in config_data:
            if isinstance(config_data["create_backups"], bool):
                self.create_backups = config_data["create_backups"]

        # max_retriesの検証と設定
        if "max_retries" in config_data:
            if isinstance(config_data["max_retries"], int) and config_data["max_retries"] > 0:
                self.max_retries = config_data["max_retries"]

    def save(self, config_path: str):
        """
        現在の設定をファイルに保存

        Args:
            config_path: 保存先のファイルパス
        """
        config_data = {
            "enabled": self.enabled,
            "auto_launch_desktop": self.auto_launch_desktop,
            "desktop_app_name": self.desktop_app_name,
            "launch_timeout": self.launch_timeout,
            "response_timeout": self.response_timeout,
            "polling_interval": self.polling_interval,
            "auto_execute_proposals": self.auto_execute_proposals,
            "create_backups": self.create_backups,
            "max_retries": self.max_retries
        }

        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config_data, indent=2, ensure_ascii=False), encoding="utf-8")

    def to_dict(self) -> Dict[str, Any]:
        """
        設定を辞書形式で取得

        Returns:
            設定の辞書
        """
        return {
            "enabled": self.enabled,
            "auto_launch_desktop": self.auto_launch_desktop,
            "desktop_app_name": self.desktop_app_name,
            "launch_timeout": self.launch_timeout,
            "response_timeout": self.response_timeout,
            "polling_interval": self.polling_interval,
            "auto_execute_proposals": self.auto_execute_proposals,
            "create_backups": self.create_backups,
            "max_retries": self.max_retries
        }


class AutomationState:
    """
    自動化実行状態を追跡するクラス

    リクエストの処理状態、各ステップの完了状況、エラー情報を管理します。
    """

    def __init__(self, request_id: str):
        """
        自動化状態を初期化

        Args:
            request_id: リクエストID
        """
        self.request_id = request_id
        self.state = "pending"  # pending|launching|waiting_response|executing|completed|failed
        self.started_at = datetime.now().isoformat()
        self.desktop_launched = False
        self.response_received = False
        self.execution_started = False
        self.errors: List[str] = []
        self.can_cancel = True

    def add_error(self, error: str):
        """
        エラーを記録

        Args:
            error: エラーメッセージ
        """
        self.errors.append(error)

    def to_dict(self) -> Dict[str, Any]:
        """
        状態を辞書形式で取得

        Returns:
            状態の辞書
        """
        return {
            "request_id": self.request_id,
            "state": self.state,
            "started_at": self.started_at,
            "desktop_launched": self.desktop_launched,
            "response_received": self.response_received,
            "execution_started": self.execution_started,
            "errors": self.errors,
            "can_cancel": self.can_cancel
        }


class ExecutionResult:
    """
    実行結果を記録するクラス

    実行の成功/失敗、完了したステップ数、変更したファイル、
    エラー情報、ロールバック可能性を管理します。
    """

    def __init__(self, request_id: str, success: bool = False):
        """
        実行結果を初期化

        Args:
            request_id: リクエストID
            success: 実行成功フラグ
        """
        self.request_id = request_id
        self.success = success
        self.steps_completed = 0
        self.steps_total = 0
        self.files_modified: List[str] = []
        self.backups_created: List[str] = []
        self.errors: List[Dict[str, Any]] = []
        self.rollback_available = False

    def add_error(self, error: Dict[str, Any]):
        """
        エラーを記録

        Args:
            error: エラー情報の辞書
        """
        self.errors.append(error)

    def add_modified_file(self, file_path: str):
        """
        変更されたファイルを記録

        Args:
            file_path: 変更されたファイルのパス
        """
        self.files_modified.append(file_path)

    def add_backup(self, backup_path: str):
        """
        作成されたバックアップを記録

        Args:
            backup_path: バックアップファイルのパス
        """
        self.backups_created.append(backup_path)

    def to_dict(self) -> Dict[str, Any]:
        """
        実行結果を辞書形式で取得

        Returns:
            実行結果の辞書
        """
        return {
            "request_id": self.request_id,
            "success": self.success,
            "steps_completed": self.steps_completed,
            "steps_total": self.steps_total,
            "files_modified": self.files_modified,
            "backups_created": self.backups_created,
            "errors": self.errors,
            "rollback_available": self.rollback_available
        }


class DesktopLauncher:
    """
    Claude Desktopアプリケーションの起動を管理するクラス

    macOSでのアプリケーション起動、プロセス確認、起動完了待機を提供します。
    """

    def __init__(self, config: AutomationConfig):
        """
        DesktopLauncherを初期化

        Args:
            config: 自動化設定
        """
        self.config = config
        self.app_name = config.desktop_app_name

    def launch(self) -> bool:
        """
        Claude Desktopアプリケーションを起動

        Returns:
            起動成功時True、失敗時False
        """
        try:
            # macOSのopenコマンドでアプリケーションを起動
            result = subprocess.run(
                ["/usr/bin/open", "-a", self.app_name],
                capture_output=True,
                timeout=self.config.launch_timeout
            )

            # 起動成功を確認
            return result.returncode == 0

        except Exception as e:
            print(f"⚠️ アプリケーション起動エラー: {e}")
            return False

    def is_running(self) -> bool:
        """
        アプリケーションが実行中かを確認

        Returns:
            実行中の場合True、そうでない場合False
        """
        try:
            # pgrepコマンドでプロセスを検索
            result = subprocess.run(
                ["pgrep", "-x", self.app_name],
                capture_output=True,
                timeout=5
            )

            # プロセスが見つかった場合はreturncode=0
            return result.returncode == 0

        except Exception:
            return False

    def wait_until_ready(self) -> bool:
        """
        アプリケーションが起動完了するまで待機

        Returns:
            起動完了時True、タイムアウト時False
        """
        start_time = time.time()
        timeout = self.config.launch_timeout

        while time.time() - start_time < timeout:
            if self.is_running():
                return True

            # 0.5秒待機してから再確認
            time.sleep(0.5)

        # タイムアウト
        return False

    def launch_with_retry(self) -> bool:
        """
        リトライ機能付きでアプリケーションを起動

        最大max_retries回まで起動を試行します。
        各リトライの間には1秒の待機時間を設けます。

        Returns:
            起動成功時True、すべての試行が失敗した場合False
        """
        for attempt in range(1, self.config.max_retries + 1):
            print(f"🔄 起動試行 {attempt}/{self.config.max_retries}...")

            # アプリケーション起動を試行
            if self.launch():
                # 起動コマンドが成功したら、実際に起動完了するまで待機
                if self.wait_until_ready():
                    print(f"✅ 起動成功 (試行 {attempt}回目)")
                    return True
                else:
                    print(f"⚠️ 起動タイムアウト (試行 {attempt}回目)")
            else:
                print(f"⚠️ 起動失敗 (試行 {attempt}回目)")

            # 最後の試行以外では待機
            if attempt < self.config.max_retries:
                print("⏳ 1秒待機してから再試行...")
                time.sleep(1)

        print(f"❌ すべての起動試行が失敗しました ({self.config.max_retries}回)")
        return False

    def show_manual_fallback_message(self):
        """
        手動起動のフォールバックメッセージを表示

        自動起動が失敗した際に、ユーザーに手動起動を促すメッセージを表示します。
        """
        print("\n" + "=" * 60)
        print("⚠️  自動起動に失敗しました")
        print("=" * 60)
        print(f"\n📝 次の手順で手動起動してください:")
        print(f"\n1. Finderまたはアプリケーションフォルダから")
        print(f"   「{self.app_name}」を手動で起動してください")
        print(f"\n2. アプリケーションが起動したら、")
        print(f"   このプログラムを再実行してください")
        print("\n" + "=" * 60 + "\n")


class ResponseMonitor:
    """
    Claude Desktopからのレスポンスファイルを監視するクラス

    ファイルシステムポーリングによる監視を提供します。
    """

    def __init__(self, config: AutomationConfig, response_file_path: str):
        """
        ResponseMonitorを初期化

        Args:
            config: 自動化設定
            response_file_path: 監視するレスポンスファイルのパス
        """
        self.config = config
        self.response_file_path = Path(response_file_path)
        self.cancelled = False  # キャンセルフラグ

    def check_for_response(self) -> bool:
        """
        レスポンスファイルの存在を確認

        Returns:
            ファイルが存在する場合True、そうでない場合False
        """
        return self.response_file_path.exists()

    def wait_for_response(self) -> bool:
        """
        レスポンスファイルが作成されるまで待機

        polling_interval秒ごとにファイルの存在を確認します。
        response_timeoutを超えた場合はタイムアウトします。

        Returns:
            レスポンス検出時True、タイムアウト時False
        """
        start_time = time.time()
        timeout = self.config.response_timeout
        interval = self.config.polling_interval

        print(f"🔍 レスポンスファイルを監視中...")
        print(f"   ファイル: {self.response_file_path}")
        print(f"   タイムアウト: {timeout}秒")

        while time.time() - start_time < timeout:
            # キャンセルチェック
            if self.cancelled:
                print(f"⚠️ 監視がキャンセルされました")
                return False

            # レスポンスファイルの存在確認
            if self.check_for_response():
                print(f"✅ レスポンスファイルを検出しました")
                return True

            # polling_interval秒待機してCPU使用率を抑制
            time.sleep(interval)

        # タイムアウト
        elapsed = time.time() - start_time
        print(f"⚠️ タイムアウト: {elapsed:.1f}秒経過")
        return False

    def read_response(self) -> Optional[Dict[str, Any]]:
        """
        レスポンスファイルを読み込んで解析

        Returns:
            レスポンスデータの辞書、失敗時はNone
        """
        try:
            # ファイルの存在確認
            if not self.response_file_path.exists():
                print(f"⚠️ レスポンスファイルが見つかりません: {self.response_file_path}")
                return None

            # JSONファイルを読み込み
            response_data = json.loads(
                self.response_file_path.read_text(encoding="utf-8")
            )

            print(f"✅ レスポンスファイルを読み込みました")
            return response_data

        except json.JSONDecodeError as e:
            print(f"⚠️ JSONパースエラー: {e}")
            return None

        except Exception as e:
            print(f"⚠️ レスポンス読み込みエラー: {e}")
            return None

    def cancel(self):
        """
        監視をキャンセル

        wait_for_response()を中断します。
        """
        self.cancelled = True
        print("🛑 監視のキャンセルを要求しました")
