from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from matrimonials.filters import MatrimonialFilter
from matrimonials.models import BookmarkedProfile, ConnectionRequest, Conversation, MatrimonialProfile, \
    MatrimonialProfileImage
from matrimonials.serializers import ConnectionRequestSerializer, ConversationListSerializer, \
    ConversationSerializer, CreateMatrimonialProfileSerializer, \
    MatrimonialProfileSerializer


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


class BookmarkUsersMatrimonialProfile(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
            summary="Add matrimonial profile to bookmarks list",
            description=
            """
            This endpoint allows an authenticated user to bookmark another user's matrimonial profile.
            """,
            responses={
                status.HTTP_201_CREATED: OpenApiResponse(
                        description="Matrimonial profile added to bookmark.",
                ),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                        description="Invalid or missing matrimonial_profile_id.",
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="Matrimonial profile not found.",
                ),
            }
    )
    def post(self, request, *args, **kwargs):
        user = self.request.user
        matrimonial_profile_id = self.kwargs.get("matrimonial_profile_id")
        if not matrimonial_profile_id:
            return Response({"message": "Matrimonial profile id is required", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            matrimonial_profile = MatrimonialProfile.objects.get(id=matrimonial_profile_id)
        except MatrimonialProfile.DoesNotExist:
            return Response({"message": "Invalid ad id", "status": "failed"}, status=status.HTTP_404_NOT_FOUND)

        matrimonial_profile, created = MatrimonialProfile.objects.get_or_create(user=user, profile=matrimonial_profile)

        if created:
            return Response({"message": "Matrimonial profile bookmarked", "status": "success"},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Matrimonial profile already bookmarked", "status": "success"},
                            status=status.HTTP_200_OK)


class BookmarkMatrimonialProfileListView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
            summary="Retrieves all bookmarked matrimonial profile",
            description=
            """
            This endpoint allows an authenticated user to retrieve their bookmarked matrimonial profile.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="All bookmarked profiles fetched",
                ),
            }
    )
    def get(self, request):
        user = self.request.user
        bookmarked_profiles = BookmarkedProfile.objects.select_related('user', 'profile').filter(user=user)
        if not bookmarked_profiles.exists():
            return Response({"message": "Customer has no profile bookmarked", "status": "failed"},
                            status=status.HTTP_404_NOT_FOUND)
        serialized_data = [
            {
                "full_name": bp.profile.full_name,
                "height": bp.profile.height,
                "age": bp.profile.age,
                "religion": bp.profile.religion,
                "city": bp.profile.city,
                "education": bp.profile.education,
                "profession": bp.profile.profession,
                "images": [image.matrimonial_image for image in bp.profile.images.all()]
            }.copy()
            for bp in bookmarked_profiles
        ]
        return Response({"message": "All bookmarked profiles fetched", "data": serialized_data, "status": "success"},
                        status=status.HTTP_200_OK)


class FilterMatrimonialProfilesView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MatrimonialProfileSerializer
    filterset_class = MatrimonialFilter
    filter_backends = [DjangoFilterBackend]
    queryset = MatrimonialProfile.objects.all()

    @extend_schema(
            summary="Matrimonial Profile List",
            description=
            """
            This endpoint retrieves a list of filtered matrimonial profile.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="Matrimonial profile filtered successfully.",
                ),
                status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                        description="Authentication credentials were not provided."
                ),
            },
    )
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serialized_data = [
            {
                "full_name": bp.profile.full_name,
                "height": bp.profile.height,
                "age": bp.profile.age,
                "religion": bp.profile.religion,
                "city": bp.profile.city,
                "education": bp.profile.education,
                "profession": bp.profile.profession,
                "images": [image.matrimonial_image for image in bp.profile.images.all()]
            }.copy()
            for bp in queryset
        ]
        return Response({"message": "Ads filtered successfully", "data": serialized_data, "status": "success"},
                        status.HTTP_200_OK)


class ConnectionRequestListCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ConnectionRequest.objects.all()
    serializer_class = ConnectionRequestSerializer

    @extend_schema(
            summary="Connection Request List",
            description=
            """
            This endpoint retrieves a list of connection requests.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="All connection requests fetched successfully",
                        response=ConnectionRequestSerializer,
                ),
                status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                        description="Authentication credentials were not provided."
                ),
            },
    )
    def get(self, request):
        connections = self.get_queryset()
        serialized_connections = self.serializer_class(connections, many=True)
        return Response({"message": "All connection requests fetched successfully", "data": serialized_connections,
                         "status": "success"}, status=status.HTTP_200_OK)

    @extend_schema(
            summary="Create Connection Request",
            description=
            """
            This endpoint creates connection requests.
            """,
            responses={
                status.HTTP_201_CREATED: OpenApiResponse(
                        description="Connection request created successfully",
                        response=ConnectionRequestSerializer,
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="Matrimonial profile does not exist."
                ),
            },
    )
    def post(self, request):
        user = self.request.user
        try:
            matrimonial_profile = MatrimonialProfile.objects.get(user=user)
        except MatrimonialProfile.DoesNotExist:
            return Response({"message": "Matrimonial profile does not exist", "status": "failed"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=matrimonial_profile)
        return Response({"message": "Connection request created successfully", "status": "success"},
                        status=status.HTTP_201_CREATED)


class ConnectionRequestRetrieveUpdateView(GenericAPIView):
    serializer_class = ConnectionRequestSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
            summary="Updates a Connection Request",
            description=
            """
            This endpoint updates a connection requests.
            """,
            responses={
                status.HTTP_202_ACCEPTED: OpenApiResponse(
                        description="Connection request updated successfully",
                        response=ConnectionRequestSerializer,
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="Connection request does not exist."
                ),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                        description="Connection request id is required."
                ),
            },
    )
    def patch(self, request, *args, **kwargs):
        connection_request_id = self.kwargs.get('connection_request_id')
        if connection_request_id is not None:
            try:
                connection_request = ConnectionRequest.objects.get(id=connection_request_id)
            except ConnectionRequest.DoesNotExist:
                return Response({"message": "Connection request does not exist", "status": "failed"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Connection request id is required", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(connection_request, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
                {"message": "Connection request updated successfully", "data": serializer.data, "status": "failed"},
                status=status.HTTP_202_ACCEPTED)

    @extend_schema(
            summary="Deletes a Connection Request",
            description=
            """
            This endpoint deletes a connection requests.
            """,
            responses={
                status.HTTP_204_NO_CONTENT: OpenApiResponse(
                        description="Connection request deleted successfully",
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="Connection request does not exist."
                ),
                status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                        description="Connection request id is required."
                ),
            },
    )
    def delete(self, request, *args, **kwargs):
        connection_request_id = self.kwargs.get('connection_request_id')
        if connection_request_id is not None:
            try:
                connection_request = ConnectionRequest.objects.get(id=connection_request_id)
            except ConnectionRequest.DoesNotExist:
                return Response({"message": "Connection request does not exist", "status": "failed"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Connection request id is required", "status": "failed"},
                            status=status.HTTP_400_BAD_REQUEST)
        connection_request.delete()
        return Response({"message": "Connection request deleted successfully", "status": "failed"},
                        status=status.HTTP_204_NO_CONTENT)


class ConversationsListView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
            summary="Retrieve a Conversation List",
            description=
            """
            This endpoint retrieve a conversation list.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="Conversation list fetched successfully",
                ),
            },
    )
    def get(self, request):
        conversation_list = Conversation.objects.filter(Q(initiator=self.request.user) |
                                                        Q(receiver=self.request.user))
        serializer = ConversationListSerializer(instance=conversation_list, many=True)
        return Response(
                {"message": "Conversation list fetched successfully", "data": serializer.data, "status": "success"},
                status=status.HTTP_200_OK)


class RetrieveConversationView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    @extend_schema(
            summary="Retrieve a conversation",
            description=
            """
            This endpoint retrieve a conversation.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="Conversation list fetched successfully",
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="Conversation does not exist",
                ),
            },
    )
    def get(self, request, *args, **kwargs):
        convo_id = self.kwargs.get('convo_id')
        conversation = Conversation.objects.filter(id=convo_id)
        if not conversation.exists():
            return Response({"message": "Conversation does not exist", "status": "success"},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = self.serializer_class(instance=conversation[0])
            return Response({"message": "Conversation fetched successfully", "data": serializer.data, "status": "success"},
                            status=status.HTTP_200_OK)


class CreateConversationView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    @extend_schema(
            summary="Create a conversation",
            description=
            """
            This endpoint creates a conversation.
            """,
            responses={
                status.HTTP_200_OK: OpenApiResponse(
                        description="Conversation created successfully",
                        response=ConversationSerializer,
                ),
                status.HTTP_404_NOT_FOUND: OpenApiResponse(
                        description="Matrimonial profile does not exist",
                ),
            },
    )
    def post(self, request, *args, **kwargs):
        participant_id = self.kwargs.get('participant_id')
        try:
            initiator = MatrimonialProfile.objects.get(user=self.request.user)
        except MatrimonialProfile.DoesNotExist:
            return Response({"message": "Matrimonial profile does not exist", "status": "failed"},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            participant = MatrimonialProfile.objects.get(user=participant_id)
        except MatrimonialProfile.DoesNotExist:
            return Response({"message": "You cannot chat with a non existent user", "status": "failed"},
                            status=status.HTTP_404_NOT_FOUND)

        conversation = Conversation.objects.filter(Q(initiator=initiator, receiver=participant) |
                                                   Q(initiator=participant, receiver=initiator))
        if conversation.exists():
            return redirect(reverse('get_conversation', args=(conversation[0].id,)))
        else:
            conversation = Conversation.objects.create(initiator=initiator, receiver=participant)
            serialized_data = ConversationSerializer(conversation).data
            return Response(
                    {"message": "Conversation created successfully", "data": serialized_data, "status": "success"},
                    status=status.HTTP_201_CREATED)
