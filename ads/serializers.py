from django.core.validators import MinValueValidator
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from ads.models import Ad


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
    sub_category = serializers.UUIDField(required=False)
    featured = serializers.BooleanField()
    images = serializers.ListField(child=serializers.ImageField(), required=False, max_length=3)