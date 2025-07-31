"""
8期予算計画策定ツール - メインアプリケーション
Streamlitを使用したWebアプリケーション
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import traceback
from typing import Dict

# エラーハンドリングを追加
try:
    from utils.data_manager import DataManager
    from utils.chart_generator import ChartGenerator
    from utils.auth_manager import AuthManager
    from utils.login_ui import show_login_page, show_user_management_page, show_user_profile, show_user_info_in_sidebar
    from utils.streamlit_compat import get_query_param, set_query_param, rerun_app
except ImportError as e:
    st.error(f"モジュールのインポートエラー: {e}")
    st.error(f"Python version: {sys.version}")
    st.stop()

# ページ設定
st.set_page_config(
    page_title="8期予算計画策定ツール",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 認証マネージャーの初期化
auth_manager = AuthManager()

# セッション状態の初期化
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'chart_generator' not in st.session_state:
    st.session_state.chart_generator = ChartGenerator()

# スライダーの値を管理するセッション状態
if 'fixed_ratios' not in st.session_state:
    st.session_state.fixed_ratios = {}
    for dept_name in st.session_state.data_manager.departments.keys():
        st.session_state.fixed_ratios[dept_name] = st.session_state.data_manager.allocation_ratios[dept_name]["fixed"]

if 'variable_ratios' not in st.session_state:
    st.session_state.variable_ratios = {}
    for dept_name in st.session_state.data_manager.departments.keys():
        st.session_state.variable_ratios[dept_name] = st.session_state.data_manager.allocation_ratios[dept_name]["variable"]

def main():
    """メインアプリケーション"""
    
    try:
        # URLパラメータからページを取得
        page = get_query_param("page", None)
        
        # ログアウト処理
        if page == "logout":
            auth_manager.logout()
            st.success("ログアウトしました。")
            st.rerun()
        
        # 認証チェック
        if not auth_manager.is_authenticated():
            if page == "profile":
                st.error("ログインが必要です。")
                return
            
            # ログイン画面を表示
            result = show_login_page()
            if result is None:  # キャンセル
                return
            elif not result:  # ログイン失敗
                return
            else:  # ログイン成功
                st.rerun()
        
        # 認証済みの場合の処理
        current_user = auth_manager.get_current_user()
        
        # プロフィールページ
        if page == "profile":
            show_user_profile()
            return
        
        # ユーザー管理ページ（管理者のみ）
        if page == "user_management":
            show_user_management_page()
            return
        
        # ヘッダーにユーザー情報を表示
        show_user_info_in_sidebar()
        
        # メインコンテンツ
        st.title("📊 8期予算計画策定ツール")
        st.markdown("各事業部の利益体質に見合った目標設定と本部費用の最適配賦を支援します")
        
        # サイドバー
        with st.sidebar:
            st.header("⚙️ 設定")
            
            # 管理者メニュー
            if current_user and current_user['role'] == 'admin':
                st.subheader("🔧 管理者メニュー")
                if st.button("👥 ユーザー管理"):
                    set_query_param("page", "user_management")
                    rerun_app()
            
            # ユーザーメニュー
            st.subheader("👤 ユーザーメニュー")
            if st.button("👤 プロフィール"):
                set_query_param("page", "profile")
                rerun_app()
            if st.button("🚪 ログアウト"):
                auth_manager.logout()
                st.success("ログアウトしました。")
                rerun_app()
            
            st.markdown("---")
            
            # 本部費用の配賦設定
            st.subheader("本部費用配賦設定")
            
            # 操作説明
            with st.expander("ℹ️ 操作方法", expanded=False):
                st.markdown("""
                **操作方法:**
                - **スライダー**: ドラッグで概略調整
                - **数値入力**: カーソルで上下、または直接入力で精密調整
                - **合計確認**: 固定費・変動費それぞれの合計が1.00になるよう調整してください
                - **リセット**: 均等配賦に戻す場合は「配賦割合をリセット」ボタンを使用
                """)
            
            # 固定費の配賦割合
            st.markdown("**固定費配賦割合**")
            
            # 事業部名のリストを取得（順序を保持）
            dept_names = list(st.session_state.data_manager.departments.keys())
            
            # 各事業部のスライダーと数値入力を表示
            for i, dept_name in enumerate(dept_names):
                # セッション状態から現在の値を取得
                current_ratio = st.session_state.fixed_ratios[dept_name]
                
                # 4列レイアウトでラベル、スライダー、数値入力、現在値を並べる
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    # ラベルを表示
                    st.markdown(f"**{dept_name}事業部**")
                
                with col2:
                    # スライダーを表示
                    ratio = st.slider(
                        f"スライダー",
                        min_value=0.0,
                        max_value=1.0,
                        value=current_ratio,
                        step=0.01,
                        format="%.2f",
                        key=f"fixed_slider_{dept_name}",
                        label_visibility="collapsed"
                    )
                
                with col3:
                    # 数値入力を表示（カーソルで上下可能）
                    number_input = st.number_input(
                        f"値",
                        min_value=0.0,
                        max_value=1.0,
                        value=current_ratio,
                        step=0.01,
                        format="%.2f",
                        key=f"fixed_number_{dept_name}",
                        help=f"カーソルで上下、または直接入力（{current_ratio:.1%}）"
                    )
                
                with col4:
                    # 現在値を表示
                    st.markdown(f"**{current_ratio:.1%}**")
                
                # どちらかが変更された場合、セッション状態を更新
                if abs(ratio - current_ratio) > 0.001:
                    st.session_state.fixed_ratios[dept_name] = ratio
                elif abs(number_input - current_ratio) > 0.001:
                    st.session_state.fixed_ratios[dept_name] = number_input
            
            # 合計を表示
            total_fixed = sum(st.session_state.fixed_ratios.values())
            if abs(total_fixed - 1.0) < 0.001:
                st.success(f"固定費配賦割合の合計: {total_fixed:.2f}")
            else:
                st.warning(f"固定費配賦割合の合計: {total_fixed:.2f} (1.00にする必要があります)")
            
            # 固定費配賦割合として使用
            fixed_ratios = st.session_state.fixed_ratios
            
            # 変動費の配賦割合
            st.markdown("**変動費配賦割合**")
            
            # 各事業部のスライダーと数値入力を表示
            for i, dept_name in enumerate(dept_names):
                # セッション状態から現在の値を取得
                current_ratio = st.session_state.variable_ratios[dept_name]
                
                # 4列レイアウトでラベル、スライダー、数値入力、現在値を並べる
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    # ラベルを表示
                    st.markdown(f"**{dept_name}事業部**")
                
                with col2:
                    # スライダーを表示
                    ratio = st.slider(
                        f"スライダー",
                        min_value=0.0,
                        max_value=1.0,
                        value=current_ratio,
                        step=0.01,
                        format="%.2f",
                        key=f"variable_slider_{dept_name}",
                        label_visibility="collapsed"
                    )
                
                with col3:
                    # 数値入力を表示（カーソルで上下可能）
                    number_input = st.number_input(
                        f"値",
                        min_value=0.0,
                        max_value=1.0,
                        value=current_ratio,
                        step=0.01,
                        format="%.2f",
                        key=f"variable_number_{dept_name}",
                        help=f"カーソルで上下、または直接入力（{current_ratio:.1%}）"
                    )
                
                with col4:
                    # 現在値を表示
                    st.markdown(f"**{current_ratio:.1%}**")
                
                # どちらかが変更された場合、セッション状態を更新
                if abs(ratio - current_ratio) > 0.001:
                    st.session_state.variable_ratios[dept_name] = ratio
                elif abs(number_input - current_ratio) > 0.001:
                    st.session_state.variable_ratios[dept_name] = number_input
            
            # 合計を表示
            total_variable = sum(st.session_state.variable_ratios.values())
            if abs(total_variable - 1.0) < 0.001:
                st.success(f"変動費配賦割合の合計: {total_variable:.2f}")
            else:
                st.warning(f"変動費配賦割合の合計: {total_variable:.2f} (1.00にする必要があります)")
            
            # 変動費配賦割合として使用
            variable_ratios = st.session_state.variable_ratios
            
            # 配賦割合を更新
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
                
                # セッション状態もリセット
                for dept_name in st.session_state.data_manager.departments.keys():
                    st.session_state.fixed_ratios[dept_name] = equal_ratio
                    st.session_state.variable_ratios[dept_name] = equal_ratio
                
                st.rerun()
        
        # メインコンテンツ
        tab1, tab2, tab3, tab4 = st.tabs(["📈 損益分岐点分析", "📊 配賦サマリー", "📋 データ詳細", "📚 損益分岐点分析の説明"])
        
        with tab1:
            st.header("損益分岐点分析")
            
            # 配賦の影響についての説明
            with st.expander("ℹ️ 配賦の影響について", expanded=False):
                st.markdown("""
                **限界利益率の計算方法（売上総利益調整版）:**
                - **配賦前:** 事業部固有の限界利益率を使用
                - **配賦後:** 売上総利益と変動費の両方を調整して再計算
                
                **計算式:**
                - 元の仮の売上総利益 = 事業部変動費 ÷ (1 - 元の限界利益率)
                - 配賦後売上総利益 = 元の仮の売上総利益 + 本部変動費配賦額
                - 配賦後限界利益率 = (配賦後売上総利益 - 総変動費) ÷ 配賦後売上総利益
                
                **変動費配賦の影響:**
                - 本部変動費を配賦すると、売上総利益と変動費の両方が増加します
                - 売上総利益の増加により、限界利益率の低下が緩和されます
                - より現実的な損益分岐点分析が可能になります
                """)
            
            # 配賦後のコストを計算
            allocated_costs = st.session_state.data_manager.calculate_allocated_costs()
            
            # # 仮の売上総利益を表示
            # st.subheader("仮の売上総利益（配賦計算基準）")
            # col1, col2, col3 = st.columns(3)
            # for i, (dept_name, costs) in enumerate(allocated_costs.items()):
            #     with col1 if i < 2 else col2 if i < 4 else col3:
            #         st.metric(
            #             f"{dept_name}事業部",
            #             f"{costs['implied_sales']:,.0f}円",
            #             f"配賦後限界利益率: {costs['margin_rate']:.1%}"
            #         )
            
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
            
            # 配賦詳細チャートを生成
            detail_fig = st.session_state.chart_generator.create_allocation_detail_chart(allocated_costs)
            
            # グラフを表示
            st.plotly_chart(detail_fig, use_container_width=True)
            
            # 配賦詳細の説明
            with st.expander("ℹ️ 配賦詳細の見方", expanded=False):
                st.markdown("""
                **グラフの見方:**
                - **青いバー**: 事業部固有コスト（固定費+変動費）
                - **オレンジのバー**: 本部コスト配賦分（固定費+変動費）
                
                **配賦の仕組み:**
                - 各事業部は固有のコスト（青）を持っています
                - 本部費用は設定した配賦割合に基づいて各事業部に配賦されます（オレンジ）
                - 配賦後の総コスト = 事業部固有コスト + 本部コスト配賦分
                """)
            
            # サマリーチャートを生成
            summary_fig = st.session_state.chart_generator.create_allocation_summary_chart(allocated_costs)
            
            # グラフを表示
            st.plotly_chart(summary_fig, use_container_width=True)
            
            # コスト構成の説明
            with st.expander("ℹ️ コスト構成の見方", expanded=False):
                st.markdown("""
                **グラフの見方:**
                - **青いバー**: 固定費（事業部固有+本部配賦）
                - **オレンジのバー**: 変動費（事業部固有+本部配賦）
                
                **コスト構成:**
                - 各事業部の総コストは固定費と変動費に分かれています
                - 固定費は売上に関係なく発生するコスト
                - 変動費は売上に比例して発生するコスト
                - 損益分岐点分析では、固定費÷限界利益率で損益分岐点を計算
                """)
            
            # 配賦詳細テーブル
            st.subheader("配賦詳細データ")
            detail_data = []
            for dept_name, costs in allocated_costs.items():
                detail_data.append({
                    "事業部": dept_name,
                    "事業部固有固定費": f"{costs['original_fixed']:,.0f}円",
                    "本部固定費配賦": f"{costs['hq_fixed_allocated']:,.0f}円",
                    "総固定費": f"{costs['fixed_cost']:,.0f}円",
                    "事業部固有変動費": f"{costs['original_variable']:,.0f}円",
                    "本部変動費配賦": f"{costs['hq_variable_allocated']:,.0f}円",
                    "総変動費": f"{costs['variable_cost']:,.0f}円",
                    "配賦後限界利益率": f"{costs['margin_rate']:.1%}"
                })
            
            detail_df = pd.DataFrame(detail_data)
            st.dataframe(detail_df, use_container_width=True)
            
            # 配賦割合テーブル
            st.subheader("本部費用配賦割合")
            allocation_ratios = st.session_state.data_manager.get_allocation_ratios()
            ratio_data = []
            for dept_name, ratios in allocation_ratios.items():
                ratio_data.append({
                    "事業部": dept_name,
                    "固定費配賦率": f"{ratios['fixed']:.1%}",
                    "変動費配賦率": f"{ratios['variable']:.1%}",
                    "固定費配賦額": f"{allocated_costs[dept_name]['hq_fixed_allocated']:,.0f}円",
                    "変動費配賦額": f"{allocated_costs[dept_name]['hq_variable_allocated']:,.0f}円"
                })
            
            ratio_df = pd.DataFrame(ratio_data)
            st.dataframe(ratio_df, use_container_width=True)
            
            # 配賦の影響分析
            st.subheader("配賦の影響分析")
            impact_analysis = st.session_state.data_manager.get_allocation_impact_analysis()
            
            # 影響分析をDataFrameで表示
            impact_data = []
            for dept_name, impact in impact_analysis.items():
                impact_data.append({
                    "事業部": dept_name,
                    "元の限界利益率": f"{impact['配賦前']['限界利益率']:.1%}",
                    "配賦後限界利益率": f"{impact['配賦後']['限界利益率']:.1%}",
                    "限界利益率変化": f"{impact['影響']['限界利益率変化']:+.1%}",
                    "売上総利益増加": f"{impact['影響']['売上総利益増加']:,.0f}円",
                    "売上総利益増加率": f"{impact['影響']['売上総利益増加率']:+.1f}%",
                    "変動費増加": f"{impact['影響']['変動費増加']:,.0f}円",
                    "変動費増加率": f"{impact['影響']['変動費増加率']:+.1f}%",
                    "固定費増加": f"{impact['影響']['固定費増加']:,.0f}円"
                })
            
            impact_df = pd.DataFrame(impact_data)
            st.dataframe(impact_df, use_container_width=True)
            
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
                implied_sales = st.session_state.data_manager.calculate_implied_sales(dept_name)
                basic_data.append({
                    "事業部": dept_name,
                    "元の限界利益率": f"{data['margin_rate']:.1%}",
                    "仮の売上総利益": f"{implied_sales:,.0f}円",
                    "固定費": f"{data['fixed_cost']:,.0f}円",
                    "変動費": f"{data['variable_cost']:,.0f}円"
                })
            
            basic_df = pd.DataFrame(basic_data)
            st.dataframe(basic_df, use_container_width=True)
            
            # 配賦後のデータ
            st.subheader("配賦後データ")
            allocated_costs = st.session_state.data_manager.calculate_allocated_costs()
            allocated_data = []
            for dept_name, costs in allocated_costs.items():
                allocated_data.append({
                    "事業部": dept_name,
                    "配賦後限界利益率": f"{costs['margin_rate']:.1%}",
                    "限界利益率変化": f"{costs['margin_rate'] - costs['original_margin_rate']:+.1%}",
                    "配賦後売上総利益": f"{costs['implied_sales']:,.0f}円",
                    "売上総利益増加": f"{costs['sales_increase']:,.0f}円",
                    "総固定費": f"{costs['fixed_cost']:,.0f}円",
                    "総変動費": f"{costs['variable_cost']:,.0f}円",
                    "本部固定費配賦": f"{costs['hq_fixed_allocated']:,.0f}円",
                    "本部変動費配賦": f"{costs['hq_variable_allocated']:,.0f}円"
                })
            
            allocated_df = pd.DataFrame(allocated_data)
            st.dataframe(allocated_df, use_container_width=True)
            
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
        
        with tab4:
            st.header("📚 損益分岐点分析の説明")
            
            # 説明ファイルの内容を読み込んで表示
            try:
                with open("損益分岐点分析の説明.md", "r", encoding="utf-8") as f:
                    explanation_content = f.read()
                
                # Markdownとして表示
                st.markdown(explanation_content)
                
            except FileNotFoundError:
                st.error("説明ファイルが見つかりません。")
            except Exception as e:
                st.error(f"ファイル読み込みエラー: {e}")
        
        # フッター
        st.markdown("---")
        st.markdown("**8期予算計画策定ツール** - 各事業部の利益体質に見合った目標設定を支援")
        
    except Exception as e:
        st.error(f"アプリケーションエラー: {e}")
        st.error("詳細なエラー情報:")
        st.code(traceback.format_exc())
        st.error(f"Python version: {sys.version}")

if __name__ == "__main__":
    main() 