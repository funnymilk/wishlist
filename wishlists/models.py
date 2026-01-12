from django.conf import settings
from django.db import models


class Wishlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlists",
    )
    gifts = models.ManyToManyField(
        "gifts.Gift",
        through="WishlistGift",
        related_name="wishlists",
    )

    def __str__(self) -> str:
        return self.name


class WishlistGift(models.Model):
    wishlist = models.ForeignKey("wishlists.Wishlist", on_delete=models.CASCADE)
    gift = models.ForeignKey("gifts.Gift", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("wishlist", "gift")
