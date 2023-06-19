from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from core.choices import GENDER_CHOICES
from matrimonials.choices import CONNECTION_CHOICES, EDUCATION_CHOICES, RELIGION_CHOICES
from matrimonials.models import ConnectionRequest, MatrimonialProfile


class CreateMatrimonialProfileSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField(), max_length=6)
    short_bio = serializers.CharField()
    age = serializers.IntegerField()
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    height = serializers.CharField()
    country = CountryField()
    city = serializers.CharField()
    religion = serializers.ChoiceField(choices=RELIGION_CHOICES)
    birthday = serializers.DateField()
    education = serializers.ChoiceField(choices=EDUCATION_CHOICES)
    profession = serializers.CharField()
    income = serializers.IntegerField()

    def validate(self, attrs):
        short_bio = attrs.get('short_bio')
        income = attrs.get('income')
        if len(short_bio) < 10:
            raise serializers.ValidationError(
                    {"message": "Short bio should have at least 10 characters.", "status": "failed"})
        if income < 0:
            raise serializers.ValidationError({"message": "Income should be a positive value.", "status": "failed"})
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        if MatrimonialProfile.objects.filter(user=user).exists():
            serializers.ValidationError({"message": "Ths user already has a matrimonial profile", "status": "failed"})
        return MatrimonialProfile.objects.create(user=user, **validated_data)


class MatrimonialProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField(source="user.full_name")
    image = serializers.SerializerMethodField()
    short_bio = serializers.CharField()
    religion = serializers.CharField()
    education = serializers.CharField()
    profession = serializers.CharField()
    country = CountryField()

    def get_image(self, obj: MatrimonialProfile):
        first_image = obj.images.first()
        if first_image:
            return first_image.matrimonial_image
        return first_image


class ConnectionRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    sender = serializers.UUIDField()
    receiver = serializers.UUIDField()
    status = serializers.ChoiceField(choices=CONNECTION_CHOICES)
    created = serializers.DateTimeField(read_only=True)

    def validate(self, attrs):
        sender = attrs.get('sender')
        receiver = attrs.get('receiver')

        try:
            MatrimonialProfile.objects.get(id=sender)
        except MatrimonialProfile.DoesNotExist:
            return serializers.ValidationError(
                    {"message": "Sender matrimonial profile doesn't exist", "status": "failed"})

        try:
            MatrimonialProfile.objects.get(id=receiver)
        except MatrimonialProfile.DoesNotExist:
            return serializers.ValidationError(
                    {"message": "Receiver matrimonial profile doesn't exist", "status": "failed"})

    def create(self, validated_data):
        return ConnectionRequest.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance