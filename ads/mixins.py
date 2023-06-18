from ads.models import Ad


class AdsByCategoryMixin:
    @staticmethod
    def get_ads_by_category(category):
        return Ad.objects.select_related('category', 'sub_category').filter(category=category, is_active=True)
