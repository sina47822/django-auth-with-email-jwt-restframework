from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model
from .serializers import (
    RegistrationSerializer, LoginSerializer, SendTokenSerializer,
    VerifyTokenSerializer, ResetPasswordSerializer, UserDetailSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import get_object_or_404
from .utils import send_verification_email, send_verification_via_sms, make_token, make_uid
from django.db import transaction
from django.utils import timezone

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


def get_user_by_identifier(identifier):
    # case-insensitive search for email/username/phone
    qs = User.objects.filter(
        email__iexact=identifier
    ) | User.objects.filter(username__iexact=identifier) | User.objects.filter(phone__iexact=identifier)
    return qs.first()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        # Optionally send verification token
        if user.email:
            send_verification_email(user, purpose='verify')
        elif user.phone:
            send_verification_via_sms(user, purpose='verify')


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        identifier = s.validated_data['identifier']
        password = s.validated_data['password']

        user = get_user_by_identifier(identifier)
        if user is None:
            return Response({"detail":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({"detail":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"detail":"User inactive"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserDetailSerializer(user).data
        })


class LogoutView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        # expect refresh token in body to blacklist
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail":"Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail":"Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail":"Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class SendTokenView(generics.GenericAPIView):
    serializer_class = SendTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        identifier = s.validated_data['identifier']
        purpose = s.validated_data['purpose']

        user = get_user_by_identifier(identifier)
        if not user:
            return Response({"detail":"No user found"}, status=status.HTTP_404_NOT_FOUND)

        if user.email and purpose in ('verify','reset'):
            send_verification_email(user, purpose=purpose)
        elif user.phone:
            send_verification_via_sms(user, purpose=purpose)
        else:
            return Response({"detail":"No delivery method available"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail":"Token sent"}, status=status.HTTP_200_OK)


class VerifyTokenView(generics.GenericAPIView):
    serializer_class = VerifyTokenSerializer
    permission_classes = (permissions.AllowAny,)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        identifier = s.validated_data['identifier']
        code = s.validated_data['code']
        purpose = s.validated_data['purpose']

        user = get_user_by_identifier(identifier)
        if not user:
            return Response({"detail": "User not found"}, status=404)

        now = timezone.now()

        if purpose == "phone":
            if user.phone_verification_code != code:
                return Response({"detail": "Invalid code"}, status=400)
            if user.phone_verification_expiry < now:
                return Response({"detail": "Code expired"}, status=400)
            user.is_phone_verified = True
            user.phone_verified_at = now
            user.phone_verification_code = None
            user.phone_verification_expiry = None
            user.save(update_fields=['is_phone_verified', 'phone_verified_at', 'phone_verification_code', 'phone_verification_expiry'])

        elif purpose == "email":
            if user.email_verification_code != code:
                return Response({"detail": "Invalid code"}, status=400)
            if user.email_verification_expiry < now:
                return Response({"detail": "Code expired"}, status=400)
            user.is_email_verified = True
            user.email_verified_at = now
            user.email_verification_code = None
            user.email_verification_expiry = None
            user.save(update_fields=['is_email_verified', 'email_verified_at', 'email_verification_code', 'email_verification_expiry'])

        user.refresh_from_db()
        return Response({"detail": f"{purpose.capitalize()} verified", "user": UserDetailSerializer(user).data})

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        uid = s.validated_data['uid']
        token = s.validated_data['token']
        new_password = s.validated_data['new_password']

        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pk)
        except Exception:
            return Response({"detail":"Invalid uid"}, status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({"detail":"Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail":"Password reset successful"}, status=status.HTTP_200_OK)


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
