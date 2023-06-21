from django.db import transaction
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from core.choices import GENDER_CHOICES
from matrimonials.choices import CONNECTION_CHOICES, EDUCATION_CHOICES, RELIGION_CHOICES
from matrimonials.models import ConnectionRequest, Conversation, MatrimonialProfile, MatrimonialProfileImage


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

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        if MatrimonialProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                    {"message": "This user already has a matrimonial profile", "status": "failed"}
            )

        images = validated_data.pop('images')
        profile = MatrimonialProfile.objects.create(user=user, **validated_data)

        matrimonial_images = [
            MatrimonialProfileImage(matrimonial_profile=profile, _image=image)
            for image in images
        ]
        MatrimonialProfileImage.objects.bulk_create(matrimonial_images)

        return profile


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


class MessageSerializer(serializers.Serializer):
    sender = serializers.UUIDField()
    text = serializers.CharField()
    attachment = serializers.FileField(allow_empty_file=True, required=False)

    def validate(self, attrs):
        sender = attrs.get('sender')

        try:
            MatrimonialProfile.objects.get(id=sender)
        except MatrimonialProfile.DoesNotExist:
            return serializers.ValidationError(
                    {"message": "Sender matrimonial profile doesn't exist", "status": "failed"})


class ConversationListSerializer(serializers.Serializer):
    initiator = serializers.UUIDField()
    receiver = serializers.UUIDField()
    last_message = serializers.SerializerMethodField()

    @staticmethod
    def get_last_message(obj: Conversation):
        message = obj.messages.first()
        return MessageSerializer(message)

    def validate(self, attrs):
        initiator = attrs.get('initiator')
        receiver = attrs.get('receiver')

        try:
            MatrimonialProfile.objects.get(id=initiator)
        except MatrimonialProfile.DoesNotExist:
            return serializers.ValidationError(
                    {"message": "Initiator matrimonial profile doesn't exist", "status": "failed"})

        try:
            MatrimonialProfile.objects.get(id=receiver)
        except MatrimonialProfile.DoesNotExist:
            return serializers.ValidationError(
                    {"message": "Receiver matrimonial profile doesn't exist", "status": "failed"})


class ConversationSerializer(serializers.Serializer):
    initiator = serializers.UUIDField()
    receiver = serializers.UUIDField()
    messages = MessageSerializer(many=True)

    def validate(self, attrs):
        initiator = attrs.get('initiator')
        receiver = attrs.get('receiver')

        try:
            MatrimonialProfile.objects.get(id=initiator)
        except MatrimonialProfile.DoesNotExist:
            return serializers.ValidationError(
                    {"message": "Initiator matrimonial profile doesn't exist", "status": "failed"})

        try:
            MatrimonialProfile.objects.get(id=receiver)
        except MatrimonialProfile.DoesNotExist:
            return serializers.ValidationError(
                    {"message": "Receiver matrimonial profile doesn't exist", "status": "failed"})
