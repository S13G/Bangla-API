from django.contrib import admin

from matrimonials.models import MatrimonialProfile


# Register your models here.
@admin.register(MatrimonialProfile)
class MatrimonialProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'country', 'city', 'religion', 'income',)
    list_filter = ('gender', 'country', 'city', 'religion', 'profession',)
    list_per_page = 20
    ordering = ('gender', 'religion',)
    search_fields = ('full_name', 'country',)
