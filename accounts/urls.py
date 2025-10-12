from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import send_test_email

urlpatterns = [
    path('send-email/', send_test_email, name='send_test_email'),

    # --- Authentication ---
    path("signup/", views.signup, name="signup"),
    path("login/", views.custom_login, name="login"),
    path("logout/", views.custom_logout, name="logout"),

    # --- Password Reset (Django built-in) ---
    path("password_reset/", auth_views.PasswordResetView.as_view(
        template_name="accounts/password_reset.html"
    ), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html"
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html"
    ), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html"
    ), name="password_reset_complete"),

    # --- Email Activation ---
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
]
