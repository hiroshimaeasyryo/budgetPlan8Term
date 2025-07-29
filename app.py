"""
8期予算計画策定ツール - メインアプリケーション
Streamlitを使用したWebアプリケーション
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data_manager import DataManager
from utils.chart_generator import ChartGenerator

# ページ設定
st.set_page_config(
    page_title="8期予算計画策定ツール",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'chart_generator' not in st.session_state:
    st.session_state.chart_generator = ChartGenerator()

def main():
    """メインアプリケーション"""
    
    # ヘッダー
    st.title("📊 8期予算計画策定ツール")
    st.markdown("各事業部の利益体質に見合った目標設定と本部費用の最適配賦を支援します")
    
    # サイドバー
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 本部費用の配賦設定
        st.subheader("本部費用配賦設定")
        
        # 固定費の配賦割合
        st.markdown("**固定費配賦割合**")
        fixed_ratios = {}
        total_fixed = 0
        
        for dept_name in st.session_state.data_manager.departments.keys():
            current_ratio = st.session_state.data_manager.allocation_ratios[dept_name]["fixed"]
            ratio = st.slider(
                f"{dept_name}事業部",
                min_value=0.0,
                max_value=1.0,
                value=current_ratio,
                step=0.01,
                format="%.2f",
                key=f"fixed_{dept_name}"
            )
            fixed_ratios[dept_name] = ratio
            total_fixed += ratio
        
        # 合計が1.0になるように調整
        if abs(total_fixed - 1.0) > 0.001:
            st.warning(f"固定費配賦割合の合計: {total_fixed:.2f} (1.00にする必要があります)")
        else:
            st.success(f"固定費配賦割合の合計: {total_fixed:.2f}")
        
        # 変動費の配賦割合
        st.markdown("**変動費配賦割合**")
        variable_ratios = {}
        total_variable = 0
        
        for dept_name in st.session_state.data_manager.departments.keys():
            current_ratio = st.session_state.data_manager.allocation_ratios[dept_name]["variable"]
            ratio = st.slider(
                f"{dept_name}事業部",
                min_value=0.0,
                max_value=1.0,
                value=current_ratio,
                step=0.01,
                format="%.2f",
                key=f"variable_{dept_name}"
            )
            variable_ratios[dept_name] = ratio
            total_variable += ratio
        
        # 合計が1.0になるように調整
        if abs(total_variable - 1.0) > 0.001:
            st.warning(f"変動費配賦割合の合計: {total_variable:.2f} (1.00にする必要があります)")
        else:
            st.success(f"変動費配賦割合の合計: {total_variable:.2f}")
        
        # 配賦割合を更新
        if abs(total_fixed - 1.0) < 0.001 and abs(total_variable - 1.0) < 0.001:
            new_ratios = {}
            for dept_name in st.session_state.data_manager.departments.keys():
                new_ratios[dept_name] = {
                    "fixed": fixed_ratios[dept_name],
                    "variable": variable_ratios[dept_name]
                }
            st.session_state.data_manager.update_allocation_ratios(new_ratios)
        
        # リセットボタン
        if st.button("配賦割合をリセット"):
            # 均等配賦にリセット
            reset_ratios = {}
            dept_count = len(st.session_state.data_manager.departments)
            equal_ratio = 1.0 / dept_count
            for dept_name in st.session_state.data_manager.departments.keys():
                reset_ratios[dept_name] = {
                    "fixed": equal_ratio,
                    "variable": equal_ratio
                }
            st.session_state.data_manager.update_allocation_ratios(reset_ratios)
            st.rerun()
    
    # メインコンテンツ
    tab1, tab2, tab3 = st.tabs(["📈 損益分岐点分析", "📊 配賦サマリー", "📋 データ詳細"])
    
    with tab1:
        st.header("損益分岐点分析")
        
        # 配賦後のコストを計算
        allocated_costs = st.session_state.data_manager.calculate_allocated_costs()
        
        # グラフを生成
        fig = st.session_state.chart_generator.create_break_even_chart(allocated_costs)
        
        # グラフを表示
        st.plotly_chart(fig, use_container_width=True)
        
        # 説明
        st.markdown("""
        **グラフの見方:**
        - **青い線**: 営業利益の変化
        - **緑の領域**: 利益が出る範囲
        - **赤の領域**: 損失が出る範囲
        - **赤い破線**: 固定費の水準
        - **緑の丸**: 損益分岐点
        - **グレーの点線**: 損益分岐線（利益=0）
        """)
    
    with tab2:
        st.header("配賦サマリー")
        
        # 配賦後のコストを計算
        allocated_costs = st.session_state.data_manager.calculate_allocated_costs()
        
        # サマリーチャートを生成
        summary_fig = st.session_state.chart_generator.create_allocation_summary_chart(allocated_costs)
        
        # グラフを表示
        st.plotly_chart(summary_fig, use_container_width=True)
        
        # サマリーテーブル
        st.subheader("配賦後データ")
        summary_df = st.session_state.data_manager.get_summary_data()
        st.dataframe(summary_df, use_container_width=True)
    
    with tab3:
        st.header("データ詳細")
        
        # 基本データ
        st.subheader("事業部基本データ")
        dept_data = st.session_state.data_manager.get_department_data()
        hq_fixed, hq_variable = st.session_state.data_manager.get_headquarters_costs()
        
        # 基本データをDataFrameで表示
        basic_data = []
        for dept_name, data in dept_data.items():
            basic_data.append({
                "事業部": dept_name,
                "限界利益率": f"{data['margin_rate']:.1%}",
                "固定費": f"{data['fixed_cost']:,.0f}円",
                "変動費": f"{data['variable_cost']:,.0f}円"
            })
        
        basic_df = pd.DataFrame(basic_data)
        st.dataframe(basic_df, use_container_width=True)
        
        # 本部費用
        st.subheader("本部費用")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("本部固定費", f"{hq_fixed:,.0f}円")
        with col2:
            st.metric("本部変動費", f"{hq_variable:,.0f}円")
        
        # 配賦割合
        st.subheader("現在の配賦割合")
        allocation_df = pd.DataFrame([
            {
                "事業部": dept_name,
                "固定費配賦率": f"{ratios['fixed']:.1%}",
                "変動費配賦率": f"{ratios['variable']:.1%}"
            }
            for dept_name, ratios in st.session_state.data_manager.get_allocation_ratios().items()
        ])
        st.dataframe(allocation_df, use_container_width=True)
    
    # フッター
    st.markdown("---")
    st.markdown("**8期予算計画策定ツール** - 各事業部の利益体質に見合った目標設定を支援")

if __name__ == "__main__":
    main() 