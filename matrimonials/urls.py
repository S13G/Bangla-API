from django.urls import path

from matrimonials import views

urlpatterns = [
    path('matrimonial-profile/all/', views.RetrieveCreateMatrimonialProfileView.as_view(),
         name="retrieve_all_matrimonial_profile"),
    path('matrimonial-profile/', views.RetrieveCreateMatrimonialProfileView.as_view(),
         name="retrieve_create_matrimonial_profile"),
    path('/matrimonial-profile/<str:matrimonial_profile_id>/',
         views.RetrieveOtherUsersMatrimonialProfileView.as_view(),
         name="retrieve_user_matrimonial_profile")
]
