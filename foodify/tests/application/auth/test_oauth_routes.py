from unittest import TestCase

from tests.factories import UsersFactory
from tests.test_sql_app import test_client


class OAuthRoutesTestCase(TestCase):
    def setUp(self):
        super().setUp()

    def test_login_user_does_not_exist(self):
        response = test_client.post(
            "/token", json={"username": "test", "password": "test"}
        )
        self.assertEqual(response.status_code, 404)

    def test_login_user_invalid_password(self):
        user = UsersFactory(username="test_username", password="test_password")
        response = test_client.post(
            "/api/oauth2/token",
            data={"username": user.username, "password": "not_valid_password"},
        )
        self.assertEqual(response.status_code, 401)

    def test_login_valid(self):
        user_password = "test_password"
        user = UsersFactory(username="test_username", password=user_password)
        response = test_client.post(
            "/api/oauth2/token",
            data={"username": user.username, "password": user_password},
        )
        self.assertEqual(response.status_code, 200)
