from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class AuthApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "password"
        cls.username = "test"
        cls.user = get_user_model().objects.create_user(
            username=cls.username, password=cls.password
        )

    def test_me_without_session(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login(self):
        response = self.client.post(
            reverse("login"), {"username": self.username, "password": self.password}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("id"), self.user.id)
        self.assertEqual(response.data.get("username"), self.user.username)

    def test_me_after_login(self):
        self.client.post(reverse("login"), {"username": self.username, "password": self.password})
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_wrong_password(self):
        response = self.client.post(
            reverse("login"), {"username": self.username, "password": "wrong"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_with_session_and__me_after(self):
        self.client.post(reverse("login"), {"username": self.username, "password": self.password})
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_without_session(self):
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # The CSRF tests below use their own client: self.client skips CSRF checks,
    # so it would let these requests through.

    # Regression guard: if this fails, @csrf_protect was probably moved above
    # @api_view in login_view, which silently disables it.
    def test_login_without_token(self):
        client = APIClient(enforce_csrf_checks=True)
        response = client.post(
            reverse("login"), {"username": self.username, "password": self.password}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_with_token(self):
        client = APIClient(enforce_csrf_checks=True)
        # Same flow as the React app: /me/ sets the csrftoken cookie (even on 403),
        # then the token is copied into the X-CSRFToken header.
        client.get(reverse("me"))
        token = client.cookies["csrftoken"].value
        response = client.post(
            reverse("login"),
            {"username": self.username, "password": self.password},
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_with_session_without_token(self):
        client = APIClient(enforce_csrf_checks=True)
        # client.login() creates the session without going through login_view.
        client.login(username=self.username, password=self.password)
        # Rejected by DRF's SessionAuthentication, which checks CSRF for
        # authenticated users (logout_view has no @csrf_protect).
        response = client.post(reverse("logout"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
