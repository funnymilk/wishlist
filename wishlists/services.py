# wishlists/services.py
from dataclasses import dataclass
from typing import Optional

from wishlists.models import Wishlist, WishlistGift
from gifts.models import Gift

from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound

@dataclass(frozen=True)
class WishListGiftResult:
    wishlist_gift: WishlistGift
    gift: Gift
    created_gift: bool


def _ensure_wishlist_ownership(wishlist: Wishlist, user) -> None:
    if wishlist.user != user:
        raise ValidationError("You do not have permission to modify this wishlist.")
    
@transaction.atomic
def add_gift_to_wishlist(*, user, wishlist: Wishlist, gift_id: int, gift_data: Optional[dict] = None) -> WishListGiftResult:

    _ensure_wishlist_ownership(wishlist, user)

    try: 
        gift = Gift.objects.get(id=gift_id) 
    except Gift.DoesNotExist:
        raise NotFound("Gift not found.")
    
    if WishlistGift.objects.filter(wishlist=wishlist, gift=gift).exists():
        raise ValidationError("Gift already in this wishlist.")
    
    wishlist_gift = WishlistGift.objects.create(
        wishlist=wishlist,
        gift=gift
    )
    return WishListGiftResult(
        wishlist_gift=wishlist_gift,
        gift=gift,
        created_gift=False
    )

@transaction.atomic
def create_and_add_gift_to_wishlist(*, user, wishlist: Wishlist, gift_data: dict) -> WishListGiftResult:
    _ensure_wishlist_ownership(wishlist, user)

    gift = Gift.objects.create(user=user, **gift_data)

    if WishlistGift.objects.filter(wishlist=wishlist, gift=gift).exists():
        raise ValidationError("Gift already in this wishlist.")

    wishlist_gift = WishlistGift.objects.create(
        wishlist=wishlist,
        gift=gift
    )
    return WishListGiftResult(
        wishlist_gift=wishlist_gift,
        gift=gift,
        created_gift=True
    )

