import re

from django.core.validators import FileExtensionValidator
from django.core.validators import validate_email
from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import User


class ChangePasswordSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    password = serializers.CharField(max_length=50, min_length=6, write_only=True)

    def validate(self, attrs):
        code = attrs.get('code')

        if not code:
            raise serializers.ValidationError({"message": "Code is required", "status": "failed"})

        if not re.match("^[0-9]{4}$", str(code)):
            raise serializers.ValidationError({"message": "Code must be 4-digit number", "status": "failed"})

        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=150, min_length=6, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')

        try:
            validate_email(email)
        except ValidationError:
            raise serializers.ValidationError({"message": "Invalid email format", "status": "failed"})

        return attrs


class ProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField(source="user.full_name")
    email = serializers.EmailField(source="user.email")
    _avatar = serializers.ImageField(validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    country = CountryField()
    phone_number = serializers.CharField(max_length=20)

    def validate__avatar(self, attrs):
        avatar = attrs.get('_avatar')
        max_size = 5 * 1024 * 1024  # 3MB in bytes
        if avatar.size > max_size:
            raise ValidationError({"message": f"Image {avatar} size should be less than 5MB", "status": "failed"})
        return attrs

    def validate_phone_number(self, value):
        phone_number = value
        if not phone_number.startswith('+'):
            raise ValidationError({"message": "Phone number must start with a plus sign (+)", "status": "failed"})
        if not phone_number[1:].isdigit():
            raise ValidationError(
                    {"message": "Phone number must only contain digits after the plus sign (+)", "status": "failed"})
        return value


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=50, min_length=6, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        full_name = attrs.get('full_name')

        try:
            validate_email(email)
        except ValidationError:
            raise serializers.ValidationError({"message": "Invalid email format", "status": "failed"})

        if not full_name:
            raise serializers.ValidationError({"message": "full name is required", "status": "failed"})

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RequestNewPasswordCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')

        try:
            validate_email(email)
        except ValidationError:
            raise serializers.ValidationError({"message": "Invalid email format", "status": "failed"})
        return attrs


class UpdateProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField(source="user.full_name")
    email = serializers.EmailField(source="user.email")
    _avatar = serializers.ImageField(validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    description = serializers.CharField()
    country = CountryField()
    language = serializers.CharField()
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        phone_number = value
        if not phone_number.startswith('+'):
            raise ValidationError({"message": "Phone number must start with a plus sign (+)", "status": "failed"})
        if not phone_number[1:].isdigit():
            raise ValidationError(
                    {"message": "Phone number must only contain digits after the plus sign (+)", "status": "failed"})
        return value

    def validate__avatar(self, attrs):
        avatar = attrs.get('_avatar')
        max_size = 5 * 1024 * 1024  # 3MB in bytes
        if avatar.size > max_size:
            raise ValidationError({"message": f"Image {avatar} size should be less than 5MB", "status": "failed"})
        return attrs

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
            instance.save()
        return instance
