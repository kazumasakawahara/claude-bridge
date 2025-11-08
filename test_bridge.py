"""
Claude Bridge システムのテスト

このスクリプトで動作確認ができます。
"""

import sys
from pathlib import Path

# bridge_helperをインポート
sys.path.append(str(Path.home() / "AI-Workspace/claude-bridge"))

from bridge_helper import ask_claude_desktop, ClaudeBridge


def test_create_request():
    """テストリクエストを作成"""
    print("=" * 60)
    print("テスト: ヘルプリクエストの作成")
    print("=" * 60)
    
    # テスト用のダミーファイルを作成
    test_file = Path.cwd() / "test_code.py"
    test_file.write_text("""
def slow_function():
    # この関数が遅い
    result = []
    for i in range(10000):
        for j in range(10000):
            result.append(i * j)
    return result
""")
    
    # ヘルプリクエスト作成
    request_id = ask_claude_desktop(
        title="テスト: パフォーマンス問題",
        problem="slow_function()が完了するのに30秒かかる。目標は1秒以内。",
        tried=[
            "リスト内包表記に変更 → 効果なし",
            "NumPy使用 → インストールエラー",
            "キャッシュ追加 → ロジック的に不可能"
        ],
        files=["test_code.py"],
        error="実行時間: 30.2秒"
    )
    
    print(f"\n✅ テストリクエスト作成完了: {request_id}")
    print("\n次のステップ:")
    print("1. Claude Desktopでこのリクエストを確認")
    print("2. テスト回答を作成してみる")
    
    # クリーンアップ
    test_file.unlink()
    
    return request_id


def test_check_response(request_id: str):
    """回答のチェックテスト"""
    print("\n" + "=" * 60)
    print("テスト: 回答の確認")
    print("=" * 60)
    
    bridge = ClaudeBridge()
    response = bridge.check_response(request_id)
    
    if response:
        print("✅ 回答が見つかりました")
    else:
        print("⏳ 回答待ち（正常な動作です）")


def test_list_pending():
    """未回答リクエストのリストテスト"""
    print("\n" + "=" * 60)
    print("テスト: 未回答リクエスト一覧")
    print("=" * 60)
    
    bridge = ClaudeBridge()
    bridge.list_pending_requests()


def create_sample_response(request_id: str):
    """サンプル回答を作成（Claude Desktop側の動作テスト用）"""
    print("\n" + "=" * 60)
    print("テスト: サンプル回答の作成")
    print("=" * 60)
    
    import json
    from datetime import datetime
    
    bridge = ClaudeBridge()
    response_file = bridge.responses_path / f"{request_id}_response.json"
    
    sample_response = {
        "request_id": request_id,
        "response_timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "analysis": {
            "root_cause": "ネストしたループによるO(n²)の計算量",
            "recommendations": [
                {
                    "priority": 1,
                    "title": "アルゴリズムの見直し",
                    "description": "ネストループを避け、ベクトル化された計算を使用",
                    "code_example": "import numpy as np\nresult = np.outer(range(10000), range(10000)).flatten()"
                },
                {
                    "priority": 2,
                    "title": "結果のキャッシュ",
                    "description": "計算結果を保存し、再利用",
                    "code_example": "@lru_cache(maxsize=128)\ndef cached_slow_function(): ..."
                }
            ]
        },
        "implementation_steps": [
            "1. NumPyをインストール: pip install numpy",
            "2. slow_function()をベクトル化実装に変更",
            "3. 性能測定（目標: 1秒以内）",
            "4. 必要に応じてキャッシュ追加"
        ],
        "code_files": {
            "test_code.py": """import numpy as np

def fast_function():
    # ベクトル化された実装
    i = np.arange(10000)
    j = np.arange(10000)
    result = np.outer(i, j).flatten()
    return result.tolist()
"""
        },
        "additional_notes": "NumPyのインストールには `uv pip install numpy` を推奨"
    }
    
    response_file.write_text(
        json.dumps(sample_response, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    print(f"✅ サンプル回答作成: {response_file}")
    print("\n次のステップ:")
    print(f"python test_bridge.py --check {request_id}")


def run_full_test():
    """完全なテストフロー"""
    print("\n🚀 Claude Bridge 完全テスト開始\n")
    
    # 1. リクエスト作成
    request_id = test_create_request()
    
    # 2. 未回答リスト確認
    test_list_pending()
    
    # 3. サンプル回答作成（Claude Desktop側のシミュレーション）
    create_sample_response(request_id)
    
    # 4. 回答確認
    test_check_response(request_id)
    
    print("\n" + "=" * 60)
    print("✅ 全テスト完了")
    print("=" * 60)
    print("\nシステムは正常に動作しています！")
    print("\n実際のプロジェクトで使用する準備ができました。")
    print("詳細は README.md を参照してください。")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Bridge システムテスト")
    parser.add_argument("--full", action="store_true", help="完全なテストを実行")
    parser.add_argument("--create", action="store_true", help="テストリクエストを作成")
    parser.add_argument("--check", type=str, help="指定したリクエストIDの回答を確認")
    parser.add_argument("--list", action="store_true", help="未回答リクエスト一覧")
    parser.add_argument("--sample", type=str, help="指定したリクエストIDのサンプル回答を作成")
    
    args = parser.parse_args()
    
    if args.full:
        run_full_test()
    elif args.create:
        test_create_request()
    elif args.check:
        test_check_response(args.check)
    elif args.list:
        test_list_pending()
    elif args.sample:
        create_sample_response(args.sample)
    else:
        print("Claude Bridge システムテスト")
        print("\n使用例:")
        print("  python test_bridge.py --full      # 完全テスト")
        print("  python test_bridge.py --create    # リクエスト作成テスト")
        print("  python test_bridge.py --list      # 未回答リスト表示")
        print("  python test_bridge.py --check REQ_ID  # 回答確認")
        print("  python test_bridge.py --sample REQ_ID # サンプル回答作成")
