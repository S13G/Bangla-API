from django.urls import path

from core import views

urlpatterns = [
    path('email/verify/', views.VerifyEmailView.as_view(), name="verify_email"),
    path('email/verification/code/resend/', views.ResendEmailVerificationCodeView.as_view(),
         name="resend_verification_code"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('password/change/', views.ChangePasswordView.as_view(), name="change_password"),
    path('password/reset/code/request/', views.RequestNewPasswordCodeView.as_view(), name="request_password_code"),
    path('profile/', views.RetrieveUpdateProfileView.as_view(), name="retrieve_update_profile"),
    path('token/refresh/', views.RefreshView.as_view(), name="refresh_token")
]
