from django.core.validators import MinValueValidator
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from ads.choices import STATUS_CHOICES
from ads.models import Ad, AdCategory
from common.exceptions import CustomValidation


class AdCategorySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    image = serializers.ImageField()


class AdSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    location = CountryField()
    category = AdCategorySerializer
    featured = serializers.BooleanField()
    images = serializers.SerializerMethodField()
    is_approved = serializers.BooleanField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES)

    @staticmethod
    def get_images(obj: Ad):
        images = [image.ad_image for image in obj.images.all()]
        return images


class CreateAdSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    location = CountryField()
    category = serializers.UUIDField()
    images = serializers.ListField(child=serializers.ImageField(), required=False, max_length=3)
    featured = serializers.BooleanField()
    is_approved = serializers.BooleanField()
    status = serializers.ChoiceField(choices=STATUS_CHOICES)

    def get_fields(self):
        fields = super().get_fields()
        if self.context['request'].method != "PATCH":
            fields['status'].read_only = True
            fields['featured'].read_only = True
            fields['is_approved'].read_only = True
        return fields

    @staticmethod
    def validate_name(value):
        if Ad.objects.filter(name=value).exists():
            raise CustomValidation({"message": "An ad with this name already exists.", "status": "failed"})
        return value

    def create(self, validated_data):
        creator = self.context['request'].user
        # Extract the category and from validated_data
        category_id = validated_data.pop('category')

        # Retrieve the AdCategory instance
        try:
            category = AdCategory.objects.get(id=category_id)
        except AdCategory.DoesNotExist:
            raise CustomValidation({"message": "Category does not exist", "status": "failed"})

        # Create and return the new Ad instance
        return Ad.objects.create(ad_creator=creator, category=category, **validated_data)

    def update(self, instance, validated_data):
        category_id = self.validated_data.pop('category', [])
        for field, value in validated_data.items():
            setattr(instance, field, value)
        try:
            category = AdCategory.objects.get(id=category_id)
        except AdCategory.DoesNotExist:
            raise CustomValidation({"message": "Category does not exist", "status": "failed"})
        instance.category = category
        instance.save()
        return instance
