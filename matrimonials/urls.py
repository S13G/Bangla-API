from django.urls import path

from matrimonials import views

urlpatterns = [
    path('connection-requests/', views.ConnectionRequestListCreateView.as_view(), name='connection-request-list'),
    path('connection-requests/<str:connection_request_id>/', views.ConnectionRequestRetrieveUpdateView.as_view(),
         name='connection-request-detail'),
    path('matrimonial-profile/all/', views.RetrieveCreateMatrimonialProfileView.as_view(),
         name="retrieve_all_matrimonial_profile"),
    path('matrimonial-profile/', views.RetrieveCreateMatrimonialProfileView.as_view(),
         name="retrieve_create_matrimonial_profile"),
    path('matrimonial-profile/<str:matrimonial_profile_id>/',
         views.RetrieveOtherUsersMatrimonialProfileView.as_view(),
         name="retrieve_user_matrimonial_profile"),
    path('bookmark/<str:matrimonial_profile_id>/', views.BookmarkUsersMatrimonialProfile.as_view(),
         name="bookmark_matrimonial_profile"),
    path('bookmark/matrimonial_profile/all/', views.BookmarkMatrimonialProfileListView.as_view(),
         name="all_bookmarked_matrimonial_profile"),
    path('matrimonial_profile/filters/', views.FilterMatrimonialProfilesView.as_view(),
         name="matrimonial_profile_filters"),
]
