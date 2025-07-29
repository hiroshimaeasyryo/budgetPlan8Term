# 8期予算計画策定ツール

## 概要
このプロジェクトは、当社の来期(8期)の予算計画策定にあたり各事業部の利益体質に見合った目標設定を行い、実現可能で現場からの不満感を可能な限り抑制した形で本部費用を配賦するための可視化ツールです。

## 機能
- **認証機能**: ID/PWによるログイン認証
- **ユーザー管理**: 管理者によるユーザー追加・管理
- **各事業部の損益分岐点分析**: 配賦後の限界利益率を考慮した分析
- **本部費用の配賦割合調整**: 固定費・変動費の配賦割合をリアルタイム調整
- **事業部間の固定費・変動費負担調整**: スライダーと数値入力による精密調整
- **リアルタイムでのグラフ可視化**: Plotlyによるインタラクティブなグラフ表示

## セットアップ

### 1. 仮想環境の作成
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定（推奨）
```bash
# env.exampleを.envにコピー
cp env.example .env

# .envファイルを編集して管理者アカウントを設定
# 本番環境では必ず強力なパスワードに変更してください
```

### 4. アプリケーションの実行
```bash
streamlit run app.py
```

## 認証機能

### 初回起動時の設定
初回起動時に管理者アカウントが自動的に作成されます：

**デフォルト管理者アカウント:**
- ユーザー名: `admin`
- パスワード: `admin123`

**環境変数による設定（推奨）:**
```bash
export ADMIN_USERNAME=your_admin_username
export ADMIN_PASSWORD=your_secure_password
export ADMIN_NAME=管理者名
```

**セキュリティ推奨事項:**
- 初回ログイン後、必ずパスワードを変更してください
- 管理者アカウントでログイン後、必要に応じて一般ユーザーを追加してください
- 本番環境では環境変数で管理者アカウントを設定することを強く推奨します

### セキュリティ機能
- パスワードのハッシュ化保存
- ログイン試行回数制限（5回失敗で5分間ロックアウト）
- セッション管理による認証状態の保持

## 技術スタック
- Python 3.8+
- Streamlit
- Plotly
- Pandas
- NumPy
- hashlib（パスワードハッシュ化）

## プロジェクト構造
```
8termBudgetPlan/
├── app.py                 # メインアプリケーション
├── utils/
│   ├── __init__.py
│   ├── data_manager.py    # データ管理
│   ├── chart_generator.py # グラフ生成
│   ├── auth_manager.py    # 認証機能管理
│   └── login_ui.py       # ログインUI
├── users.json            # ユーザー情報（自動生成）
├── env.example          # 環境変数設定例
├── requirements.txt       # 依存関係
├── .gitignore           # Git除外設定
├── README.md           # プロジェクト説明
├── 概要.md             # プロジェクト概要
└── colab_ver.py        # 元のColabコード
``` 