# 8期予算計画策定ツール

## 概要
このプロジェクトは、当社の来期(8期)の予算計画策定にあたり各事業部の利益体質に見合った目標設定を行い、実現可能で現場からの不満感を可能な限り抑制した形で本部費用を配賦するための可視化ツールです。

## 機能
- 各事業部の損益分岐点分析
- 本部費用の配賦割合調整
- 事業部間の固定費・変動費負担調整
- リアルタイムでのグラフ可視化

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

### 3. アプリケーションの実行
```bash
streamlit run app.py
```

## 技術スタック
- Python 3.8+
- Streamlit
- Plotly
- Pandas
- NumPy

## プロジェクト構造
```
8termBudgetPlan/
├── app.py                 # メインアプリケーション
├── utils/
│   ├── __init__.py
│   ├── data_manager.py    # データ管理
│   └── chart_generator.py # グラフ生成
├── requirements.txt       # 依存関係
├── .gitignore           # Git除外設定
├── README.md           # プロジェクト説明
├── 概要.md             # プロジェクト概要
└── colab_ver.py        # 元のColabコード
``` 