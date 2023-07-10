from django.urls import path

from ads import views

urlpatterns = [
    path('all/', views.RetrieveAllApprovedActiveAdsView.as_view(), name="all_ads"),
    path('ads-categories/', views.AdsCategoryView.as_view(), name="ads_and_categories"),
    path('ad/<str:ad_id>/details/', views.RetrieveAdView.as_view(), name="ad_details"),
    path('ad/<str:ad_id>/delete/', views.DeleteUserAdView.as_view(), name="delete_ad"),
    path('ad/<str:ad_id>/update/', views.UpdateUserAdView.as_view(), name="update_ad"),
    path("ads/search-filters/", views.FilteredAdsListView.as_view(), name="ads_search_and_filters"),
    path("ads/add/", views.CreateAdsView.as_view(), name="create_ads"),
    path('categories/sub-categories/', views.RetrieveAllCategoriesAndSubcategories.as_view(),
         name="categories_and_sub_categories"),
    path("creator/ads/all/", views.RetrieveUserAdsView.as_view(), name="all_creator_ads"),
    path("favourite-ads/<str:ad_id>/add/", views.FavouriteAdView.as_view(), name="add_favourite_ad"),
    path("favourite-ads/", views.FavouriteAdListView.as_view(), name="favourite_ads_list"),
]
