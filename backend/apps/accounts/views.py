"""Authentication API views."""
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from apps.accounts.auth_cookies import attach_auth_cookies, clear_auth_cookies
from apps.accounts.permissions import IsAuthenticatedUser
from apps.accounts.services import AuthService, PermissionService, RoleService
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    ProfileSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UpdateProfileSerializer,
    UserSerializer,
    VerifyEmailSerializer,
)
from apps.customers.serializers import CustomerSerializer


class AuthAnonThrottle(AnonRateThrottle):
    scope = "auth"


class AuthUserThrottle(UserRateThrottle):
    scope = "auth_user"


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        response = Response(
            {
                "user": UserSerializer(result["user"]).data,
                "customer": CustomerSerializer(result["customer"]).data,
                "tokens": result["tokens"],
                "message": result["message"],
            },
            status=status.HTTP_201_CREATED,
        )
        return attach_auth_cookies(response, result["tokens"])


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = AuthService.login(
            email=serializer.validated_data["email"],
            password=request.data["password"],
        )
        payload = {
            "user": UserSerializer(result["user"]).data,
            "tokens": result["tokens"],
        }
        if result["customer"]:
            payload["customer"] = CustomerSerializer(result["customer"]).data
        response = Response(payload)
        return attach_auth_cookies(response, result["tokens"])


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthUserThrottle]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = (
            request.COOKIES.get(settings.JWT_AUTH_REFRESH_COOKIE)
            or serializer.validated_data.get("refresh")
        )
        if refresh:
            AuthService.logout(refresh_token=refresh)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_auth_cookies(response)
        return response


class ProfileView(APIView):
    permission_classes = [IsAuthenticatedUser]
    throttle_classes = [AuthUserThrottle]

    def get(self, request):
        payload = AuthService.get_profile_payload(request.user)
        return Response(ProfileSerializer(payload).data)

    def patch(self, request):
        serializer = UpdateProfileSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        AuthService.update_profile(request.user, **serializer.validated_data)
        return self.get(request)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AuthService.verify_email(
            uid=serializer.validated_data["uid"],
            token=serializer.validated_data["token"],
        )
        return Response(
            {
                "message": "Email verified successfully.",
                "user": UserSerializer(user).data,
            }
        )


class ResendVerificationView(APIView):
    permission_classes = [IsAuthenticatedUser]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        AuthService.resend_verification_email(request.user)
        return Response({"message": "Verification email sent."})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.request_password_reset(email=serializer.validated_data["email"])
        return Response(
            {
                "message": (
                    "If an account exists for that email, "
                    "password reset instructions have been sent."
                )
            }
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthAnonThrottle]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.reset_password(
            uid=serializer.validated_data["uid"],
            token=serializer.validated_data["token"],
            password=serializer.validated_data["password"],
        )
        return Response({"message": "Password reset successfully."})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticatedUser]
    throttle_classes = [AuthUserThrottle]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.change_password(
            user=request.user,
            current_password=serializer.validated_data["current_password"],
            new_password=serializer.validated_data["new_password"],
        )
        return Response({"message": "Password changed successfully."})


class PermissionsView(APIView):
    """GET /auth/permissions/ — current user's roles and permission codenames."""

    permission_classes = [IsAuthenticatedUser]
    throttle_classes = [AuthUserThrottle]

    def get(self, request):
        return Response(
            {
                "roles": RoleService.get_role_slugs(request.user),
                "permissions": PermissionService.get_user_permissions(request.user),
            }
        )


# Backward-compatible alias
MeView = ProfileView
