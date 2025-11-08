#!/bin/bash
#
# Claude Code ⇄ Claude Desktop Bridge
# インストールスクリプト
#
# このスクリプトは以下を実行します:
# 1. ディレクトリ構造の作成
# 2. 依存関係のインストール
# 3. 初期設定ファイルの作成
# 4. パーミッションの設定
# 5. セットアップ検証
#

set -e  # エラーで終了

# 色付き出力
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo "=========================================="
    echo "  $1"
    echo "=========================================="
    echo ""
}

# インストールディレクトリ
INSTALL_DIR="$HOME/AI-Workspace/claude-bridge"

print_header "Claude Bridge インストーラー"

log_info "インストールディレクトリ: $INSTALL_DIR"
echo ""

# ステップ1: ディレクトリ構造の作成
print_header "ステップ1: ディレクトリ構造の作成"

if [ -d "$INSTALL_DIR" ]; then
    log_warning "既存のインストールが見つかりました"
    read -p "既存のインストールを上書きしますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "インストールをキャンセルしました"
        exit 0
    fi
fi

log_info "ディレクトリを作成中..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/help-requests"
mkdir -p "$INSTALL_DIR/help-responses"
mkdir -p "$INSTALL_DIR/archive"
mkdir -p "$INSTALL_DIR/backups"
mkdir -p "$INSTALL_DIR/checkpoints"
mkdir -p "$INSTALL_DIR/logs"

log_success "ディレクトリ構造を作成しました"

# ステップ2: Pythonバージョンチェック
print_header "ステップ2: Python環境の確認"

if ! command -v python3 &> /dev/null; then
    log_error "Python 3が見つかりません"
    log_info "Python 3.7以上をインストールしてください"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_success "Python $PYTHON_VERSION を検出しました"

# ステップ3: 依存関係のインストール
print_header "ステップ3: 依存関係のインストール"

if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    log_info "依存関係をインストール中..."

    # pipのアップグレード
    python3 -m pip install --upgrade pip --quiet

    # 依存関係のインストール
    if python3 -m pip install -r "$INSTALL_DIR/requirements.txt" --quiet; then
        log_success "依存関係をインストールしました"
    else
        log_warning "依存関係のインストールに失敗しました（オプション機能が制限される可能性があります）"
    fi
else
    log_info "requirements.txtが見つかりません（スキップ）"
fi

# ステップ4: 初期設定ファイルの作成
print_header "ステップ4: 初期設定ファイルの作成"

CONFIG_FILE="$INSTALL_DIR/automation_config.json"

if [ -f "$CONFIG_FILE" ]; then
    log_info "既存の設定ファイルが見つかりました"
    read -p "設定ファイルを上書きしますか？ (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "configure.pyを実行してください: python3 $INSTALL_DIR/configure.py"
    else
        log_info "既存の設定を保持します"
    fi
else
    log_info "デフォルト設定ファイルを作成中..."
    read -p "対話的に設定を作成しますか？ (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # 対話的設定
        cd "$INSTALL_DIR"
        python3 configure.py
    else
        # クイックセットアップ
        cd "$INSTALL_DIR"
        python3 configure.py --quick
    fi
    log_success "設定ファイルを作成しました"
fi

# ステップ5: パーミッションの設定
print_header "ステップ5: パーミッションの設定"

log_info "実行権限を設定中..."
chmod +x "$INSTALL_DIR/install.sh" 2>/dev/null || true
chmod +x "$INSTALL_DIR/configure.py" 2>/dev/null || true

log_success "パーミッションを設定しました"

# ステップ6: セットアップ検証
print_header "ステップ6: セットアップ検証"

log_info "インストールを検証中..."

# 必須ファイルの確認
REQUIRED_FILES=(
    "bridge_helper.py"
    "automation_helper.py"
    "configure.py"
    "README.md"
)

ALL_FILES_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$INSTALL_DIR/$file" ]; then
        log_success "✓ $file"
    else
        log_error "✗ $file が見つかりません"
        ALL_FILES_EXIST=false
    fi
done

# ディレクトリの確認
REQUIRED_DIRS=(
    "help-requests"
    "help-responses"
    "archive"
    "backups"
    "checkpoints"
    "logs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$INSTALL_DIR/$dir" ]; then
        log_success "✓ $dir/"
    else
        log_error "✗ $dir/ が見つかりません"
        ALL_FILES_EXIST=false
    fi
done

echo ""

if [ "$ALL_FILES_EXIST" = true ]; then
    log_success "全ての必須ファイルが存在します"
else
    log_error "一部のファイルが不足しています"
    exit 1
fi

# ステップ7: Pythonモジュールのインポートテスト
log_info "Pythonモジュールをテスト中..."

cd "$INSTALL_DIR"
if python3 -c "from bridge_helper import ClaudeBridge; from automation_helper import AutomatedBridge" 2>/dev/null; then
    log_success "Pythonモジュールのインポートに成功しました"
else
    log_error "Pythonモジュールのインポートに失敗しました"
    exit 1
fi

# インストール完了
print_header "インストール完了！"

echo ""
log_success "Claude Bridge のインストールが完了しました"
echo ""
echo "📝 次のステップ:"
echo ""
echo "1. 使い方を確認:"
echo "   cat $INSTALL_DIR/README.md"
echo ""
echo "2. 設定を確認・編集:"
echo "   python3 $INSTALL_DIR/configure.py --show"
echo "   python3 $INSTALL_DIR/configure.py"
echo ""
echo "3. 手動モードで使用:"
echo "   python3 << 'EOF'"
echo "   import sys"
echo "   from pathlib import Path"
echo "   sys.path.append('$INSTALL_DIR')"
echo "   from bridge_helper import ask_claude_desktop"
echo "   EOF"
echo ""
echo "4. 自動モードで使用:"
echo "   python3 << 'EOF'"
echo "   import sys"
echo "   from pathlib import Path"
echo "   sys.path.append('$INSTALL_DIR')"
echo "   from automation_helper import AutomatedBridge"
echo "   bridge = AutomatedBridge()"
echo "   EOF"
echo ""
echo "5. ステータスダッシュボードで確認:"
echo "   python3 $INSTALL_DIR/dashboard.py"
echo ""
echo "6. テスト実行:"
echo "   cd $INSTALL_DIR && python3 test_automation.py"
echo ""
echo "🎉 Happy Coding with Claude Bridge!"
echo ""
