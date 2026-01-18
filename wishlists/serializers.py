from rest_framework import serializers
from .models import Wishlist, WishlistGift
from gifts.serializers import GiftSerializer
from gifts.models import Gift


class WishlistGiftSerializer(serializers.ModelSerializer):
    gift = GiftSerializer(read_only=True)

    class Meta:
        model = WishlistGift
        fields = ["id", "wishlist", "gift"]
        read_only_fields = ["id", "wishlist"]


class CreateGiftForWishlistSerializer(serializers.Serializer):
    """Serializer for creating a new gift to add to a wishlist."""
    name = serializers.CharField(max_length=255, required=True)
    link = serializers.URLField(required=False, allow_blank=True)
    cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    image = serializers.URLField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=Gift.Status.choices,
        required=False,
        default=Gift.Status.AVAILABLE
    )

    def validate_link(self, value):
        """Allow empty string for optional URL field."""
        return value if value else ""

    def validate_image(self, value):
        """Allow empty string for optional URL field."""
        return value if value else ""


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = [
            "id",
            "name",
            "user",
            "gifts",
        ]
        read_only_fields = ["id", "user"]
