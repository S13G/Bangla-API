from django.db.models import Count
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ads.mixins import AdsByCategoryMixin
from ads.models import Ad, AdCategory


# Create your views here.

class AdsCategoryView(AdsByCategoryMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ad_categories = AdCategory.objects.annotate(num_of_ads=Count('ads'))
        featured_ads = Ad.objects.select_related('category') \
            .filter(featured=True) \
            .only('id', 'name', 'category', 'price', 'condition', 'description', 'date_and_time')
        count_featured_ads = featured_ads.count()
        other_ads = []
        for category in ad_categories:
            ads = self.get_ads_by_category(category['category'])
            other_ads.append({
                "category": category['category'],
                "name": category['name'],
                "num_ads": category['num_ads'],
                "ads": ads
            })
        data = {
            "ad_categories": ad_categories,
            "featured_ads": featured_ads,
            "count_featured_ads": count_featured_ads,
            "other_ads": other_ads,
        }
        return Response({"message": "Fetched successfully", "data": data, "status": "success"},
                        status=status.HTTP_200_OK)
