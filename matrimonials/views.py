from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from matrimonials.models import MatrimonialProfile, MatrimonialProfileImage
from matrimonials.serializers import CreateMatrimonialProfileSerializer, MatrimonialProfileSerializer


class RetrieveAllMatrimonialProfilesView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
            summary="Get all matrimonial profile",
            description=
            """
            This endpoint allows an authenticated user to retrieve all matrimonial profile.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="All Matrimonial Profile retrieved successfully",
                        response=MatrimonialProfileSerializer
                ),
            }
    )
    def get(self, request):
        all_matrimonial_profiles = MatrimonialProfile.objects.all()
        data = [
            {
                "full_name": profile.full_name,
                "religion": profile.religion,
                "city": profile.city,
                "education": profile.education,
                "profession": profile.profession,
                "age": profile.age,
                "height": profile.height,
                "images": [image.matrimonial_image for image in profile.images.all()]
            }.copy()
            for profile in all_matrimonial_profiles
        ]
        return Response(
                {"message": "All matrimonial profiles fetched", "data": data, "status": "success"},
                status=status.HTTP_200_OK)


class RetrieveCreateMatrimonialProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateMatrimonialProfileSerializer

    @extend_schema(
            summary="Get matrimonial profile",
            description=
            """
            This endpoint allows an authenticated user to retrieve his/her matrimonial profile.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="Matrimonial Profile retrieved successfully",
                        response=MatrimonialProfileSerializer
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="User does not have matrimonial profile.",
                ),
            }
    )
    def get(self, request):
        user = self.request.user
        try:
            user_matrimonial_profile = MatrimonialProfile.objects.get(user=user)
        except MatrimonialProfile.DoesNotExist:
            return Response({"message": "User does not have matrimonial profile", "status": "failed"},
                            status=status.HTTP_404_NOT_FOUND)
        serialized_data = MatrimonialProfileSerializer(user_matrimonial_profile).data
        return Response(
                {"message": "Matrimonial profile fetched successfully", "data": serialized_data, "status": "success"},
                status=status.HTTP_200_OK)

    @extend_schema(
            summary="Create a matrimonial profile",
            description=
            """
            This endpoint allows an authenticated user to create a matrimonial profile.
            """,
            request=CreateMatrimonialProfileSerializer,
            responses={
                status.HTTP_201_CREATED: OpenApiResponse(
                        description="Matrimonial Profile created successfully",
                        response=MatrimonialProfileSerializer
                ),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                        description="Bad request. Maximum number of allowed images exceeded.",
                ),
            }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        images = self.request.FILES.getlist('images')
        if len(images) > 6:
            return Response({"message": "The maximum number of allowed images is 6", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)
        created_profile = serializer.save()
        serialized_data = MatrimonialProfileSerializer(created_profile).data
        matrimonial_images = [MatrimonialProfileImage(matrimonial_profile=created_profile, _image=image) for image in
                              images]
        MatrimonialProfileImage.objects.bulk_create(matrimonial_images)
        return Response(
                {"message": "Matrimonial profile created successfully", "data": serialized_data, "status": "success"},
                status=status.HTTP_201_CREATED)


class RetrieveOtherUsersMatrimonialProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MatrimonialProfileSerializer

    @extend_schema(
            summary="Get another user matrimonial profile",
            description=
            """
            This endpoint allows an authenticated user to retrieve another user's matrimonial profile.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="Matrimonial Profile retrieved successfully",
                        response=MatrimonialProfileSerializer
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="User does not have matrimonial profile.",
                ),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                        description="Matrimonial Profile ID is required."
                )
            }
    )
    def get(self, request, *args, **kwargs):
        matrimonial_profile_id = self.kwargs.get('matrimonial_profile_id')
        if matrimonial_profile_id is not None:
            try:
                matrimonial_profile = MatrimonialProfile.objects.get(id=matrimonial_profile_id)
            except MatrimonialProfile.DoesNotExist:
                return Response({"message": "Matrimonial profile does not exist", "status": "failed"},
                                status=status.HTTP_404_NOT_FOUND)
            serialized_profile = MatrimonialProfileSerializer(matrimonial_profile).data
            return Response({"message": "Matrimonial profile retrieved successfully", "data": serialized_profile,
                             "status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Matrimonial Profile ID is required", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)
