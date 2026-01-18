from rest_framework import serializers
from .models import Wishlist, WishlistGift


class WishlistGiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistGift
        fields = ["id", "wishlist", "gift"]
        read_only_fields = ["id"]


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
