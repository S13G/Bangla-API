from django.core.validators import MinValueValidator
from django_countries.serializer_fields import CountryField
from rest_framework import serializers

from ads.models import Ad, AdCategory, AdSubCategory


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
    images = serializers.ListField(child=serializers.ImageField(), required=False, max_length=3)

    def validate_name(self, value):
        if Ad.objects.filter(name=value).exists():
            raise serializers.ValidationError({"message": "An ad with this name already exists.", "status": "failed"})
        return value

    def create(self, validated_data):
        creator = self.context['request'].user
        # Extract the category and sub_category from validated_data
        category_id = validated_data.pop('category')
        sub_category_id = validated_data.pop('sub_category', None)

        # Retrieve the AdCategory instance
        try:
            category = AdCategory.objects.get(id=category_id)
        except AdCategory.DoesNotExist:
            raise serializers.ValidationError({"message": "Category does not exist", "status": "failed"})

        # Retrieve the AdSubCategory instance if sub_category_id is provided
        sub_category = None
        if sub_category_id:
            try:
                sub_category = category.sub_categories.get(id=sub_category_id)
            except AdSubCategory.DoesNotExist:
                raise serializers.ValidationError(
                        {"message": "Sub category for this category does not exist", "status": "failed"})

        # Create and return the new Ad instance
        return Ad.objects.create(ad_creator=creator, category=category, sub_category=sub_category, **validated_data)
