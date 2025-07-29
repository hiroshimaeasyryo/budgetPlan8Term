import plotly.graph_objects as go
import numpy as np

# 各事業部の限界利益率・固定費（本部費用配賦後）
departments = {
    "キャリア": {"margin_rate": 0.6025, "fixed_cost": 43_087_612},
    "インサイド": {"margin_rate": 0.6483, "fixed_cost": 48_443_632},
    "フィールド": {"margin_rate": 0.4512, "fixed_cost": 8_268_146},
    "SP": {"margin_rate": 0.5421, "fixed_cost": 23_683_173},
    "飲食": {"margin_rate": 0.5478, "fixed_cost": 15_424_497},
}

# 全てのトレースとアノテーションのデータを格納するリスト
all_traces = []
all_annotations_data = [] # アノテーションの生データを格納

# 各事業部のデータを準備
for i, (name, p) in enumerate(departments.items()):
    margin_rate, F = p["margin_rate"], p["fixed_cost"]
    bep_sales = F / margin_rate
    x_max = bep_sales * 1.5 # 売上総利益の最大値を設定
    sales = np.linspace(0, x_max, 400) # 売上総利益の範囲を生成

    # 利益を計算 (売上総利益 - 総費用)
    # 総費用 = 固定費 + 変動費
    # 変動費 = 売上総利益 * (1 - 限界利益率)
    # 利益 = 売上総利益 - (固定費 + sales * (1 - margin_rate))
    profit = sales - (F + sales * (1 - margin_rate))


    # 百万円単位に変換
    sales_m = sales / 1_000_000
    profit_m = profit / 1_000_000
    F_m = F / 1_000_000
    bep_sales_m = bep_sales / 1_000_000


    # トレース1: 利益線 (メインの線)
    all_traces.append(
        go.Scatter(
            x=sales_m,
            y=profit_m,
            mode='lines',
            name=f'{name}事業部: 利益',
            line=dict(color='blue', width=2),
            # ホバー情報を元の円単位で表示
            hovertemplate='<b>売上総利益:</b> %{customdata[0]:,.0f}円<br><b>営業利益:　</b> %{customdata[1]:,.0f}円<extra></extra>',
            customdata=np.stack([sales, profit], axis=-1), # 元の円単位のデータをcustomdataに格納
            visible=(i == 0) # 最初の事業部のみ初期表示
        )
    )

    # トレース2: 利益領域 (正の利益部分を緑色で塗りつぶし)
    profit_positive_y = np.where(profit_m >= 0, profit_m, 0)
    all_traces.append(
        go.Scatter(
            x=sales_m,
            y=profit_positive_y,
            mode='lines',
            fill='tozeroy', # Y=0まで塗りつぶす
            fillcolor='rgba(0,255,0,0.15)', # 薄い緑色
            line=dict(width=0), # 線を非表示
            name=f'{name}事業部: 利益領域',
            showlegend=False, # 凡例に表示しない
             # ホバー情報を元の円単位で表示
            hovertemplate='<b>売上総利益:</b> %{customdata[0]:,.0f}円<br><b>営業利益:　</b> %{customdata[1]:,.0f}円<extra></extra>',
            customdata=np.stack([sales, profit_positive_y * 1_000_000], axis=-1), # 元の円単位のデータをcustomdataに格納
            visible=(i == 0)
        )
    )

    # トレース3: 損失領域 (負の利益部分を赤色で塗りつぶし)
    profit_negative_y = np.where(profit_m < 0, profit_m, 0)
    all_traces.append(
        go.Scatter(
            x=sales_m,
            y=profit_negative_y,
            mode='lines',
            fill='tozeroy', # Y=0まで塗りつぶす
            fillcolor='rgba(255,0,0,0.15)', # 薄い赤色
            line=dict(width=0), # 線を非表示
            name=f'{name}事業部: 損失領域',
            showlegend=False, # 凡例に表示しない
             # ホバー情報を元の円単位で表示
            hovertemplate='<b>売上総利益:</b> %{customdata[0]:,.0f}円<br><b>営業損失:　</b> %{customdata[1]:,.0f}円<extra></extra>',
            customdata=np.stack([sales, profit_negative_y * 1_000_000], axis=-1), # 元の円単位のデータをcustomdataに格納
            visible=(i == 0)
        )
    )

    # トレース4: 固定費線 (利益チャート上では-F_mの水平線)
    all_traces.append(
        go.Scatter(
            x=[0, x_max / 1_000_000],
            y=[-F_m, -F_m],
            mode='lines',
            name=f'{name}事業部: 固定費 ({F_m:,.0f}百万円)',
            line=dict(color='red', dash='dash'),
            # ホバー情報を元の円単位で表示
            hovertemplate='<b>固定費:</b> %{customdata[0]:,.0f}円<extra></extra>',
            customdata=np.stack([-F, -F], axis=-1), # 元の円単位のデータをcustomdataに格納
            visible=(i == 0)
        )
    )


    # トレース5: 損益分岐点 (BEP) マーカー
    all_traces.append(
        go.Scatter(
            x=[bep_sales_m],
            y=[0], # BEPでは利益が0
            mode='markers',
            name=f'{name}事業部: 損益分岐点',
            marker=dict(color='green', size=10, symbol='circle'),
             # ホバー情報を元の円単位で表示
            hovertemplate='<b>損益分岐点 売上総利益:</b> %{customdata[0]:,.0f}円<br><b>営業利益:　</b> %{customdata[1]:,.0f}円<extra></extra>',
            customdata=np.stack([bep_sales, 0], axis=-1), # 元の円単位のデータをcustomdataに格納
            visible=(i == 0)
        )
    )

    # アノテーションの生データを格納
    all_annotations_data.append(
        dict(
            x=bep_sales_m,
            y=0,
            xref="x",
            yref="y",
            text=f"損益分岐点<br>{bep_sales:,.0f}円",
            showarrow=True,
            arrowhead=2,
            ax=bep_sales_m * 0.6, # アノテーションのX位置を調整
            ay=profit_m.max() * 0.5, # アノテーションのY位置を調整
            visible=(i == 0) # 初期表示設定
        )
    )

# メインの図を作成
fig = go.Figure(data=all_traces)

# ドロップダウンボタンを作成
all_buttons = []
for i, name in enumerate(departments.keys()):
    visibility = [False] * len(all_traces) # 全てのトレースを初期的に非表示に設定
    # 現在の事業部の5つのトレースを表示に設定
    visibility[i*5] = True      # 利益線
    visibility[i*5 + 1] = True  # 利益塗りつぶし
    visibility[i*5 + 2] = True  # 損失塗りつぶし
    visibility[i*5 + 3] = True  # 固定費線
    visibility[i*5 + 4] = True  # BEPマーカー

    # このボタンの状態に対応するアノテーションの新しいリストを作成
    # 現在の事業部のアノテーションのみ表示
    button_annotations = []
    for j, ann_data in enumerate(all_annotations_data):
        new_ann = ann_data.copy() # コピーを作成して変更
        new_ann['visible'] = (j == i) # 現在の事業部のアノテーションのみ表示
        button_annotations.append(new_ann)


    all_buttons.append(
        dict(
            label=name,
            method="update",
            args=[
                {"visible": visibility}, # トレースの表示/非表示
                {"annotations": button_annotations} # アノテーションの表示/非表示
            ]
        )
    )

# レイアウトを更新し、ドロップダウンメニューを追加
fig.update_layout(
    updatemenus=[
        go.layout.Updatemenu(
            active=0, # 初期選択は最初の事業部
            buttons=list(all_buttons),
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.01,
            xanchor="left",
            y=1.15,
            yanchor="top"
        ),
    ],
    title_text="事業部別：損益分岐点分析（営業利益 vs 売上総利益）",
    xaxis_title="売上総利益 (百万円)", # X軸ラベルを百万円単位に変更
    yaxis_title="営業利益　 (百万円)", # Y軸ラベルを百万円単位に変更
    hovermode="x unified", # ホバー時にX軸上の全てのトレース情報を表示
    template="plotly_white", # 白い背景のテンプレートを使用
    annotations=all_annotations_data, # 全てのアノテーションを初期レイアウトに追加
    height=600, # 図の高さ
    margin=dict(t=120) # ドロップダウンメニューのために上マージンを調整
)


# 損益分岐線 (Y=0の水平線) を追加 (常に表示)
# 全ての事業部で最大のX値を見つけて線の長さを決定
max_x_val = 0
for name, p in departments.items():
    bep_sales = p["fixed_cost"] / p["margin_rate"]
    max_x_val = max(max_x_val, bep_sales * 1.5 / 1_000_000)


fig.add_shape(
    type="line",
    x0=0,
    y0=0,
    x1=max_x_val,
    y1=0,
    line=dict(color="grey", width=2, dash="dot"),
    layer="below" # 他の要素の下に表示
)

# Y軸の初期範囲を調整して、負の利益（固定費）も表示できるようにする
min_profit = float('inf')
max_profit = float('-inf')
for name, p in departments.items():
    F = p["fixed_cost"]
    margin_rate = p["margin_rate"]
    bep_sales = F / margin_rate
    x_max = bep_sales * 1.5
    sales = np.linspace(0, x_max, 400)
    profit = sales - (F + sales * (1 - margin_rate))
    min_profit = min(min_profit, profit.min())
    max_profit = max(max_profit, profit.max())


fig.update_yaxes(range=[min_profit / 1_000_000 * 1.1, max_profit / 1_000_000 * 1.1])
fig.update_xaxes(range=[0, max_x_val * 1.1]) # X軸の範囲も少し調整


# 図を表示
fig.show()