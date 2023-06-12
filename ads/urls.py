from django.urls import path

from ads import views

urlpatterns = [
    path('ads-categories/', views.AdsCategoryView.as_view(), name="ads_and_categories")
]