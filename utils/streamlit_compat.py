"""
Streamlitのバージョン互換性を確保するヘルパー関数
"""

import streamlit as st
from typing import Optional, Any

def get_query_param(key: str, default: Any = None) -> Any:
    """
    クエリパラメータを取得（バージョン互換）
    
    Args:
        key: パラメータ名
        default: デフォルト値
        
    Returns:
        パラメータ値
    """
    try:
        # 新しいバージョンのStreamlit
        return st.query_params.get(key, default)
    except AttributeError:
        # 古いバージョンのStreamlit
        params = st.experimental_get_query_params()
        values = params.get(key, [default])
        return values[0] if values else default

def set_query_param(key: str, value: str) -> None:
    """
    クエリパラメータを設定（バージョン互換）
    
    Args:
        key: パラメータ名
        value: パラメータ値
    """
    try:
        # 新しいバージョンのStreamlit
        st.query_params[key] = value
    except AttributeError:
        # 古いバージョンのStreamlit
        st.experimental_set_query_params(**{key: value})

def rerun_app() -> None:
    """
    アプリケーションを再実行（バージョン互換）
    """
    try:
        # 新しいバージョンのStreamlit
        st.rerun()
    except AttributeError:
        # 古いバージョンのStreamlit
        st.experimental_rerun() 