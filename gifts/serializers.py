from rest_framework import serializers
from .models import Gift


class GiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gift
        fields = [
            "id",
            "name",
            "link",
            "cost",
            "image",
            "status",
            "user",
        ]
        read_only_fields = ["id", "user"]