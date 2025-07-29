"""
グラフ生成モジュール
Plotlyを使用して損益分岐点分析のグラフを生成
"""

import plotly.graph_objects as go
import numpy as np
from typing import Dict, List

class ChartGenerator:
    """損益分岐点分析のグラフを生成するクラス"""
    
    def __init__(self):
        self.colors = {
            "キャリア": "#1f77b4",
            "インサイド": "#ff7f0e", 
            "フィールド": "#2ca02c",
            "SP": "#d62728",
            "飲食": "#9467bd"
        }
    
    def create_break_even_chart(self, allocated_costs: Dict, selected_department: str = None) -> go.Figure:
        """損益分岐点分析のグラフを作成"""
        
        # 全てのトレースとアノテーションのデータを格納
        all_traces = []
        all_annotations_data = []
        
        # 各事業部のデータを準備
        for i, (dept_name, costs) in enumerate(allocated_costs.items()):
            margin_rate = costs["margin_rate"]
            fixed_cost = costs["fixed_cost"]
            
            # 損益分岐点を計算
            bep_sales = fixed_cost / margin_rate
            x_max = bep_sales * 1.5  # 売上総利益の最大値を設定
            sales = np.linspace(0, x_max, 400)  # 売上総利益の範囲を生成
            
            # 利益を計算 (売上総利益 - 総費用)
            # 総費用 = 固定費 + 変動費
            # 変動費 = 売上総利益 * (1 - 限界利益率)
            # 利益 = 売上総利益 - (固定費 + sales * (1 - margin_rate))
            profit = sales - (fixed_cost + sales * (1 - margin_rate))
            
            # 百万円単位に変換
            sales_m = sales / 1_000_000
            profit_m = profit / 1_000_000
            fixed_cost_m = fixed_cost / 1_000_000
            bep_sales_m = bep_sales / 1_000_000
            
            # 初期表示設定（選択された事業部または最初の事業部）
            is_visible = (selected_department is None and i == 0) or (selected_department == dept_name)
            
            # トレース1: 利益線 (メインの線)
            all_traces.append(
                go.Scatter(
                    x=sales_m,
                    y=profit_m,
                    mode='lines',
                    name=f'{dept_name}事業部: 利益',
                    line=dict(color=self.colors.get(dept_name, "#1f77b4"), width=2),
                    hovertemplate='<b>売上総利益:</b> %{customdata[0]:,.0f}円<br><b>営業利益:　</b> %{customdata[1]:,.0f}円<extra></extra>',
                    customdata=np.stack([sales, profit], axis=-1),
                    visible=is_visible
                )
            )
            
            # トレース2: 利益領域 (正の利益部分を緑色で塗りつぶし)
            profit_positive_y = np.where(profit_m >= 0, profit_m, 0)
            all_traces.append(
                go.Scatter(
                    x=sales_m,
                    y=profit_positive_y,
                    mode='lines',
                    fill='tozeroy',
                    fillcolor='rgba(0,255,0,0.15)',
                    line=dict(width=0),
                    name=f'{dept_name}事業部: 利益領域',
                    showlegend=False,
                    hovertemplate='<b>売上総利益:</b> %{customdata[0]:,.0f}円<br><b>営業利益:　</b> %{customdata[1]:,.0f}円<extra></extra>',
                    customdata=np.stack([sales, profit_positive_y * 1_000_000], axis=-1),
                    visible=is_visible
                )
            )
            
            # トレース3: 損失領域 (負の利益部分を赤色で塗りつぶし)
            profit_negative_y = np.where(profit_m < 0, profit_m, 0)
            all_traces.append(
                go.Scatter(
                    x=sales_m,
                    y=profit_negative_y,
                    mode='lines',
                    fill='tozeroy',
                    fillcolor='rgba(255,0,0,0.15)',
                    line=dict(width=0),
                    name=f'{dept_name}事業部: 損失領域',
                    showlegend=False,
                    hovertemplate='<b>売上総利益:</b> %{customdata[0]:,.0f}円<br><b>営業損失:　</b> %{customdata[1]:,.0f}円<extra></extra>',
                    customdata=np.stack([sales, profit_negative_y * 1_000_000], axis=-1),
                    visible=is_visible
                )
            )
            
            # トレース4: 固定費線 (利益チャート上では-fixed_cost_mの水平線)
            all_traces.append(
                go.Scatter(
                    x=[0, x_max / 1_000_000],
                    y=[-fixed_cost_m, -fixed_cost_m],
                    mode='lines',
                    name=f'{dept_name}事業部: 固定費 ({fixed_cost_m:,.0f}百万円)',
                    line=dict(color='red', dash='dash'),
                    hovertemplate='<b>固定費:</b> %{customdata[0]:,.0f}円<extra></extra>',
                    customdata=np.stack([-fixed_cost, -fixed_cost], axis=-1),
                    visible=is_visible
                )
            )
            
            # トレース5: 損益分岐点 (BEP) マーカー
            all_traces.append(
                go.Scatter(
                    x=[bep_sales_m],
                    y=[0],
                    mode='markers',
                    name=f'{dept_name}事業部: 損益分岐点',
                    marker=dict(color='green', size=10, symbol='circle'),
                    hovertemplate='<b>損益分岐点 売上総利益:</b> %{customdata[0]:,.0f}円<br><b>営業利益:　</b> %{customdata[1]:,.0f}円<extra></extra>',
                    customdata=np.stack([bep_sales, 0], axis=-1),
                    visible=is_visible
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
                    ax=bep_sales_m * 0.6,
                    ay=profit_m.max() * 0.5,
                    visible=is_visible
                )
            )
        
        # メインの図を作成
        fig = go.Figure(data=all_traces)
        
        # ドロップダウンボタンを作成
        all_buttons = []
        for i, dept_name in enumerate(allocated_costs.keys()):
            visibility = [False] * len(all_traces)
            # 現在の事業部の5つのトレースを表示に設定
            visibility[i*5] = True      # 利益線
            visibility[i*5 + 1] = True  # 利益塗りつぶし
            visibility[i*5 + 2] = True  # 損失塗りつぶし
            visibility[i*5 + 3] = True  # 固定費線
            visibility[i*5 + 4] = True  # BEPマーカー
            
            # このボタンの状態に対応するアノテーションの新しいリストを作成
            button_annotations = []
            for j, ann_data in enumerate(all_annotations_data):
                new_ann = ann_data.copy()
                new_ann['visible'] = (j == i)
                button_annotations.append(new_ann)
            
            all_buttons.append(
                dict(
                    label=dept_name,
                    method="update",
                    args=[
                        {"visible": visibility},
                        {"annotations": button_annotations}
                    ]
                )
            )
        
        # レイアウトを更新
        fig.update_layout(
            updatemenus=[
                go.layout.Updatemenu(
                    active=0,
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
            xaxis_title="売上総利益 (百万円)",
            yaxis_title="営業利益　 (百万円)",
            hovermode="x unified",
            template="plotly_white",
            annotations=all_annotations_data,
            height=600,
            margin=dict(t=120)
        )
        
        # 損益分岐線 (Y=0の水平線) を追加
        max_x_val = 0
        for dept_name, costs in allocated_costs.items():
            bep_sales = costs["fixed_cost"] / costs["margin_rate"]
            max_x_val = max(max_x_val, bep_sales * 1.5 / 1_000_000)
        
        fig.add_shape(
            type="line",
            x0=0,
            y0=0,
            x1=max_x_val,
            y1=0,
            line=dict(color="grey", width=2, dash="dot"),
            layer="below"
        )
        
        # Y軸の初期範囲を調整
        min_profit = float('inf')
        max_profit = float('-inf')
        for dept_name, costs in allocated_costs.items():
            fixed_cost = costs["fixed_cost"]
            margin_rate = costs["margin_rate"]
            bep_sales = fixed_cost / margin_rate
            x_max = bep_sales * 1.5
            sales = np.linspace(0, x_max, 400)
            profit = sales - (fixed_cost + sales * (1 - margin_rate))
            min_profit = min(min_profit, profit.min())
            max_profit = max(max_profit, profit.max())
        
        fig.update_yaxes(range=[min_profit / 1_000_000 * 1.1, max_profit / 1_000_000 * 1.1])
        fig.update_xaxes(range=[0, max_x_val * 1.1])
        
        return fig
    
    def create_allocation_summary_chart(self, allocated_costs: Dict) -> go.Figure:
        """本部費用配賦のサマリーチャートを作成"""
        
        departments = list(allocated_costs.keys())
        fixed_costs = [costs["fixed_cost"] / 1_000_000 for costs in allocated_costs.values()]
        variable_costs = [costs["variable_cost"] / 1_000_000 for costs in allocated_costs.values()]
        
        fig = go.Figure()
        
        # 固定費のバー
        fig.add_trace(go.Bar(
            name='固定費',
            x=departments,
            y=fixed_costs,
            marker_color='#1f77b4',
            hovertemplate='<b>%{x}</b><br>固定費: %{y:,.1f}百万円<extra></extra>'
        ))
        
        # 変動費のバー
        fig.add_trace(go.Bar(
            name='変動費',
            x=departments,
            y=variable_costs,
            marker_color='#ff7f0e',
            hovertemplate='<b>%{x}</b><br>変動費: %{y:,.1f}百万円<extra></extra>'
        ))
        
        fig.update_layout(
            title_text="事業部別：配賦後コスト構成",
            xaxis_title="事業部",
            yaxis_title="コスト (百万円)",
            barmode='stack',
            template="plotly_white",
            height=400
        )
        
        return fig 