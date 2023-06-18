from urllib.parse import urlencode

from django.contrib import admin
from django.contrib.admin import TabularInline
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ads.models import Ad, AdCategory, AdImage, AdSubCategory


# Register your models here.

class AdImageAdmin(TabularInline):
    model = AdImage
    extra = 2
    max_num = 3


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    inlines = (AdImageAdmin,)
    list_display = ('name', 'ad_creator', 'price', 'category', 'location', 'featured')
    list_filter = ('name', 'price', 'category', 'location')
    list_per_page = 20
    ordering = ('name', 'category', 'ad_creator')
    search_fields = ('title', 'category__title')


class AdSubCategoryAdmin(TabularInline):
    model = AdSubCategory
    extra = 1


@admin.register(AdCategory)
class AdCategoryAdmin(admin.ModelAdmin):
    inlines = (AdSubCategoryAdmin,)
    list_display = ('title', 'ads_count', 'sub_categories_count',)
    list_filter = ('title',)
    list_per_page = 20
    ordering = ('title',)
    readonly_fields = ('ad_category_image',)
    search_fields = ('title',)

    @staticmethod
    def ad_category_image(obj: AdCategory):
        category_image = obj.category_image
        html = ''
        html += '<img src="{url}" width="{width}" height="{height}" />'.format(
                url=category_image,
                width=120,
                height=100,
        )
        return mark_safe(html)

    @admin.display(ordering="ads_count")
    def ads_count(self, category):
        url = (reverse("admin:ads_ad_changelist")
               + "?"
               + urlencode({"category__id": str(category.id)})
               )

        return format_html('<a href="{}">{} Ads</a>', url, category.ads_count)

    @admin.display(ordering="sub_categories_count")
    def sub_categories_count(self, obj):
        return obj.sub_categories_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request).annotate(
                ads_count=Count("ads"),
                sub_categories_count=Count("sub_categories")
        )
        return queryset
