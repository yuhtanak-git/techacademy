"""
Authenticatorクラスの単体テスト
"""

import pytest
from authenticator import Authenticator


@pytest.fixture
def auth():
    """
    テストごとに新しいインスタンスを返す。
    """
    return Authenticator()


def test_register_success(auth):
    """
    registerメソッドでユーザーが正しく登録されるかを確認する。
    """
    auth.register("user1", "pass1")
    assert auth.users["user1"] == "pass1"


def test_register_duplicate_user(auth):
    """
    registerメソッドですでに存在するユーザー名で登録を試みた場合に、ValueError が発生することを確認する。
    """
    auth.register("user1", "pass1")
    with pytest.raises(ValueError, match="エラー: ユーザーは既に存在します。"):
        auth.register("user1", "pass2")


def test_login_success(auth):
    """
    loginメソッドで正しいユーザー名とパスワードでログインできるかを確認する。
    """
    auth.register("user1", "pass1")
    result = auth.login("user1", "pass1")
    assert result == "ログイン成功"


def test_login_wrong_password(auth):
    """
    loginメソッドで誤ったパスワードでログインした場合に、ValueError が発生することを確認する。
    """
    auth.register("user1", "pass1")
    with pytest.raises(
        ValueError, match="エラー: ユーザー名またはパスワードが正しくありません。"
    ):
        auth.login("wrongpass", "wrongpass")
