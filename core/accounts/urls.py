from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, SendTokenView,
    VerifyTokenView, ResetPasswordView, UserDetailView
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/send-token/', SendTokenView.as_view(), name='auth-send-token'),
    path('auth/verify-token/', VerifyTokenView.as_view(), name='auth-verify-token'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='auth-reset-password'),
    path('auth/user/', UserDetailView.as_view(), name='auth-user-detail'),
]