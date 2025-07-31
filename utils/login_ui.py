"""
ログイン画面とユーザー管理画面のUIコンポーネント
"""

import streamlit as st
from utils.auth_manager import AuthManager
from typing import Optional

def show_login_page() -> Optional[bool]:
    """
    ログイン画面を表示
    
    Returns:
        ログイン成功時はTrue、失敗時はFalse、キャンセル時はNone
    """
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🔐 8期予算計画策定ツール</h1>
        <p style="font-size: 1.2rem; color: #666;">ログインしてください</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 中央に配置
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # シンプルなログインフォーム
        with st.form("login_form"):
            st.markdown("### ログイン")
            
            username = st.text_input("ユーザー名", key="login_username")
            password = st.text_input("パスワード", type="password", key="login_password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_submitted = st.form_submit_button("ログイン", type="primary")
            with col2:
                cancel_submitted = st.form_submit_button("キャンセル")
            
            if cancel_submitted:
                return None
            
            if login_submitted:
                if not username or not password:
                    st.error("ユーザー名とパスワードを入力してください。")
                    return False
                
                auth_manager = AuthManager()
                success, message = auth_manager.login(username, password)
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
                    return False
        
        # 初回起動時の案内
        with st.expander("ℹ️ 初回起動について", expanded=False):
            st.markdown("""
            **初回起動時:**
            - 管理者アカウントが自動的に作成されます
            - 環境変数で設定可能（ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_NAME）
            - デフォルト: ユーザー名 `admin` / パスワード `admin123`
            
            **セキュリティ注意事項:**
            - 初回ログイン後、必ずパスワードを変更してください
            - 管理者アカウントでログイン後、必要に応じて一般ユーザーを追加してください
            - 本番環境では環境変数で管理者アカウントを設定することを推奨します
            """)
    
    return False

def show_user_management_page():
    """ユーザー管理画面を表示"""
    st.title("👥 ユーザー管理")
    
    auth_manager = AuthManager()
    current_user = auth_manager.get_current_user()
    
    # 管理者権限チェック
    if not current_user or current_user['role'] != 'admin':
        st.error("このページにアクセスするには管理者権限が必要です。")
        return
    
    # タブを作成
    tab1, tab2, tab3 = st.tabs(["📋 ユーザー一覧", "➕ 新規ユーザー追加", "🔑 パスワード変更"])
    
    with tab1:
        st.subheader("ユーザー一覧")
        
        users = auth_manager.get_users()
        if users:
            user_data = []
            for username, user_info in users.items():
                user_data.append({
                    "ユーザー名": username,
                    "表示名": user_info['name'],
                    "役割": user_info['role'],
                    "作成日": user_info['created_at'][:10]
                })
            
            st.dataframe(user_data, use_container_width=True)
        else:
            st.info("ユーザーが登録されていません。")
    
    with tab2:
        st.subheader("新規ユーザー追加")
        
        with st.form("add_user_form"):
            new_username = st.text_input("ユーザー名")
            new_password = st.text_input("パスワード", type="password")
            new_name = st.text_input("表示名")
            new_role = st.selectbox("役割", ["user", "admin"], format_func=lambda x: "一般ユーザー" if x == "user" else "管理者")
            
            if st.form_submit_button("ユーザーを追加"):
                if not all([new_username, new_password, new_name]):
                    st.error("すべての項目を入力してください。")
                else:
                    success, message = auth_manager.add_user(new_username, new_password, new_name, new_role)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    with tab3:
        st.subheader("パスワード変更")
        
        with st.form("change_password_form"):
            change_username = st.selectbox("ユーザー", list(users.keys()) if users else [])
            old_password = st.text_input("現在のパスワード", type="password")
            new_password = st.text_input("新しいパスワード", type="password")
            confirm_password = st.text_input("新しいパスワード（確認）", type="password")
            
            if st.form_submit_button("パスワードを変更"):
                if not all([change_username, old_password, new_password, confirm_password]):
                    st.error("すべての項目を入力してください。")
                elif new_password != confirm_password:
                    st.error("新しいパスワードが一致しません。")
                else:
                    success, message = auth_manager.change_password(change_username, old_password, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

def show_user_profile():
    """ユーザープロフィール画面を表示"""
    st.title("👤 ユーザープロフィール")
    
    auth_manager = AuthManager()
    current_user = auth_manager.get_current_user()
    
    if not current_user:
        st.error("ログインしていません。")
        return
    
    # ユーザー情報表示
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ユーザー情報")
        st.write(f"**ユーザー名:** {current_user['username']}")
        st.write(f"**表示名:** {current_user['name']}")
        st.write(f"**役割:** {current_user['role']}")
    
    with col2:
        st.subheader("アカウント操作")
        
        # パスワード変更
        with st.expander("🔑 パスワード変更"):
            with st.form("profile_password_change"):
                old_password = st.text_input("現在のパスワード", type="password")
                new_password = st.text_input("新しいパスワード", type="password")
                confirm_password = st.text_input("新しいパスワード（確認）", type="password")
                
                if st.form_submit_button("パスワードを変更"):
                    if not all([old_password, new_password, confirm_password]):
                        st.error("すべての項目を入力してください。")
                    elif new_password != confirm_password:
                        st.error("新しいパスワードが一致しません。")
                    else:
                        success, message = auth_manager.change_password(
                            current_user['username'], 
                            old_password, 
                            new_password
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        # ログアウト
        if st.button("🚪 ログアウト", type="secondary"):
            auth_manager.logout()
            st.success("ログアウトしました。")
            st.rerun()

def show_user_info_in_sidebar():
    """サイドバーにユーザー情報を表示"""
    auth_manager = AuthManager()
    current_user = auth_manager.get_current_user()
    
    if current_user:
        with st.sidebar:
            st.markdown("### 👤 ユーザー情報")
            st.write(f"**名前:** {current_user['name']}")
            st.write(f"**役割:** {current_user['role']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⚙️ 設定", use_container_width=True):
                    st.switch_page("?page=profile")
            with col2:
                if st.button("🚪 ログアウト", use_container_width=True, type="secondary"):
                    auth_manager.logout()
                    st.success("ログアウトしました。")
                    st.rerun()

def show_header_with_user_info():
    """ヘッダーにユーザー情報を表示（非推奨 - サイドバー版を使用してください）"""
    # この関数は非推奨です。show_user_info_in_sidebar()を使用してください。
    pass 