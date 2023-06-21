from django.core.validators import MinValueValidator
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from ads.models import Ad, AdCategory
from common.exceptions import CustomValidation


class AdCategorySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    _image = serializers.ImageField()


class AdSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    location = CountryField()
    category = AdCategorySerializer
    featured = serializers.BooleanField()
    images = serializers.SerializerMethodField()

    @staticmethod
    def get_images(obj: Ad):
        images = [image.image for image in obj.images.all()]
        return images


class CreateAdSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    location = CountryField()
    category = serializers.UUIDField()
    images = serializers.ListField(child=serializers.ImageField(), required=False, max_length=3)

    def validate_name(self, value):
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
