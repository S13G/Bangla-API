from django.urls import path

from core import views

urlpatterns = [
    path('email/change/', views.ChangeEmailView.as_view(), name="change_email"),
    path('email/change/code/request/', views.RequestEmailChangeCodeView.as_view(), name="request_email_change_code"),
    path('email/verify/', views.VerifyEmailView.as_view(), name="verify_email"),
    path('email/verification/code/resend/', views.ResendEmailVerificationCodeView.as_view(),
         name="resend_verification_code"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('password/change/', views.ChangePasswordView.as_view(), name="change_password"),
    path('password/reset/code/request/', views.RequestNewPasswordCodeView.as_view(), name="request_password_code"),
    path('profile/', views.ListUpdateProfileView.as_view(), name="list_update_profile"),
    path('token/refresh/', views.RefreshView.as_view(), name="refresh_token"),
]
