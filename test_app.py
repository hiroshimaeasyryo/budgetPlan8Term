"""
アプリケーションの動作確認用テストスクリプト
"""

import streamlit as st
import sys
import os

def test_imports():
    """必要なモジュールのインポートテスト"""
    try:
        import streamlit
        st.success(f"Streamlit version: {streamlit.__version__}")
        
        import plotly
        st.success(f"Plotly version: {plotly.__version__}")
        
        import pandas
        st.success(f"Pandas version: {pandas.__version__}")
        
        import numpy
        st.success(f"NumPy version: {numpy.__version__}")
        
        return True
    except ImportError as e:
        st.error(f"Import error: {e}")
        return False

def test_utils():
    """utilsモジュールのテスト"""
    try:
        from utils.data_manager import DataManager
        from utils.chart_generator import ChartGenerator
        
        data_manager = DataManager()
        chart_generator = ChartGenerator()
        
        st.success("Utils modules imported successfully")
        return True
    except Exception as e:
        st.error(f"Utils error: {e}")
        return False

def main():
    st.title("🔧 アプリケーション動作確認")
    
    st.header("Python環境情報")
    st.write(f"Python version: {sys.version}")
    st.write(f"Working directory: {os.getcwd()}")
    
    st.header("依存関係の確認")
    if test_imports():
        st.success("✅ すべての依存関係が正常にインポートされました")
    else:
        st.error("❌ 依存関係のインポートに失敗しました")
    
    st.header("Utilsモジュールの確認")
    if test_utils():
        st.success("✅ Utilsモジュールが正常に動作しています")
    else:
        st.error("❌ Utilsモジュールでエラーが発生しました")
    
    st.header("テスト完了")
    st.info("このページが正常に表示されていれば、基本的な環境は動作しています。")

if __name__ == "__main__":
    main() 