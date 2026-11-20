from django.urls import path

from .views import login_view, logout_view, me

urlpatterns = [
    path("me/", me, name="me"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]
