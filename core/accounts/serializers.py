from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id','email','username','phone','name','password','password_confirm')
        read_only_fields = ('id',)

    def validate(self, attrs):
        p1 = attrs.get('password')
        p2 = attrs.pop('password_confirm', None)
        if p1 or p2:
            if p1 != p2:
                raise serializers.ValidationError({"password": "Passwords do not match."})
            validate_password(p1, user=self.instance)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # email/username/phone
    password = serializers.CharField(write_only=True)


class SendTokenSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)  # email/username/phone
    purpose = serializers.ChoiceField(choices=('verify', 'reset'))


class VerifyTokenSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    code = serializers.CharField()
    purpose = serializers.ChoiceField(choices=('email', 'phone'))

class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, v):
        validate_password(v)
        return v


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email','username','phone','name','is_active','is_staff')
        read_only_fields = ('id','is_staff','is_active')
