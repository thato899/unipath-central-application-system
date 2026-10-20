from django.urls import include, path
from applications import views
from applications.auth_views import RegisterView, SecureLoginView, setup_totp, logout_view

urlpatterns = [
    path("", views.home, name="home"),
    path("api/", include("applications.urls")),
    path("auth/login/", SecureLoginView.as_view(), name="login"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/2fa/setup/", setup_totp, name="totp_setup"),
    path("auth/logout/", logout_view, name="logout"),
]
