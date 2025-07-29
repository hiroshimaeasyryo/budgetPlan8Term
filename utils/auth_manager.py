"""
認証機能管理モジュール
ユーザー管理、パスワードハッシュ化、セッション管理を提供
"""

import streamlit as st
import hashlib
import json
import os
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

class AuthManager:
    """認証機能を管理するクラス"""
    
    def __init__(self, users_file: str = "users.json"):
        """
        AuthManagerの初期化
        
        Args:
            users_file: ユーザー情報を保存するファイルパス
        """
        self.users_file = users_file
        self.users = self._load_users()
        
        # セッション状態の初期化
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0
        if 'lockout_until' not in st.session_state:
            st.session_state.lockout_until = None
    
    def _load_users(self) -> Dict:
        """ユーザー情報をファイルから読み込み"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"ユーザーファイルの読み込みエラー: {e}")
                return self._get_default_users()
        else:
            # デフォルトユーザーを作成
            default_users = self._get_default_users()
            self._save_users(default_users)
            return default_users
    
    def _save_users(self, users: Dict) -> None:
        """ユーザー情報をファイルに保存"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"ユーザーファイルの保存エラー: {e}")
    
    def _get_default_users(self) -> Dict:
        """デフォルトユーザーを取得（初回起動時のみ）"""
        # 環境変数から管理者アカウント情報を取得
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        admin_name = os.getenv('ADMIN_NAME', '管理者')
        
        # 初回起動時は管理者アカウントのみ作成
        return {
            admin_username: {
                "password_hash": self._hash_password(admin_password),
                "role": "admin",
                "name": admin_name,
                "created_at": datetime.now().isoformat()
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """パスワードをハッシュ化"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """パスワードを検証"""
        return self._hash_password(password) == password_hash
    
    def is_locked_out(self) -> bool:
        """アカウントがロックアウトされているかチェック"""
        if st.session_state.lockout_until:
            if datetime.now() < st.session_state.lockout_until:
                return True
            else:
                # ロックアウト期間終了
                st.session_state.lockout_until = None
                st.session_state.login_attempts = 0
        return False
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        ログイン処理
        
        Args:
            username: ユーザー名
            password: パスワード
            
        Returns:
            (成功フラグ, メッセージ)
        """
        # ロックアウトチェック
        if self.is_locked_out():
            remaining_time = st.session_state.lockout_until - datetime.now()
            minutes = int(remaining_time.total_seconds() // 60)
            seconds = int(remaining_time.total_seconds() % 60)
            return False, f"アカウントがロックされています。{minutes}分{seconds}秒後に再試行してください。"
        
        # ユーザー存在チェック
        if username not in self.users:
            self._increment_login_attempts()
            return False, "ユーザー名またはパスワードが正しくありません。"
        
        # パスワード検証
        user = self.users[username]
        if not self._verify_password(password, user['password_hash']):
            self._increment_login_attempts()
            return False, "ユーザー名またはパスワードが正しくありません。"
        
        # ログイン成功
        st.session_state.authenticated = True
        st.session_state.current_user = {
            'username': username,
            'name': user['name'],
            'role': user['role']
        }
        st.session_state.login_attempts = 0
        st.session_state.lockout_until = None
        
        return True, f"ようこそ、{user['name']}さん！"
    
    def _increment_login_attempts(self) -> None:
        """ログイン試行回数を増加"""
        st.session_state.login_attempts += 1
        
        # 5回失敗でロックアウト（5分間）
        if st.session_state.login_attempts >= 5:
            st.session_state.lockout_until = datetime.now() + timedelta(minutes=5)
    
    def logout(self) -> None:
        """ログアウト処理"""
        st.session_state.authenticated = False
        st.session_state.current_user = None
    
    def is_authenticated(self) -> bool:
        """認証済みかチェック"""
        return st.session_state.authenticated
    
    def get_current_user(self) -> Optional[Dict]:
        """現在のユーザー情報を取得"""
        return st.session_state.current_user
    
    def add_user(self, username: str, password: str, name: str, role: str = "user") -> Tuple[bool, str]:
        """
        新規ユーザーを追加
        
        Args:
            username: ユーザー名
            password: パスワード
            name: 表示名
            role: 役割
            
        Returns:
            (成功フラグ, メッセージ)
        """
        if username in self.users:
            return False, "ユーザー名が既に存在します。"
        
        if len(password) < 6:
            return False, "パスワードは6文字以上である必要があります。"
        
        self.users[username] = {
            "password_hash": self._hash_password(password),
            "role": role,
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_users(self.users)
        return True, f"ユーザー '{name}' を追加しました。"
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        パスワード変更
        
        Args:
            username: ユーザー名
            old_password: 現在のパスワード
            new_password: 新しいパスワード
            
        Returns:
            (成功フラグ, メッセージ)
        """
        if username not in self.users:
            return False, "ユーザーが存在しません。"
        
        user = self.users[username]
        if not self._verify_password(old_password, user['password_hash']):
            return False, "現在のパスワードが正しくありません。"
        
        if len(new_password) < 6:
            return False, "新しいパスワードは6文字以上である必要があります。"
        
        user['password_hash'] = self._hash_password(new_password)
        self._save_users(self.users)
        
        return True, "パスワードを変更しました。"
    
    def get_users(self) -> Dict:
        """ユーザー一覧を取得（パスワードハッシュは除外）"""
        users_info = {}
        for username, user in self.users.items():
            users_info[username] = {
                'name': user['name'],
                'role': user['role'],
                'created_at': user['created_at']
            }
        return users_info 