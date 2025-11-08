#!/usr/bin/env python3
"""
Claude Bridge 設定管理CLIツール

対話的に自動化設定を作成・編集します。
"""

import sys
from pathlib import Path
from automation_helper import AutomationConfig


def print_header(title: str):
    """ヘッダーを表示"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """
    Yes/No質問をする

    Args:
        prompt: 質問文
        default: デフォルト値

    Returns:
        ユーザーの回答（True/False）
    """
    default_text = "Y/n" if default else "y/N"
    while True:
        response = input(f"{prompt} [{default_text}]: ").strip().lower()

        if not response:
            return default

        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("⚠️  'y' または 'n' を入力してください")


def get_integer(prompt: str, default: int, min_val: int = 1, max_val: int = None) -> int:
    """
    整数値を入力させる

    Args:
        prompt: 質問文
        default: デフォルト値
        min_val: 最小値
        max_val: 最大値（Noneの場合は制限なし）

    Returns:
        ユーザーの入力値
    """
    while True:
        response = input(f"{prompt} [デフォルト: {default}]: ").strip()

        if not response:
            return default

        try:
            value = int(response)

            if value < min_val:
                print(f"⚠️  {min_val}以上の値を入力してください")
                continue

            if max_val is not None and value > max_val:
                print(f"⚠️  {max_val}以下の値を入力してください")
                continue

            return value

        except ValueError:
            print("⚠️  整数を入力してください")


def get_float(prompt: str, default: float, min_val: float = 0.1, max_val: float = None) -> float:
    """
    小数値を入力させる

    Args:
        prompt: 質問文
        default: デフォルト値
        min_val: 最小値
        max_val: 最大値（Noneの場合は制限なし）

    Returns:
        ユーザーの入力値
    """
    while True:
        response = input(f"{prompt} [デフォルト: {default}]: ").strip()

        if not response:
            return default

        try:
            value = float(response)

            if value < min_val:
                print(f"⚠️  {min_val}以上の値を入力してください")
                continue

            if max_val is not None and value > max_val:
                print(f"⚠️  {max_val}以下の値を入力してください")
                continue

            return value

        except ValueError:
            print("⚠️  数値を入力してください")


def configure_basic_settings(config: AutomationConfig):
    """基本設定を対話的に設定"""
    print_header("基本設定")

    print("📝 自動化機能の基本設定を行います\n")

    # 自動化の有効/無効
    config.enabled = get_yes_no(
        "自動化機能を有効にしますか？",
        default=config.enabled
    )

    if not config.enabled:
        print("\n💡 自動化は無効化されました。手動モードで動作します。")
        return

    # Claude Desktop自動起動
    config.auto_launch_desktop = get_yes_no(
        "Claude Desktopを自動起動しますか？",
        default=config.auto_launch_desktop
    )

    if not config.auto_launch_desktop:
        print("\n💡 Claude Desktopは手動で起動する必要があります。")


def configure_timeout_settings(config: AutomationConfig):
    """タイムアウト設定を対話的に設定"""
    print_header("タイムアウト設定")

    print("⏱️  各処理のタイムアウト時間を設定します\n")

    # 起動タイムアウト
    print("Claude Desktop起動のタイムアウト:")
    print("  - 推奨値: 10-30秒")
    print("  - 起動が遅い場合は長めに設定")
    config.launch_timeout = get_integer(
        "\n起動タイムアウト（秒）",
        default=config.launch_timeout,
        min_val=5,
        max_val=120
    )

    # レスポンスタイムアウト
    print("\nClaude Desktopからのレスポンス待機時間:")
    print("  - 推奨値: 1800秒（30分）")
    print("  - 複雑な分析には時間がかかります")
    config.response_timeout = get_integer(
        "\nレスポンスタイムアウト（秒）",
        default=config.response_timeout,
        min_val=60,
        max_val=7200
    )


def configure_advanced_settings(config: AutomationConfig):
    """高度な設定を対話的に設定"""
    print_header("高度な設定")

    print("⚙️  高度な設定を行います\n")

    # ポーリング間隔
    print("レスポンスファイル監視のポーリング間隔:")
    print("  - 推奨値: 1.0秒")
    print("  - 短すぎるとCPU使用率が上がります")
    config.polling_interval = get_float(
        "\nポーリング間隔（秒）",
        default=config.polling_interval,
        min_val=0.5,
        max_val=10.0
    )

    # 最大リトライ回数
    print("\n起動失敗時の最大リトライ回数:")
    print("  - 推奨値: 3回")
    print("  - 0にするとリトライしません")
    config.max_retries = get_integer(
        "\n最大リトライ回数",
        default=config.max_retries,
        min_val=0,
        max_val=10
    )


def show_config_summary(config: AutomationConfig):
    """設定内容のサマリーを表示"""
    print_header("設定内容の確認")

    print("📋 以下の設定が適用されます:\n")

    print("【基本設定】")
    print(f"  自動化有効: {'✅ はい' if config.enabled else '❌ いいえ'}")
    print(f"  Claude Desktop自動起動: {'✅ はい' if config.auto_launch_desktop else '❌ いいえ'}")
    print(f"  アプリケーション名: {config.desktop_app_name}")

    print("\n【タイムアウト設定】")
    print(f"  起動タイムアウト: {config.launch_timeout}秒")
    print(f"  レスポンスタイムアウト: {config.response_timeout}秒")

    print("\n【高度な設定】")
    print(f"  ポーリング間隔: {config.polling_interval}秒")
    print(f"  最大リトライ回数: {config.max_retries}回")
    print(f"  バックアップ作成: {'✅ はい' if config.create_backups else '❌ いいえ'}")
    print(f"  提案自動実行: {'✅ はい' if config.auto_execute_proposals else '❌ いいえ'}")


def interactive_configuration():
    """対話的な設定フロー"""
    print("\n" + "="*60)
    print("  Claude Bridge 設定ツール")
    print("="*60)
    print("\nこのツールで自動化機能の設定を行います。")
    print("各質問に答えるか、Enterキーでデフォルト値を使用できます。\n")

    # 既存設定の確認
    config_file = Path("automation_config.json")
    if config_file.exists():
        print(f"✅ 既存の設定ファイルが見つかりました: {config_file}")
        use_existing = get_yes_no("既存の設定を読み込みますか？", default=True)

        if use_existing:
            config = AutomationConfig.load(str(config_file))
            print("✅ 既存の設定を読み込みました")
        else:
            config = AutomationConfig()
            print("✅ デフォルト設定で開始します")
    else:
        config = AutomationConfig()
        print("✅ 新しい設定を作成します")

    # 設定ステップ
    try:
        configure_basic_settings(config)
        configure_timeout_settings(config)

        # 高度な設定（オプション）
        if get_yes_no("\n高度な設定を行いますか？", default=False):
            configure_advanced_settings(config)
        else:
            print("\n💡 高度な設定はスキップされました。デフォルト値が使用されます。")

        # 設定確認
        show_config_summary(config)

        # 保存確認
        if not get_yes_no("\nこの設定を保存しますか？", default=True):
            print("\n⚠️  設定は保存されませんでした")
            return 1

        # 設定検証
        if not config.validate_config():
            print("\n❌ 設定の検証に失敗しました")
            return 1

        # 保存
        save_path = "automation_config.json"
        config.save(save_path)

        print(f"\n✅ 設定を保存しました: {save_path}")
        print("\n次のステップ:")
        print("  1. 自動化ブリッジを使用: AutomatedBridge()")
        print("  2. 設定の再編集: python3 configure.py")
        print("  3. 使用例を確認: EXAMPLES.md を参照")

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  設定がキャンセルされました")
        return 1
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1


def quick_setup():
    """クイックセットアップ（デフォルト値で設定）"""
    print_header("クイックセットアップ")

    config = AutomationConfig()
    print("⚡ デフォルト設定で自動化を設定します\n")

    show_config_summary(config)

    if not get_yes_no("\nこの設定で進めますか？", default=True):
        print("\n⚠️  クイックセットアップをキャンセルしました")
        return 1

    save_path = "automation_config.json"
    config.save(save_path)

    print(f"\n✅ 設定を保存しました: {save_path}")
    print("\n🎉 クイックセットアップが完了しました！")
    print("\n次のステップ:")
    print("  python3 -c \"from automation_helper import AutomatedBridge; bridge = AutomatedBridge()\"")

    return 0


def show_current_config():
    """現在の設定を表示"""
    print_header("現在の設定")

    config_file = Path("automation_config.json")

    if not config_file.exists():
        print("❌ 設定ファイルが見つかりません")
        print("\n設定を作成するには:")
        print("  python3 configure.py")
        return 1

    config = AutomationConfig.load(str(config_file))
    show_config_summary(config)

    return 0


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Claude Bridge 設定管理ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 configure.py              # 対話的な設定
  python3 configure.py --quick      # クイックセットアップ
  python3 configure.py --show       # 現在の設定を表示
        """
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='クイックセットアップ（デフォルト値使用）'
    )

    parser.add_argument(
        '--show',
        action='store_true',
        help='現在の設定を表示'
    )

    args = parser.parse_args()

    # モード選択
    if args.show:
        return show_current_config()
    elif args.quick:
        return quick_setup()
    else:
        return interactive_configuration()


if __name__ == "__main__":
    sys.exit(main())
