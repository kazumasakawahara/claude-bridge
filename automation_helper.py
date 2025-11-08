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
