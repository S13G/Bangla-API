from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from ads.filters import AdFilter
from ads.mixins import AdsByCategoryMixin
from ads.models import Ad, AdCategory, AdImage, FavouriteAd
from ads.serializers import AdCategorySerializer, AdSerializer, CreateAdSerializer


# Create your views here.

class AdsCategoryView(AdsByCategoryMixin, GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdCategorySerializer

    @extend_schema(
            summary="Ads and Categories",
            description=
            """
            Get all active ads and categories including featured ads.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="Ad successfully fetched",
                        response=(AdCategorySerializer, AdSerializer,),
                ),
            }
    )
    def get(self, request):
        ad_categories = AdCategory.objects.all()
        serializer = AdCategorySerializer(ad_categories, many=True)
        featured_ads = Ad.objects.select_related('category', 'sub_category').filter(featured=True, is_active=True)
        serialized_featured_ads = AdSerializer(featured_ads, many=True)
        count_featured_ads = featured_ads.count()
        all_ads_by_category = []
        for category in ad_categories:
            ads = self.get_ads_by_category(category.id)
            num_ads = ads.count()
            all_ads_by_category.append({
                "category": category.id,
                "title": category.title,
                "num_ads": num_ads,
                "ads": AdSerializer(ads, many=True).data
            })
        data = {
            "ad_categories": serializer.data,
            "featured_ads": {
                "ads": serialized_featured_ads.data,
                "count_featured_ads": count_featured_ads,
            },
            "all_ads_by_category": all_ads_by_category,
        }
        return Response({"message": "Fetched successfully", "data": data, "status": "success"},
                        status=status.HTTP_200_OK)


class RetrieveAdView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
            summary="Ad Detail",
            description=
            """
            Get the details of a specific Ad.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="Ad successfully fetched",
                        response=AdSerializer,
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="This ad does not exist, try again",
                ),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                        description="Ad ID is required",
                ),
            }
    )
    def get(self, request, *args, **kwargs):
        ad_id = self.kwargs.get('ad_id')
        if ad_id is None:
            return Response({"message": "Ad ID is required", "status": "success"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            ad = Ad.objects.get(id=ad_id)
        except Ad.DoesNotExist:
            return Response({"message": "Ad with this id does not exist", "status": "failed"},
                            status=status.HTTP_404_NOT_FOUND)
        data = {
            "id": ad.id,
            "ad_creator": ad.ad_creator.full_name,
            "name": ad.name,
            "description": ad.description,
            "price": ad.price,
            "location": ad.location.name,
            "images": [image.image for image in ad.images.all()]
        }
        return Response({"message": "Ad fetched successfully", "data": data}, status=status.HTTP_200_OK)


class FilteredAdsListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdSerializer
    filterset_class = AdFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'description', 'category__name', 'price']
    queryset = Ad.objects.filter(is_active=True)
    throttle_classes = [UserRateThrottle]

    @extend_schema(
            summary="Filtered Ads List",
            description=
            """
            This endpoint retrieves a list of filtered ads.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="Ads filtered successfully.",
                        response=AdSerializer(many=True)
                ),
                status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                        description="Authentication credentials were not provided."
                ),
            },
    )
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.serializer_class(queryset, many=True)
        return Response({"message": "Ads filtered successfully", "data": serializer.data, "status": "success"},
                        status.HTTP_200_OK)


class CreateAdsView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateAdSerializer

    @extend_schema(
            summary="Create a ad",
            description=
            """
            This endpoint allows an authenticated user to create an ad.
            """,
            responses={
                status.HTTP_201_CREATED: OpenApiResponse(
                        description="Ad created successfully",
                ),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                        description="Bad request. Maximum number of allowed images exceeded.",
                ),
            }
    )
    def post(self, request):
        creator = self.request.user
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        images = self.request.FILES.getlist('images')
        if len(images) > 3:
            return Response({"message": "The maximum number of allowed images is 3", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)
        created_ad = Ad.objects.create(ad_creator=creator, **serializer.validated_data)
        for image in images:
            AdImage.objects.create(ad=created_ad, _image=image)
        return Response({"message": "Ad created successfully", "status": "success"}, status.HTTP_201_CREATED)


class RetrieveUserAdsView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
            summary="Get all ads relate to user",
            description=
            """
            Get all ads related to the authenticated user.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="Ad successfully fetched",
                        response=AdSerializer,
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="User has not created any ads",
                ),
            }
    )
    def get(self, request):
        creator = self.request.user
        ads = Ad.objects.filter(ad_creator=creator)
        if not ads.exists():
            return Response({"message": "User has not created any ads", "status": "failed"},
                            status=status.HTTP_404_NOT_FOUND)
        all_user_ads = [
            {
                "created": ad.created,
                "name": ad.name,
                "price": ad.price,
                "image": [image.image for image in ad.images.all()],
                "is_active": ad.is_active
            }.copy()
            for ad in ads
        ]

        return Response({"message": "All user ads fetched successfully", "data": all_user_ads, "status": "success"},
                        status=status.HTTP_200_OK)


class DeleteUserAdView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
            summary="Remove Ad",
            description=
            """
            Remove ad from ads list.
            """,
            responses={
                status.HTTP_204_NO_CONTENT: OpenApiResponse(
                        description="Ad successfully removed",
                        response=AdSerializer,
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="This ad does not exist, try again",
                ),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                        description="Ad ID is required",
                ),
            }
    )
    def delete(self, request):
        ad_id = self.kwargs.get('ad_id')
        if ad_id is None:
            return Response({"message": "Ad ID is required", "status": "success"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            ad = Ad.objects.get(id=ad_id)
        except Ad.DoesNotExist:
            return Response({"message": "Ad with this id does not exist", "status": "failed"},
                            status=status.HTTP_404_NOT_FOUND)
        ad.delete()
        return Response({"message": "Ad removed successfully", "status": "success"}, status=status.HTTP_204_NO_CONTENT)


class FavouriteAdView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
            summary="Add ad to favorites",
            description=
            """
            This endpoint allows an authenticated user to add an ad to their favorites list.
            """,
            responses={
                status.HTTP_201_CREATED: OpenApiResponse(
                        description="Ad added to favorites.",
                ),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                        description="Invalid or missing ad ID.",
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="Ad not found.",
                ),
            }
    )
    def post(self, request, *args, **kwargs):
        customer = self.request.user
        ad_id = self.kwargs.get("ad_id")
        if not ad_id:
            return Response({"message": "Ad id is required", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            ad = Ad.objects.get(id=ad_id)
        except Ad.DoesNotExist:
            return Response({"message": "Invalid ad id", "status": "failed"}, status=status.HTTP_404_NOT_FOUND)

        favourite, created = FavouriteAd.objects.get_or_create(customer=customer, ad=ad)

        if created:
            return Response({"message": "Ad added to favourites", "status": "success"},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Ad already in favourites", "status": "success"}, status=status.HTTP_200_OK)


class FavouriteAdListView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    @extend_schema(
            summary="Retrieves all favorite ads",
            description=
            """
            This endpoint allows an authenticated user to retrieve their favorite ads list.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="All favorite products fetched.",
                        response=AdSerializer(many=True)
                ),
            }
    )
    def get(self, request):
        customer = self.request.user
        if customer is None:
            return Response({"message": "Customer does not exist", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)
        favourite_ads = FavouriteAd.objects.select_related('ad').filter(customer=customer)
        if not favourite_ads.exists():
            return Response({"message": "Customer has no favourite ads", "status": "failed"},
                            status=status.HTTP_404_NOT_FOUND)
        serialized_data = [
            {
                "name": a.ad.name,
                "price": a.ad.price,
                "images": [image.image for image in a.ad.images.all()]
            }.copy()
            for a in favourite_ads
        ]
        return Response({"message": "All favorite products fetched", "data": serialized_data, "status": "success"},
                        status=status.HTTP_200_OK)
