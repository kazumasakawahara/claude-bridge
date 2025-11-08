#!/usr/bin/env python3
"""
Claude Bridge ステータスダッシュボード

システムの実行状況を可視化します:
- アクティブなリクエスト
- 自動化ステータス
- エラーログ
- パフォーマンス統計
- システムヘルス
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# claude-bridgeパスを追加
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))

from automation_helper import AutomationConfig, AutomatedBridge


class DashboardData:
    """ダッシュボードデータ収集クラス"""

    def __init__(self):
        self.bridge_dir = Path.home() / "AI-Workspace/claude-bridge"
        self.requests_dir = self.bridge_dir / "help-requests"
        self.responses_dir = self.bridge_dir / "help-responses"
        self.logs_dir = self.bridge_dir / "logs"
        self.archive_dir = self.bridge_dir / "archive"
        self.checkpoints_dir = self.bridge_dir / "checkpoints"
        self.backups_dir = self.bridge_dir / "backups"

        # 設定読み込み
        config_file = self.bridge_dir / "automation_config.json"
        if config_file.exists():
            self.config = AutomationConfig.load(str(config_file))
        else:
            self.config = AutomationConfig()

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """未回答のリクエストを取得"""
        pending = []

        if not self.requests_dir.exists():
            return pending

        for request_file in self.requests_dir.glob("req_*.json"):
            request_id = request_file.stem
            response_file = self.responses_dir / f"{request_id}_response.json"

            if not response_file.exists():
                try:
                    data = json.loads(request_file.read_text(encoding="utf-8"))
                    # ファイルのタイムスタンプを取得
                    created_time = datetime.fromtimestamp(request_file.stat().st_mtime)
                    age = datetime.now() - created_time

                    pending.append({
                        "id": request_id,
                        "title": data.get("title", "Unknown"),
                        "created": created_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "age_hours": age.total_seconds() / 3600,
                        "files_count": len(data.get("files_to_analyze", []))
                    })
                except Exception:
                    pass

        return sorted(pending, key=lambda x: x["age_hours"], reverse=True)

    def get_completed_requests(self, limit: int = 5) -> List[Dict[str, Any]]:
        """完了したリクエストを取得（最新のものから）"""
        completed = []

        if not self.responses_dir.exists():
            return completed

        for response_file in self.responses_dir.glob("req_*_response.json"):
            try:
                data = json.loads(response_file.read_text(encoding="utf-8"))
                request_id = data.get("request_id", "unknown")

                # レスポンスのタイムスタンプ
                completed_time = datetime.fromtimestamp(response_file.stat().st_mtime)

                completed.append({
                    "id": request_id,
                    "completed": completed_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "recommendations": len(data.get("analysis", {}).get("recommendations", [])),
                    "has_code": bool(data.get("code_files", {}))
                })
            except Exception:
                pass

        return sorted(completed, key=lambda x: x["completed"], reverse=True)[:limit]

    def get_error_summary(self) -> Dict[str, Any]:
        """エラーログのサマリーを取得"""
        errors = {
            "total": 0,
            "critical": 0,
            "recoverable": 0,
            "warning": 0,
            "recent": []
        }

        if not self.logs_dir.exists():
            return errors

        # 過去24時間のエラーログを確認
        cutoff_time = datetime.now() - timedelta(hours=24)

        for log_file in self.logs_dir.glob("error_*.json"):
            try:
                # ファイルのタイムスタンプを確認
                log_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if log_time < cutoff_time:
                    continue

                data = json.loads(log_file.read_text(encoding="utf-8"))
                severity = data.get("severity", "unknown")

                errors["total"] += 1

                if severity == "critical":
                    errors["critical"] += 1
                elif severity == "recoverable":
                    errors["recoverable"] += 1
                elif severity == "warning":
                    errors["warning"] += 1

                # 最近のエラー（最大5件）
                if len(errors["recent"]) < 5:
                    errors["recent"].append({
                        "time": log_time.strftime("%H:%M:%S"),
                        "severity": severity,
                        "error": data.get("error_type", "Unknown"),
                        "context": data.get("context", "")
                    })

            except Exception:
                pass

        return errors

    def get_system_stats(self) -> Dict[str, Any]:
        """システム統計を取得"""
        stats = {
            "total_requests": 0,
            "total_responses": 0,
            "archived": 0,
            "checkpoints": 0,
            "backups": 0,
            "disk_usage_mb": 0
        }

        # リクエスト数
        if self.requests_dir.exists():
            stats["total_requests"] = len(list(self.requests_dir.glob("req_*.json")))

        # レスポンス数
        if self.responses_dir.exists():
            stats["total_responses"] = len(list(self.responses_dir.glob("req_*_response.json")))

        # アーカイブ数
        if self.archive_dir.exists():
            stats["archived"] = len(list(self.archive_dir.glob("req_*.json")))

        # チェックポイント数
        if self.checkpoints_dir.exists():
            stats["checkpoints"] = len(list(self.checkpoints_dir.glob("checkpoint_*.json")))

        # バックアップ数
        if self.backups_dir.exists():
            stats["backups"] = len(list(self.backups_dir.glob("*")))

        # ディスク使用量（概算）
        try:
            total_size = 0
            for directory in [self.requests_dir, self.responses_dir, self.archive_dir,
                              self.checkpoints_dir, self.backups_dir, self.logs_dir]:
                if directory.exists():
                    for file in directory.rglob("*"):
                        if file.is_file():
                            total_size += file.stat().st_size
            stats["disk_usage_mb"] = total_size / (1024 * 1024)
        except Exception:
            stats["disk_usage_mb"] = 0

        return stats

    def get_automation_status(self) -> Dict[str, Any]:
        """自動化ステータスを取得"""
        return {
            "enabled": self.config.enabled,
            "auto_launch": self.config.auto_launch_desktop,
            "desktop_app": self.config.desktop_app_name,
            "launch_timeout": self.config.launch_timeout,
            "response_timeout": self.config.response_timeout,
            "polling_interval": self.config.polling_interval,
            "max_retries": self.config.max_retries
        }


class Dashboard:
    """ダッシュボード表示クラス"""

    def __init__(self):
        self.data = DashboardData()

    def print_header(self, title: str):
        """ヘッダーを表示"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")

    def print_section(self, title: str):
        """セクションタイトルを表示"""
        print(f"\n{title}")
        print("-" * 60)

    def display_overview(self):
        """概要を表示"""
        self.print_header("Claude Bridge ステータスダッシュボード")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"📅 現在時刻: {now}\n")

        # システム統計
        stats = self.data.get_system_stats()
        print("📊 システム統計:")
        print(f"  総リクエスト数: {stats['total_requests']}")
        print(f"  総レスポンス数: {stats['total_responses']}")
        print(f"  アーカイブ済み: {stats['archived']}")
        print(f"  チェックポイント: {stats['checkpoints']}")
        print(f"  バックアップ: {stats['backups']}")
        print(f"  ディスク使用量: {stats['disk_usage_mb']:.2f} MB")

    def display_automation_status(self):
        """自動化ステータスを表示"""
        self.print_section("🤖 自動化ステータス")

        status = self.data.get_automation_status()

        enabled_icon = "✅" if status["enabled"] else "❌"
        auto_launch_icon = "✅" if status["auto_launch"] else "❌"

        print(f"  自動化有効: {enabled_icon} {status['enabled']}")
        print(f"  自動起動: {auto_launch_icon} {status['auto_launch']}")
        print(f"  アプリケーション名: {status['desktop_app']}")
        print(f"  起動タイムアウト: {status['launch_timeout']}秒")
        print(f"  レスポンスタイムアウト: {status['response_timeout']}秒")
        print(f"  ポーリング間隔: {status['polling_interval']}秒")
        print(f"  最大リトライ回数: {status['max_retries']}回")

    def display_pending_requests(self):
        """未回答リクエストを表示"""
        self.print_section("⏳ 未回答リクエスト")

        pending = self.data.get_pending_requests()

        if not pending:
            print("  なし")
            return

        for req in pending:
            age_str = f"{req['age_hours']:.1f}時間前" if req['age_hours'] < 24 else f"{req['age_hours']/24:.1f}日前"
            print(f"\n  📋 {req['id']}")
            print(f"     タイトル: {req['title']}")
            print(f"     作成日時: {req['created']} ({age_str})")
            print(f"     分析ファイル数: {req['files_count']}")

    def display_completed_requests(self):
        """完了リクエストを表示"""
        self.print_section("✅ 最近完了したリクエスト（最新5件）")

        completed = self.data.get_completed_requests(limit=5)

        if not completed:
            print("  なし")
            return

        for req in completed:
            code_icon = "💾" if req['has_code'] else "📝"
            print(f"\n  {code_icon} {req['id']}")
            print(f"     完了日時: {req['completed']}")
            print(f"     推奨事項数: {req['recommendations']}")

    def display_error_summary(self):
        """エラーサマリーを表示"""
        self.print_section("⚠️  エラーサマリー（過去24時間）")

        errors = self.data.get_error_summary()

        if errors["total"] == 0:
            print("  ✅ エラーなし")
            return

        print(f"  総エラー数: {errors['total']}")
        print(f"    🚨 致命的: {errors['critical']}")
        print(f"    🔄 回復可能: {errors['recoverable']}")
        print(f"    ⚠️  警告: {errors['warning']}")

        if errors["recent"]:
            print("\n  最近のエラー:")
            for error in errors["recent"]:
                severity_icon = {
                    "critical": "🚨",
                    "recoverable": "🔄",
                    "warning": "⚠️"
                }.get(error["severity"], "❓")

                print(f"    {severity_icon} [{error['time']}] {error['error']}")
                if error["context"]:
                    print(f"       コンテキスト: {error['context']}")

    def display_health_check(self):
        """システムヘルスチェックを表示"""
        self.print_section("🏥 システムヘルスチェック")

        bridge_dir = Path.home() / "AI-Workspace/claude-bridge"

        # 必須ディレクトリのチェック
        required_dirs = {
            "help-requests": bridge_dir / "help-requests",
            "help-responses": bridge_dir / "help-responses",
            "logs": bridge_dir / "logs",
            "archive": bridge_dir / "archive",
            "checkpoints": bridge_dir / "checkpoints",
            "backups": bridge_dir / "backups"
        }

        all_healthy = True
        for name, path in required_dirs.items():
            if path.exists():
                print(f"  ✅ {name}/")
            else:
                print(f"  ❌ {name}/ が見つかりません")
                all_healthy = False

        # 必須ファイルのチェック
        required_files = {
            "bridge_helper.py": bridge_dir / "bridge_helper.py",
            "automation_helper.py": bridge_dir / "automation_helper.py",
            "configure.py": bridge_dir / "configure.py"
        }

        for name, path in required_files.items():
            if path.exists():
                print(f"  ✅ {name}")
            else:
                print(f"  ❌ {name} が見つかりません")
                all_healthy = False

        # 設定ファイルのチェック
        config_file = bridge_dir / "automation_config.json"
        if config_file.exists():
            print(f"  ✅ automation_config.json")
        else:
            print(f"  ⚠️  automation_config.json が見つかりません（デフォルト設定使用）")

        print()
        if all_healthy:
            print("  🎉 システムは正常に動作しています")
        else:
            print("  ⚠️  一部のファイルが不足しています")

    def display_all(self):
        """全ての情報を表示"""
        self.display_overview()
        self.display_automation_status()
        self.display_pending_requests()
        self.display_completed_requests()
        self.display_error_summary()
        self.display_health_check()

        print("\n" + "="*60)
        print()


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Claude Bridge ステータスダッシュボード',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 dashboard.py              # 全ての情報を表示
  python3 dashboard.py --pending    # 未回答リクエストのみ表示
  python3 dashboard.py --errors     # エラーサマリーのみ表示
  python3 dashboard.py --health     # ヘルスチェックのみ表示
        """
    )

    parser.add_argument(
        '--pending',
        action='store_true',
        help='未回答リクエストのみ表示'
    )

    parser.add_argument(
        '--completed',
        action='store_true',
        help='完了リクエストのみ表示'
    )

    parser.add_argument(
        '--errors',
        action='store_true',
        help='エラーサマリーのみ表示'
    )

    parser.add_argument(
        '--health',
        action='store_true',
        help='ヘルスチェックのみ表示'
    )

    parser.add_argument(
        '--automation',
        action='store_true',
        help='自動化ステータスのみ表示'
    )

    args = parser.parse_args()

    dashboard = Dashboard()

    # オプションが指定されている場合は該当セクションのみ表示
    if args.pending or args.completed or args.errors or args.health or args.automation:
        if args.pending:
            dashboard.display_pending_requests()
        if args.completed:
            dashboard.display_completed_requests()
        if args.errors:
            dashboard.display_error_summary()
        if args.health:
            dashboard.display_health_check()
        if args.automation:
            dashboard.display_automation_status()
    else:
        # オプションなしの場合は全て表示
        dashboard.display_all()


if __name__ == "__main__":
    main()
