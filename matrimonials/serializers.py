import re

from django.db import transaction
from django.db.models import Q
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from common.exceptions import CustomValidation
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
        height = attrs.get('height')
        if len(short_bio) < 10:
            raise CustomValidation(
                    {"message": "Short bio should have at least 10 characters.", "status": "failed"})
        if income < 0:
            raise CustomValidation({"message": "Income should be a positive value.", "status": "failed"})
        pattern = r'^\d{1,2}\'\d{1,2}"$'  # regular exp pattern
        if not re.match(pattern, height):
            raise CustomValidation(
                    {"message": "Height should be in the format '5'4\"'.", "status": "failed"})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        if MatrimonialProfile.objects.filter(user=user).exists():
            raise CustomValidation(
                    {"message": "This user already has a matrimonial profile", "status": "failed"}
            )

        images = validated_data.pop('images')
        profile = MatrimonialProfile.objects.create(user=user, **validated_data)

        matrimonial_images = [
            MatrimonialProfileImage(matrimonial_profile=profile, image=image)
            for image in images
        ]
        MatrimonialProfileImage.objects.bulk_create(matrimonial_images)

        return profile


class MatrimonialProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
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
    sender = serializers.UUIDField(read_only=True)
    receiver = serializers.UUIDField()
    status = serializers.ChoiceField(choices=CONNECTION_CHOICES, read_only=True)
    created = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        sender = user.matrimonial_profile
        receiver_id = validated_data.pop('receiver')
        try:
            receiver = MatrimonialProfile.objects.get(id=receiver_id)
        except MatrimonialProfile.DoesNotExist:
            raise CustomValidation(
                    {"message": "Receiver matrimonial profile doesn't exist", "status": "failed"})
        validated_data['sender'] = sender
        validated_data['receiver'] = receiver
        if ConnectionRequest.objects.filter(sender=sender, receiver=receiver).exists():
            raise CustomValidation({"message": "Connection request already made", "status": "failed"})
        return ConnectionRequest.objects.create(**validated_data)

    # once the method is patch, status field is editable
    def get_fields(self):
        fields = super().get_fields()
        if self.context['request'].method == "PATCH":
            fields['status'].read_only = False
            fields['receiver'].read_only = True
        return fields

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        if instance.status == 'R':
            instance.delete()
            return instance

        if instance.status == 'A':
            # Create a new Conversation instance and add it to ConversationListSerializer
            conversation = Conversation.objects.create(initiator=instance.sender, receiver=instance.receiver)
            conversation_serializer = ConversationListSerializer(conversation)

            instance.delete()
            return conversation_serializer.data
        return instance


class MessageSerializer(serializers.Serializer):
    sender = serializers.UUIDField(source="sender.id", read_only=True)
    text = serializers.CharField()
    attachment = serializers.FileField(allow_empty_file=True, required=False)

    def validate(self, attrs):
        sender = attrs.get('sender')

        try:
            MatrimonialProfile.objects.get(id=sender)
        except MatrimonialProfile.DoesNotExist:
            return CustomValidation(
                    {"message": "Sender matrimonial profile doesn't exist", "status": "failed"})


def validate_profiles(attrs):
    initiator = attrs.get('initiator')
    receiver = attrs.get('receiver')

    try:
        MatrimonialProfile.objects.get(id=initiator)
        MatrimonialProfile.objects.get(id=receiver)
    except MatrimonialProfile.DoesNotExist:
        return CustomValidation(
                {"message": "Initiator or receiver matrimonial profile doesn't exist", "status": "failed"})

    return attrs


class ConversationListSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    initiator = serializers.UUIDField()
    receiver = serializers.UUIDField()
    last_message = serializers.SerializerMethodField()

    @staticmethod
    def get_last_message(obj: Conversation):
        message = obj.messages.first()
        if message is None:
            return ''
        return MessageSerializer(message)

    def validate(self, attrs):
        attrs = validate_profiles(attrs)
        return attrs


class ConversationSerializer(serializers.Serializer):
    initiator = serializers.UUIDField(read_only=True)
    receiver = serializers.UUIDField()
    messages = MessageSerializer(many=True)

    def validate(self, attrs):
        attrs = validate_profiles(attrs)
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        initiator = user.matrimonial_profile
        receiver_id = validated_data.get('receiver')
        try:
            receiver = MatrimonialProfile.objects.get(id=receiver_id)
        except MatrimonialProfile.DoesNotExist:
            raise CustomValidation({"message": "Receiver matrimonial profile doesn't exist", "status": "failed"})

            # Check if a conversation already exists between the initiator and receiver
        existing_conversation = Conversation.objects.filter(
                (Q(initiator=initiator) & Q(receiver=receiver)) |
                (Q(initiator=receiver) & Q(receiver=initiator))
        ).first()

        if existing_conversation:
            raise CustomValidation({"message": "Conversation already exists",
                                    "data": ConversationSerializer(existing_conversation).data, "status": "failed"})

        return Conversation.objects.create(initiator=initiator, receiver=receiver)
