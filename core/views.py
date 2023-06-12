from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer, TokenObtainPairSerializer, \
    TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView

from core.emails import Util
from core.models import Profile, User
from core.serializers import ChangePasswordSerializer, LoginSerializer, ProfileSerializer, \
    RegisterSerializer, RequestNewPasswordCodeSerializer, \
    UpdateProfileSerializer


# Create your views here.


class ChangePasswordView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    throttle_classes = [UserRateThrottle]
    throttle_scope = 'password'

    @extend_schema(
            summary="Change password",
            description=
            """
            This endpoint allows the authenticated user to change their password after requesting for a code.
            The request should include the following data:

            - `code`: The verification code sent to the user's email.
            - `password`: The new password.

            If the password change is successful, the response will include the following data:

            - `message`: A success message indicating that the password has been updated successfully.
            - `status`: The status of the request.
            """
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.user.email
        code = serializer.validated_data['code']
        password = serializer.validated_data['password']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Account not found", "status": "failed"}, status=status.HTTP_404_NOT_FOUND)
        otp = user.otp.first()
        if otp is None or otp.code is None:
            return Response({"message": "No OTP found for this account", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)
        elif otp.code != code:
            return Response({"message": "Code is not correct", "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
        elif otp.expired:
            otp.delete()
            return Response({"message": "Code has expired. Request for another", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)

        if user.check_password(password):
            return Response({"message": "New password cannot be same as old password", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()
        otp.delete()
        return Response({"message": "Password updated successfully", "status": "success"}, status=status.HTTP_200_OK)


class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
    throttle_classes = [UserRateThrottle]

    @extend_schema(
            summary="Login",
            description=
            """
            This endpoint authenticates a registered and verified user and provides the necessary authentication tokens.
            The request should include the following data:

            - `email`: The user's email address.
            - `password`: The user's password.

            If the login is successful, the response will include the following data:

            - `access`: The access token used for authorization.
            - `refresh`: The refresh token used for obtaining a new access token.
            """

    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"message": "Invalid credentials", "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({"message": "Account is not active, contact the admin", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)

        tokens = super().post(request)

        return Response({"message": "Logged in successfully", "tokens": tokens.data,
                         "data": {"email": user.email, "full_name": user.full_name}, "status": "success"},
                        status=status.HTTP_200_OK)


class LogoutView(TokenBlacklistView):
    serializer_class = TokenBlacklistSerializer

    @extend_schema(
            summary="Logout",
            description=
            """
            This endpoint logs out an authenticated user by blacklisting their access token.
            The request should include the following data:

            - `refresh`: The refresh token used for authentication.

            If the logout is successful, the response will include the following data:

            - `message`: A success message indicating that the user has been logged out.
            - `status`: The status of the request.
            """
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response({"message": "Logged out successfully.", "status": "success"}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"message": "Token is blacklisted.", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateProfileView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    throttle_classes = [UserRateThrottle]

    @extend_schema(
            summary="Retrieve user profile",
            description=
            """
            This endpoint allows an authenticated user to retrieve their profile information.
            If the profile exists, the response will include the following data:

            - `message`: A success message indicating that the profile has been retrieved.
            - `data`: The user's profile information.
            - `status`: The status of the request.
            """
    )
    def get(self, request):
        customer_account = self.request.user
        try:
            customer_profile = Profile.objects.get(user=customer_account)
        except Profile.DoesNotExist:
            return Response({"message": "Profile for this customer account does not exist", "status": "failed"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(customer_profile)
        data = serializer.data
        return Response({"message": "Profile retrieved successfully", "data": data, "status": "success"},
                        status=status.HTTP_200_OK)

    @extend_schema(
            summary="Update profile",
            description=
            """
            This endpoint allows an authenticated user to update their profile information.
            The request should include the updated profile data.

            If the profile is successfully updated, the response will include the following data:

            - `message`: A success message indicating that the profile has been updated.
            - `data`: The updated user's profile information.
            - `status`: The status of the request.
            """
    )
    def patch(self, request):
        customer_account = self.request.user
        try:
            customer_profile = Profile.objects.get(user=customer_account)
        except Profile.DoesNotExist:
            return Response({"message": "Profile for this customer account does not exist", "status": "failed"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = UpdateProfileSerializer(data=request.data, partial=True, instance=customer_profile)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        return Response({"message": "Profile updated successfully", "data": data, "status": "success"},
                        status=status.HTTP_200_OK)


class RefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    @extend_schema(
            summary="Refresh token",
            description=
            """
            This endpoint allows a user to refresh an expired access token.
            The request should include the following data:

            - `access`: The expired access token.

            If the token refresh is successful, the response will include the following data:

            - `message`: A success message indicating that the token has been refreshed.
            - `token`: The new access token.
            - `status`: The status of the request.
            """

    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data['access']
        return Response({"message": "Refreshed successfully", "token": access_token, "status": "success"},
                        status=status.HTTP_200_OK)


class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer

    @extend_schema(
            summary="Registration",
            description=
            """
            This endpoint allows a new user to register an account.
            The request should include the following data:

            - `email`: The user's email address.
            - `first_name`: The user's first name.
            - `last_name`: The user's last name.
            - `password`: The user's password.

            If the registration is successful, the response will include the following data:

            - `message`: A success message indicating that the user has been registered.
            - `status`: The status of the request.
            """

    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = serializer.data

        Util.email_activation(user)
        return Response({"message": "Registered successfully. Check email for verification code", "data": data,
                         "status": "success"}, status=status.HTTP_201_CREATED)


class RequestNewPasswordCodeView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RequestNewPasswordCodeSerializer
    throttle_classes = [UserRateThrottle]

    @extend_schema(
            summary="Request new password code",
            description=
            """
            This endpoint allows a user to request a verification code to reset their password.
            The request should include the following data:

            - `email`: The user's email address.

            If the request is successful, the response will include the following data:

            - `message`: A success message indicating that the verification code has been sent.
            - `status`: The status of the request.
            """

    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "Account not found", "status": "failed"}, status=status.HTTP_404_NOT_FOUND)

        Util.password_activation(user)
        return Response({"message": "Password code sent successfully", "status": "success"}, status=status.HTTP_200_OK)
