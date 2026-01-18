from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Wishlist, WishlistGift
from .serializers import (
    WishlistSerializer,
    WishlistGiftSerializer,
    CreateGiftForWishlistSerializer,
)
from gifts.models import Gift


class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='gifts')
    def add_gift(self, request, pk=None):
        """
        Add a gift to a wishlist.
        Expects a POST request with 'gift_id' in the request body.
        """
        wishlist = self.get_object()
        gift_id = request.data.get('gift_id')

        if not gift_id:
            return Response(
                {'error': 'gift_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            gift = Gift.objects.get(id=gift_id)
        except Gift.DoesNotExist:
            return Response(
                {'error': 'Gift not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if gift already in wishlist
        if wishlist.gifts.filter(id=gift_id).exists():
            return Response(
                {'error': 'Gift already in this wishlist'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the relationship
        wishlist_gift = WishlistGift.objects.create(
            wishlist=wishlist,
            gift=gift
        )

        serializer = WishlistGiftSerializer(wishlist_gift)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='gifts/new')
    def create_gift(self, request, pk=None):
        """
        Create a new gift and add it to the wishlist.
        Expects a POST request with gift details (name, link, cost, image).
        """
        wishlist = self.get_object()

        # Validate and serialize the input
        serializer = CreateGiftForWishlistSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create the gift for the authenticated user
        gift = Gift.objects.create(
            user=request.user,
            **serializer.validated_data
        )

        # Create the wishlist-gift relationship
        wishlist_gift = WishlistGift.objects.create(
            wishlist=wishlist,
            gift=gift
        )

        # Return the created gift with wishlist relationship
        response_serializer = WishlistGiftSerializer(wishlist_gift)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
