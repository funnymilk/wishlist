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
from wishlists.services import add_gift_to_wishlist, create_and_add_gift_to_wishlist

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
        result = add_gift_to_wishlist(
            user=request.user,
            wishlist=wishlist,
            gift_id=int(gift_id)
        )

        return Response(WishlistGiftSerializer(result.wishlist_gift).data, status=status.HTTP_201_CREATED)

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

        result = create_and_add_gift_to_wishlist(
            user=request.user,
            wishlist=wishlist,
            gift_data=serializer.validated_data
        )
        return Response(WishlistGiftSerializer(result.wishlist_gift).data, status=status.HTTP_201_CREATED)