import re

from django.core.validators import FileExtensionValidator
from django.core.validators import validate_email
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from common.exceptions import CustomValidation
from core.models import User


class ChangePasswordSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    password = serializers.CharField(max_length=50, min_length=6, write_only=True)

    def validate(self, attrs):
        code = attrs.get('code')

        if not code:
            raise CustomValidation({"message": "Code is required", "status": "failed"})

        if not re.match("^[0-9]{4}$", str(code)):
            raise CustomValidation({"message": "Code must be 4-digit number", "status": "failed"})

        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(max_length=150, min_length=6, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')

        try:
            validate_email(email)
        except Exception:
            raise CustomValidation({"message": "Invalid email format", "status": "failed"})

        return attrs


class ProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField(source="user.full_name")
    email = serializers.CharField(source="user.email")
    avatar = serializers.ImageField(validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    country = CountryField()
    phone_number = serializers.CharField(source="user.phone_number")

    def validate_avatar(self, attrs):
        avatar = attrs.get('avatar')
        max_size = 5 * 1024 * 1024  # 3MB in bytes
        if avatar.size > max_size:
            raise CustomValidation({"message": f"Image {avatar} size should be less than 5MB", "status": "failed"})
        return attrs

    def validate_phone_number(self, value):
        phone_number = value
        if not phone_number.startswith('+'):
            raise CustomValidation({"message": "Phone number must start with a plus sign (+)", "status": "failed"})
        if not phone_number[1:].isdigit():
            raise CustomValidation(
                    {"message": "Phone number must only contain digits after the plus sign (+)", "status": "failed"})
        return value


class RegisterSerializer(serializers.Serializer):
    email = serializers.CharField()
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField(min_length=6, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        full_name = attrs.get('full_name')
        phone_number = attrs.get('phone_number')

        if User.objects.filter(email=email).exists():
            raise CustomValidation({"message": "User with this email address already exists", "status": "failed"})

        try:
            validate_email(email)
        except Exception:
            raise CustomValidation({"message": "Invalid email format", "status": "failed"})

        if not full_name:
            raise CustomValidation({"message": "full name is required", "status": "failed"})

        if not phone_number.startswith('+'):
            raise CustomValidation({"message": "Phone number must start with a plus sign (+)", "status": "failed"})
        if not phone_number[1:].isdigit():
            raise CustomValidation(
                    {"message": "Phone number must only contain digits after the plus sign (+)", "status": "failed"})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RequestNewPasswordCodeSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')

        try:
            validate_email(email)
        except Exception:
            raise CustomValidation({"message": "Invalid email format", "status": "failed"})
        return attrs


class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')

        try:
            validate_email(email)
        except Exception:
            raise CustomValidation({"message": "Invalid email format", "status": "failed"})
        return attrs


class UpdateProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField(source="user.full_name")
    email = serializers.CharField(source="user.email", read_only=True)
    avatar = serializers.ImageField(validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    description = serializers.CharField()
    country = CountryField()
    language = serializers.CharField()
    phone_number = serializers.CharField(source="user.phone_number")

    def validate_phone_number(self, value):
        phone_number = value
        if not phone_number.startswith('+'):
            raise CustomValidation({"message": "Phone number must start with a plus sign (+)", "status": "failed"})
        if not phone_number[1:].isdigit():
            raise CustomValidation(
                    {"message": "Phone number must only contain digits after the plus sign (+)", "status": "failed"})
        return value

    def validate_avatar(self, attrs):
        avatar = attrs.get('avatar')
        max_size = 5 * 1024 * 1024  # 3MB in bytes
        if avatar.size > max_size:
            raise CustomValidation({"message": f"Image {avatar} size should be less than 5MB", "status": "failed"})
        return attrs

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            for field, value in user_data.items():
                setattr(instance.user, field, value)
            instance.user.save()

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        return instance


class VerifyEmailSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    email = serializers.CharField()

    def validate(self, attrs):
        code = attrs.get('code')
        email = attrs.get('email')

        if not code:
            raise CustomValidation({"message": "Code is required", "status": "failed"})

        if not re.match("^[0-9]{4}$", str(code)):
            raise CustomValidation({"message": "Code must be a 4-digit number", "status": "failed"})

        try:
            validate_email(email)
        except CustomValidation:
            raise CustomValidation({"message": "Invalid email format", "status": "failed"})

        return attrs
