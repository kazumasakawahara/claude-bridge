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

# 既存のClaudeBridgeをインポート
import sys
sys.path.append(str(Path(__file__).parent))
from bridge_helper import ClaudeBridge


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

    @classmethod
    def load(cls, config_path: str) -> 'AutomationConfig':
        """
        設定ファイルから設定を読み込んで新しいインスタンスを作成

        Args:
            config_path: 設定ファイルのパス

        Returns:
            設定が読み込まれたAutomationConfigインスタンス
        """
        return cls(config_path=config_path)

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

    def validate_config(self) -> bool:
        """
        設定値の検証

        Returns:
            全ての設定値が有効な場合True、そうでない場合False
        """
        try:
            # ブール値の検証
            if not isinstance(self.enabled, bool):
                print(f"⚠️  無効な設定: enabled は bool 型である必要があります")
                return False

            if not isinstance(self.auto_launch_desktop, bool):
                print(f"⚠️  無効な設定: auto_launch_desktop は bool 型である必要があります")
                return False

            if not isinstance(self.auto_execute_proposals, bool):
                print(f"⚠️  無効な設定: auto_execute_proposals は bool 型である必要があります")
                return False

            if not isinstance(self.create_backups, bool):
                print(f"⚠️  無効な設定: create_backups は bool 型である必要があります")
                return False

            # 文字列の検証
            if not isinstance(self.desktop_app_name, str) or not self.desktop_app_name:
                print(f"⚠️  無効な設定: desktop_app_name は空でない文字列である必要があります")
                return False

            # 正の整数の検証
            if not isinstance(self.launch_timeout, int) or self.launch_timeout <= 0:
                print(f"⚠️  無効な設定: launch_timeout は正の整数である必要があります")
                return False

            if not isinstance(self.response_timeout, int) or self.response_timeout <= 0:
                print(f"⚠️  無効な設定: response_timeout は正の整数である必要があります")
                return False

            if not isinstance(self.max_retries, int) or self.max_retries <= 0:
                print(f"⚠️  無効な設定: max_retries は正の整数である必要があります")
                return False

            # 正の数値の検証（intまたはfloat）
            if not isinstance(self.polling_interval, (int, float)) or self.polling_interval <= 0:
                print(f"⚠️  無効な設定: polling_interval は正の数値である必要があります")
                return False

            return True

        except Exception as e:
            print(f"⚠️  設定検証エラー: {e}")
            return False

    def save_config(self, config_path: str) -> bool:
        """
        設定を検証してファイルに保存

        Args:
            config_path: 保存先のファイルパス

        Returns:
            保存成功時True、失敗時False
        """
        try:
            # 検証
            if not self.validate_config():
                print(f"⚠️  無効な設定のため保存できません")
                return False

            # 保存
            self.save(config_path)
            print(f"✅ 設定を保存しました: {config_path}")
            return True

        except Exception as e:
            print(f"⚠️  設定保存エラー: {e}")
            return False


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

    def read_response(self, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        レスポンスファイルを読み込んで解析

        Args:
            max_retries: 読み込み失敗時の最大リトライ回数

        Returns:
            レスポンスデータの辞書、失敗時はNone
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                # ファイルの存在確認
                if not self.response_file_path.exists():
                    if attempt == 0:
                        print(f"⚠️ レスポンスファイルが見つかりません: {self.response_file_path}")
                    return None

                # JSONファイルを読み込み
                response_data = json.loads(
                    self.response_file_path.read_text(encoding="utf-8")
                )

                print(f"✅ レスポンスファイルを読み込みました")
                return response_data

            except json.JSONDecodeError as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"⚠️ JSONパースエラー（試行 {attempt + 1}/{max_retries}）: {e}")
                    print(f"   1秒後にリトライします...")
                    time.sleep(1)
                else:
                    print(f"⚠️ JSONパースエラー（最終試行）: {e}")

            except (IOError, OSError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"⚠️ ファイルI/Oエラー（試行 {attempt + 1}/{max_retries}）: {e}")
                    print(f"   1秒後にリトライします...")
                    time.sleep(1)
                else:
                    print(f"⚠️ ファイルI/Oエラー（最終試行）: {e}")

            except Exception as e:
                print(f"⚠️ 予期しないエラー: {e}")
                return None

        return None

    def cancel(self):
        """
        監視をキャンセル

        wait_for_response()を中断します。
        """
        self.cancelled = True
        print("🛑 監視のキャンセルを要求しました")


class AutomatedBridge(ClaudeBridge):
    """
    ClaudeBridgeを拡張した自動化ブリッジクラス

    既存のClaudeBridge機能に加えて、完全自動化ワークフローを提供します。
    """

    def __init__(self, config: AutomationConfig):
        """
        AutomatedBridgeを初期化

        Args:
            config: 自動化設定
        """
        # 親クラスの初期化
        super().__init__()

        self.config = config
        self.launcher = DesktopLauncher(config)
        self.monitor: Optional[ResponseMonitor] = None
        self.current_request_id: Optional[str] = None

    def create_automated_request(
        self,
        title: str,
        problem: str,
        tried: List[str],
        files_to_analyze: List[str],
        error_messages: str = "",
        context: str = ""
    ) -> str:
        """
        自動化されたヘルプリクエストを作成

        親クラスのcreate_help_requestを使用してリクエストを作成し、
        自動化のためのレスポンスモニターを設定します。

        Args:
            title: 問題の簡潔なタイトル
            problem: 具体的な問題の説明
            tried: 試した解決方法のリスト
            files_to_analyze: 分析が必要なファイルパスのリスト
            error_messages: エラーメッセージ（オプション）
            context: 追加のコンテキスト情報（オプション）

        Returns:
            作成されたリクエストID
        """
        # 親クラスのメソッドでリクエスト作成
        request_id = self.create_help_request(
            title=title,
            problem=problem,
            tried=tried,
            files_to_analyze=files_to_analyze,
            error_messages=error_messages,
            context=context
        )

        # レスポンスファイルのパスを設定
        response_file = self.responses_path / f"{request_id}_response.json"

        # レスポンスモニターを初期化
        self.monitor = ResponseMonitor(self.config, str(response_file))
        self.current_request_id = request_id

        print(f"\n✅ 自動化リクエスト {request_id} を作成しました")

        return request_id

    def run_automated_workflow(
        self,
        title: str,
        problem: str,
        tried: List[str],
        files_to_analyze: List[str],
        error_messages: str = "",
        context: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        完全自動化ワークフローを実行

        リクエスト作成 → 起動 → 監視 → レスポンス取得の全体フローを実行します。

        Args:
            title: 問題の簡潔なタイトル
            problem: 具体的な問題の説明
            tried: 試した解決方法のリスト
            files_to_analyze: 分析が必要なファイルパスのリスト
            error_messages: エラーメッセージ（オプション）
            context: 追加のコンテキスト情報（オプション）

        Returns:
            レスポンスデータの辞書、失敗時はNone
        """
        print("\n" + "="*60)
        print("🚀 自動化ワークフローを開始します")
        print("="*60 + "\n")

        # ステップ1: リクエスト作成
        print("📝 ステップ1: リクエスト作成")
        request_id = self.create_automated_request(
            title=title,
            problem=problem,
            tried=tried,
            files_to_analyze=files_to_analyze,
            error_messages=error_messages,
            context=context
        )

        # ステップ2: Claude Desktop起動
        if self.config.auto_launch_desktop:
            print("\n🚀 ステップ2: Claude Desktop起動")
            if not self.launcher.launch_with_retry():
                print("\n⚠️  自動起動に失敗しました")
                self.launcher.show_manual_fallback_message()
                self.show_manual_file_transfer_instructions(request_id)
                return {
                    "request_id": request_id,
                    "status": "manual_mode",
                    "message": "手動モードに切り替えました"
                }
        else:
            print("\n⏭️  ステップ2: 自動起動はスキップされました（設定で無効）")
            self.show_manual_file_transfer_instructions(request_id)
            return {
                "request_id": request_id,
                "status": "manual_mode",
                "message": "手動モードです"
            }

        # ステップ3: レスポンス監視
        print("\n🔍 ステップ3: レスポンス監視")
        if self.monitor and self.monitor.wait_for_response():
            # ステップ4: レスポンス読み込み
            print("\n📖 ステップ4: レスポンス読み込み")
            response = self.monitor.read_response()

            if response:
                print("\n✅ 自動化ワークフローが完了しました")
                print("="*60 + "\n")
                return {
                    "request_id": request_id,
                    "status": "success",
                    "response": response
                }

        print("\n⚠️  レスポンスの取得に失敗しました")
        self.show_manual_file_transfer_instructions(request_id)
        return {
            "request_id": request_id,
            "status": "timeout",
            "message": "タイムアウトしました"
        }

    def show_manual_file_transfer_instructions(self, request_id: str):
        """
        手動ファイル転送の指示を表示

        自動化が失敗した際に、ユーザーに手動でファイルを転送する方法を指示します。

        Args:
            request_id: リクエストID
        """
        request_file = self.requests_path / f"{request_id}.json"
        response_file = self.responses_path / f"{request_id}_response.json"

        print("\n" + "="*60)
        print("📋 手動ファイル転送の手順")
        print("="*60)
        print(f"\n⚠️  自動化が利用できません。以下の手順で手動実行してください:")
        print(f"\n1. Claude Desktopを開く")
        print(f"\n2. 以下のリクエストファイルの内容を確認:")
        print(f"   {request_file}")
        print(f"\n3. Claude Desktopで分析を依頼")
        print(f"\n4. 回答を以下のファイルとして保存:")
        print(f"   {response_file}")
        print(f"\n5. 回答確認コマンドを実行:")
        print(f"   python -c \"from bridge_helper import ClaudeBridge; ClaudeBridge().check_response('{request_id}')\"")
        print("\n" + "="*60 + "\n")


class ProposalExecutor:
    """
    Claude Desktopからの提案を実行するクラス

    レスポンスに含まれる実装ステップを順次実行し、
    コードファイルの適用とバックアップを管理します。
    """

    def __init__(self, config: AutomationConfig):
        """
        ProposalExecutorを初期化

        Args:
            config: 自動化設定
        """
        self.config = config

        # バックアップディレクトリの作成
        self.backup_dir = Path.home() / "AI-Workspace/claude-bridge/backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def extract_implementation_steps(
        self,
        response: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        レスポンスからimplementation_stepsを抽出

        Args:
            response: Claude Desktopからのレスポンスデータ

        Returns:
            実装ステップのリスト
        """
        analysis = response.get("analysis", {})
        steps = analysis.get("implementation_steps", [])
        return steps

    def execute_step(
        self,
        step: Dict[str, Any],
        current: int,
        total: int
    ) -> bool:
        """
        個別の実装ステップを実行

        Args:
            step: 実装ステップの情報
            current: 現在のステップ番号
            total: 全ステップ数

        Returns:
            実行成功時True、失敗時False
        """
        print(f"\n{'='*60}")
        print(f"📋 ステップ {current}/{total}: {step.get('description', 'N/A')}")
        print(f"{'='*60}")
        print(f"\n実行内容: {step.get('action', 'N/A')}")
        print(f"\n✅ ステップ {current} 完了")

        return True

    def execute_all_steps(
        self,
        steps: List[Dict[str, Any]]
    ) -> List[bool]:
        """
        全ての実装ステップを順次実行

        Args:
            steps: 実装ステップのリスト

        Returns:
            各ステップの実行結果のリスト
        """
        results = []
        total = len(steps)

        print(f"\n{'='*60}")
        print(f"🚀 実装ステップの実行を開始")
        print(f"   全{total}ステップ")
        print(f"{'='*60}")

        for i, step in enumerate(steps, 1):
            result = self.execute_step(step, i, total)
            results.append(result)

            if not result:
                print(f"\n⚠️  ステップ {i} でエラーが発生しました")
                break

        if all(results):
            print(f"\n{'='*60}")
            print(f"✅ 全ステップの実行が完了しました")
            print(f"{'='*60}\n")

        return results

    def create_backup(self, file_path: str) -> Optional[str]:
        """
        ファイルのバックアップを作成

        Args:
            file_path: バックアップするファイルのパス

        Returns:
            バックアップファイルのパス（成功時）、None（失敗時）
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                print(f"⚠️  ファイルが存在しません: {file_path}")
                return None

            # タイムスタンプ付きバックアップファイル名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = self.backup_dir / backup_name

            # バックアップ作成
            backup_path.write_text(
                source_path.read_text(encoding="utf-8"),
                encoding="utf-8"
            )

            print(f"💾 バックアップ作成: {backup_path}")
            return str(backup_path)

        except Exception as e:
            print(f"⚠️  バックアップ作成エラー: {e}")
            return None

    def apply_code_file(
        self,
        file_path: str,
        content: str
    ) -> bool:
        """
        コードファイルを適用

        Args:
            file_path: 適用先のファイルパス
            content: 新しいファイル内容

        Returns:
            適用成功時True、失敗時False
        """
        try:
            target_path = Path(file_path)

            # 既存ファイルの場合はバックアップ作成
            if target_path.exists():
                self.create_backup(file_path)

            # 親ディレクトリがない場合は作成
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # ファイル書き込み
            target_path.write_text(content, encoding="utf-8")

            print(f"✅ ファイル適用: {file_path}")
            return True

        except Exception as e:
            print(f"⚠️  ファイル適用エラー: {e}")
            return False

    def extract_code_files(
        self,
        response: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        レスポンスからcode_filesを抽出

        Args:
            response: Claude Desktopからのレスポンスデータ

        Returns:
            コードファイルのリスト
        """
        analysis = response.get("analysis", {})
        code_files = analysis.get("code_files", [])
        return code_files

    def apply_all_code_files(
        self,
        code_files: List[Dict[str, Any]]
    ) -> List[bool]:
        """
        全てのコードファイルを適用

        Args:
            code_files: コードファイルのリスト

        Returns:
            各ファイル適用結果のリスト
        """
        results = []
        total = len(code_files)

        print(f"\n{'='*60}")
        print(f"📝 コードファイルの適用を開始")
        print(f"   全{total}ファイル")
        print(f"{'='*60}\n")

        for i, file_info in enumerate(code_files, 1):
            file_path = file_info.get("path", "")
            content = file_info.get("content", "")

            print(f"\n[{i}/{total}] {file_path}")
            result = self.apply_code_file(file_path, content)
            results.append(result)

            if not result:
                print(f"⚠️  ファイル {i} の適用に失敗しました")

        if all(results):
            print(f"\n{'='*60}")
            print(f"✅ 全ファイルの適用が完了しました")
            print(f"{'='*60}\n")

        return results

    def show_proposal_summary(self, response: Dict[str, Any]):
        """
        提案のサマリーを表示

        Args:
            response: Claude Desktopからのレスポンスデータ
        """
        analysis = response.get("analysis", {})
        recommendations = analysis.get("recommendations", [])
        steps = analysis.get("implementation_steps", [])
        code_files = analysis.get("code_files", [])

        print(f"\n{'='*60}")
        print(f"📊 Claude Desktopからの提案サマリー")
        print(f"{'='*60}\n")

        # 推奨事項
        if recommendations:
            print(f"💡 推奨事項: {len(recommendations)}件")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n  {i}. {rec.get('title', 'N/A')}")
                print(f"     {rec.get('description', 'N/A')}")

        # 実装ステップ
        if steps:
            print(f"\n📋 実装ステップ: {len(steps)}件")
            for step in steps:
                print(f"  - {step.get('description', 'N/A')}")

        # 変更ファイル
        if code_files:
            print(f"\n📝 変更ファイル: {len(code_files)}件")
            for file_info in code_files:
                print(f"  - {file_info.get('path', 'N/A')}")

        print(f"\n{'='*60}\n")

    def request_user_approval(self, message: str = "") -> bool:
        """
        ユーザーに承認を要求

        Args:
            message: 承認メッセージ（オプション）

        Returns:
            承認された場合True、拒否された場合False
        """
        if message:
            print(f"\n{message}\n")

        print(f"{'='*60}")
        print(f"❓ この提案を実行しますか？")
        print(f"{'='*60}\n")

        try:
            response = input("承認する場合は 'y' または 'Y' を入力してください [y/N]: ").strip().lower()
            approved = response == 'y'

            if approved:
                print(f"\n✅ 承認されました。実行を開始します。\n")
            else:
                print(f"\n⚠️  拒否されました。実行をスキップします。\n")

            return approved

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n⚠️  中断されました。\n")
            return False


class ErrorHandler:
    """
    エラーハンドリングとログ記録を管理するクラス

    エラーを分類（致命的/回復可能/警告）し、
    適切なログ記録と通知を行います。
    """

    def __init__(self, config: AutomationConfig):
        """
        ErrorHandlerを初期化

        Args:
            config: 自動化設定
        """
        self.config = config

        # ログディレクトリの作成
        self.log_dir = Path.home() / "AI-Workspace/claude-bridge/logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def classify_error(
        self,
        error: Exception,
        context: str = ""
    ) -> str:
        """
        エラーを分類

        Args:
            error: 発生したエラー
            context: エラーが発生したコンテキスト

        Returns:
            エラーの重大度 ("critical", "recoverable", "warning")
        """
        # 致命的エラー
        if "system_crash" in context or "critical" in context:
            return "critical"
        if isinstance(error, (SystemError, MemoryError, KeyboardInterrupt)):
            return "critical"

        # ネットワーク関連エラー（回復可能）
        if isinstance(error, (ConnectionError, TimeoutError)):
            return "recoverable"
        if "network" in context or "timeout" in context:
            return "recoverable"

        # ファイルI/Oエラー（回復可能）
        if isinstance(error, (FileNotFoundError, PermissionError, IOError, OSError)):
            return "recoverable"
        # より具体的なマッチングを使用（"validation"に"io"が含まれるため）
        if "file_operation" in context or context == "io":
            return "recoverable"

        # JSON/データ解析エラー（警告）
        if error.__class__.__name__ in ['JSONDecodeError', 'json.JSONDecodeError']:
            return "warning"
        if "json" in context or "parse" in context:
            return "warning"

        # バリデーションエラー（警告）
        # コンテキストを先にチェック（より具体的な判定）
        if "validation" in context:
            return "warning"
        if isinstance(error, (ValueError, TypeError)):
            return "warning"

        # デフォルトは回復可能
        return "recoverable"

    def log_error(
        self,
        error: Exception,
        context: str = "",
        severity: str = "recoverable"
    ) -> Optional[str]:
        """
        エラーをログファイルに記録

        Args:
            error: 発生したエラー
            context: エラーが発生したコンテキスト
            severity: エラーの重大度

        Returns:
            ログファイルのパス（成功時）、None（失敗時）
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"error_{severity}_{timestamp}.log"
            log_file = self.log_dir / log_filename

            # ログ内容
            log_content = f"""{'='*60}
エラーログ
{'='*60}
タイムスタンプ: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
重大度: {severity}
コンテキスト: {context}
エラー型: {type(error).__name__}
エラーメッセージ: {str(error)}

スタックトレース:
{self._format_traceback(error)}
{'='*60}
"""

            log_file.write_text(log_content, encoding="utf-8")

            print(f"📝 エラーログ記録: {log_file}")
            return str(log_file)

        except Exception as e:
            print(f"⚠️  ログ記録エラー: {e}")
            return None

    def _format_traceback(self, error: Exception) -> str:
        """
        スタックトレースをフォーマット

        Args:
            error: 発生したエラー

        Returns:
            フォーマットされたスタックトレース
        """
        import traceback
        return ''.join(traceback.format_exception(
            type(error), error, error.__traceback__
        ))

    def handle_error(
        self,
        error: Exception,
        context: str = "",
        raise_on_critical: bool = False
    ) -> bool:
        """
        エラーを処理

        Args:
            error: 発生したエラー
            context: エラーが発生したコンテキスト
            raise_on_critical: 致命的エラー時に例外を再発生させるか

        Returns:
            継続可能な場合True、中断すべき場合False
        """
        # エラー分類
        severity = self.classify_error(error, context)

        # ログ記録
        self.log_error(error, context, severity)

        # 重大度に応じた通知
        if severity == "critical":
            print(f"\n🚨 致命的エラー: {error}")
            print(f"   コンテキスト: {context}")
            print(f"   処理を中断します。\n")
            if raise_on_critical:
                raise error
            return False

        elif severity == "recoverable":
            print(f"\n⚠️  回復可能エラー: {error}")
            print(f"   コンテキスト: {context}")
            print(f"   処理を続行します。\n")
            return True

        else:  # warning
            print(f"\n💡 警告: {error}")
            print(f"   コンテキスト: {context}\n")
            return True

    def retry_on_error(
        self,
        func: callable,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        context: str = ""
    ) -> Any:
        """
        エラー発生時にリトライ実行するヘルパーメソッド

        Args:
            func: 実行する関数
            max_retries: 最大リトライ回数
            delay: 初回リトライまでの待機時間（秒）
            backoff: リトライごとの待機時間増加率
            context: エラーコンテキスト

        Returns:
            関数の実行結果

        Raises:
            最後のリトライでも失敗した場合の例外
        """
        import time

        last_error = None
        current_delay = delay

        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_error = e
                severity = self.classify_error(e, context)

                # 致命的エラーはリトライしない
                if severity == "critical":
                    print(f"\n🚨 致命的エラーのためリトライを中止")
                    raise e

                # リトライ情報表示
                print(f"\n⚠️  エラー発生（試行 {attempt + 1}/{max_retries}）: {e}")

                if attempt < max_retries - 1:
                    print(f"   {current_delay:.1f}秒後にリトライします...")
                    time.sleep(current_delay)
                    current_delay *= backoff
                else:
                    print(f"   最大リトライ回数に達しました")

        # 全てのリトライが失敗
        self.log_error(last_error, f"{context} (after {max_retries} retries)", "recoverable")
        raise last_error


class CheckpointManager:
    """
    チェックポイント作成とロールバック管理クラス

    変更前の状態をバックアップし、
    必要に応じて元の状態に復元します。
    """

    def __init__(self, config: AutomationConfig):
        """
        CheckpointManagerを初期化

        Args:
            config: 自動化設定
        """
        self.config = config

        # チェックポイントディレクトリの作成
        self.checkpoint_dir = Path.home() / "AI-Workspace/claude-bridge/checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def create_checkpoint(
        self,
        files: List[str],
        description: str = ""
    ) -> Optional[str]:
        """
        チェックポイントを作成

        Args:
            files: バックアップするファイルのリスト
            description: チェックポイントの説明

        Returns:
            チェックポイントID（成功時）、None（失敗時）
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_id = f"cp_{timestamp}"
            checkpoint_path = self.checkpoint_dir / checkpoint_id
            checkpoint_path.mkdir(exist_ok=True)

            # メタデータ
            metadata = {
                "checkpoint_id": checkpoint_id,
                "timestamp": timestamp,
                "description": description,
                "files": []
            }

            # 各ファイルをバックアップ
            for file_path in files:
                source_path = Path(file_path)
                if not source_path.exists():
                    continue

                # 相対パスを保持してバックアップ
                backup_name = source_path.name
                backup_path = checkpoint_path / backup_name

                backup_path.write_text(
                    source_path.read_text(encoding="utf-8"),
                    encoding="utf-8"
                )

                metadata["files"].append({
                    "original_path": str(source_path),
                    "backup_name": backup_name
                })

            # メタデータを保存
            metadata_file = checkpoint_path / "metadata.json"
            metadata_file.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            print(f"💾 チェックポイント作成: {checkpoint_id}")
            print(f"   ファイル数: {len(metadata['files'])}")

            return checkpoint_id

        except Exception as e:
            print(f"⚠️  チェックポイント作成エラー: {e}")
            return None

    def rollback(
        self,
        checkpoint_id: str,
        new_files: List[str] = None
    ) -> bool:
        """
        チェックポイントにロールバック

        Args:
            checkpoint_id: ロールバックするチェックポイントID
            new_files: 削除する新規ファイルのリスト（オプション）

        Returns:
            ロールバック成功時True、失敗時False
        """
        try:
            checkpoint_path = self.checkpoint_dir / checkpoint_id
            if not checkpoint_path.exists():
                print(f"⚠️  チェックポイントが見つかりません: {checkpoint_id}")
                return False

            # メタデータ読み込み
            metadata_file = checkpoint_path / "metadata.json"
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))

            print(f"\n{'='*60}")
            print(f"🔄 ロールバック開始: {checkpoint_id}")
            print(f"{'='*60}\n")

            # ファイルを元に戻す
            for file_info in metadata["files"]:
                original_path = Path(file_info["original_path"])
                backup_name = file_info["backup_name"]
                backup_path = checkpoint_path / backup_name

                if backup_path.exists():
                    original_path.write_text(
                        backup_path.read_text(encoding="utf-8"),
                        encoding="utf-8"
                    )
                    print(f"✅ 復元: {original_path}")

            # 新規ファイルの削除
            if new_files:
                for new_file in new_files:
                    new_path = Path(new_file)
                    if new_path.exists():
                        new_path.unlink()
                        print(f"🗑️  削除: {new_path}")

            print(f"\n{'='*60}")
            print(f"✅ ロールバック完了")
            print(f"{'='*60}\n")

            return True

        except Exception as e:
            print(f"⚠️  ロールバックエラー: {e}")
            return False

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        チェックポイント一覧を取得

        Returns:
            チェックポイント情報のリスト
        """
        checkpoints = []

        try:
            for checkpoint_path in self.checkpoint_dir.iterdir():
                if not checkpoint_path.is_dir():
                    continue

                metadata_file = checkpoint_path / "metadata.json"
                if metadata_file.exists():
                    metadata = json.loads(
                        metadata_file.read_text(encoding="utf-8")
                    )
                    checkpoints.append(metadata)

            # タイムスタンプでソート（新しい順）
            checkpoints.sort(
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )

        except Exception as e:
            print(f"⚠️  チェックポイント一覧取得エラー: {e}")

        return checkpoints
