"""
Claude Code ⇄ Claude Desktop ブリッジヘルパー

このモジュールは、Claude Codeが困難に直面した時に
Claude Desktopにヘルプを求めるための機能を提供します。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class ClaudeBridge:
    """Claude Code ⇄ Claude Desktop 連携を管理"""
    
    def __init__(self):
        self.base_path = Path.home() / "AI-Workspace/claude-bridge"
        self.requests_path = self.base_path / "help-requests"
        self.responses_path = self.base_path / "help-responses"
        self.archive_path = self.base_path / "archive"
        
        # フォルダが存在することを確認
        for path in [self.requests_path, self.responses_path, self.archive_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def create_help_request(
        self,
        title: str,
        problem: str,
        tried: list[str],
        files_to_analyze: list[str],
        error_messages: str = "",
        context: str = ""
    ) -> str:
        """
        ヘルプリクエストを作成
        
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        request_id = f"req_{timestamp}"
        
        # プロジェクトルートを取得
        project_root = str(Path.cwd())
        
        # リクエストデータ
        request = {
            "request_id": request_id,
            "timestamp": timestamp,
            "title": title,
            "problem": problem,
            "tried": tried,
            "files_to_analyze": files_to_analyze,
            "error_messages": error_messages,
            "context": context,
            "project_root": project_root,
            "status": "pending"
        }
        
        # リクエストファイル作成
        request_file = self.requests_path / f"{request_id}.json"
        request_file.write_text(
            json.dumps(request, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # 分析用ファイルをコピー
        analysis_dir = self.requests_path / request_id
        analysis_dir.mkdir(exist_ok=True)
        
        copied_files = []
        for file_path in files_to_analyze:
            full_path = Path(project_root) / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding="utf-8")
                    dest = analysis_dir / full_path.name
                    dest.write_text(content, encoding="utf-8")
                    copied_files.append(str(dest))
                except Exception as e:
                    print(f"⚠️  {file_path} のコピーに失敗: {e}")
        
        # 結果を表示
        print(f"""
{'='*60}
🚨 ヘルプリクエスト作成完了
{'='*60}

リクエストID: {request_id}
タイトル: {title}

📁 作成されたファイル:
   - リクエスト: {request_file}
   - 分析用ファイル: {len(copied_files)}個

📋 次のステップ:

1️⃣  Claude Desktopを開く

2️⃣  以下のメッセージをコピー&ペーストして送信:

---
ヘルプリクエストの分析をお願いします。
以下のファイルを確認してください:

{request_file}

分析後、回答を以下の場所に保存してください:
{self.responses_path}/{request_id}_response.json
---

3️⃣  Claude Desktopからの回答を待つ

💡 回答確認コマンド:
   python -c "from bridge_helper import ClaudeBridge; ClaudeBridge().check_response('{request_id}')"

{'='*60}
        """)
        
        return request_id
    
    def check_response(self, request_id: str) -> Optional[dict]:
        """
        特定のリクエストへの回答をチェック
        
        Args:
            request_id: チェックするリクエストID
        
        Returns:
            回答データ（あれば）、なければNone
        """
        response_file = self.responses_path / f"{request_id}_response.json"
        
        if not response_file.exists():
            print(f"⏳ {request_id} への回答はまだありません")
            print(f"   Claude Desktopでの分析を待っています...")
            return None
        
        try:
            response = json.loads(response_file.read_text(encoding="utf-8"))
            print(f"""
{'='*60}
✅ 回答を受信しました！
{'='*60}

リクエストID: {request_id}
回答時刻: {response.get('response_timestamp', 'N/A')}

📊 分析結果:
{response.get('analysis', {}).get('root_cause', 'N/A')}

💡 推奨事項:
            """)
            
            for i, rec in enumerate(response.get('analysis', {}).get('recommendations', []), 1):
                print(f"\n{i}. {rec.get('title', 'N/A')}")
                print(f"   優先度: {rec.get('priority', 'N/A')}")
                print(f"   {rec.get('description', 'N/A')}")
            
            print(f"\n{'='*60}")
            print("\n詳細は以下のファイルを確認してください:")
            print(f"{response_file}")
            print(f"{'='*60}\n")
            
            return response
            
        except Exception as e:
            print(f"❌ 回答の読み込みに失敗: {e}")
            return None
    
    def list_pending_requests(self):
        """未回答のリクエスト一覧を表示"""
        pending = []
        
        for req_file in self.requests_path.glob("req_*.json"):
            response_file = self.responses_path / f"{req_file.stem}_response.json"
            if not response_file.exists():
                try:
                    request = json.loads(req_file.read_text(encoding="utf-8"))
                    pending.append(request)
                except:
                    continue
        
        if not pending:
            print("✅ 未回答のリクエストはありません")
            return
        
        print(f"\n{'='*60}")
        print(f"📬 未回答のヘルプリクエスト: {len(pending)}件")
        print(f"{'='*60}\n")
        
        for req in pending:
            print(f"ID: {req['request_id']}")
            print(f"タイトル: {req['title']}")
            print(f"時刻: {req['timestamp']}")
            print("-" * 40)
    
    def archive_completed(self, request_id: str):
        """完了したリクエストと回答をアーカイブ"""
        request_file = self.requests_path / f"{request_id}.json"
        response_file = self.responses_path / f"{request_id}_response.json"
        request_dir = self.requests_path / request_id
        
        if request_file.exists() and response_file.exists():
            # アーカイブフォルダ作成
            archive_dir = self.archive_path / request_id
            archive_dir.mkdir(exist_ok=True)
            
            # 移動
            request_file.rename(archive_dir / request_file.name)
            response_file.rename(archive_dir / response_file.name)
            
            if request_dir.exists():
                import shutil
                shutil.move(str(request_dir), str(archive_dir))
            
            print(f"✅ {request_id} をアーカイブしました")
        else:
            print(f"⚠️  {request_id} のリクエストまたは回答が見つかりません")


# 便利な関数（短縮版）
def ask_claude_desktop(
    title: str,
    problem: str,
    tried: list[str],
    files: list[str],
    error: str = ""
) -> str:
    """
    Claude Desktopにヘルプを求める（短縮版）
    
    使用例:
        ask_claude_desktop(
            title="Neo4jクエリが遅い",
            problem="5000ノードで10秒以上かかる",
            tried=["インデックス追加", "クエリ分割"],
            files=["src/queries.py", "src/models.py"],
            error="Query execution time: 12.3s"
        )
    """
    bridge = ClaudeBridge()
    return bridge.create_help_request(
        title=title,
        problem=problem,
        tried=tried,
        files_to_analyze=files,
        error_messages=error
    )


if __name__ == "__main__":
    # テスト用
    print("Claude Bridge Helper")
    print("="*60)
    print("\nヘルプリクエストを作成するには:")
    print("  ask_claude_desktop(...)")
    print("\n回答をチェックするには:")
    print("  ClaudeBridge().check_response('req_...')")
    print("\n未回答リクエスト一覧:")
    ClaudeBridge().list_pending_requests()
