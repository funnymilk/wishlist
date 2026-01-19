"""

Write Django unit tests (django.test.TestCase) for wishlists serializers.
IMPORTANT RULES:
- Do NOT test Meta.fields or serializer.fields.keys().
- Do NOT assert "field exists" only. Test BEHAVIOR and OUTPUT.
- Use real DB objects (create User, Wishlist, Gift, WishlistGift) in test database.
- No APIClient, no reverse, no HTTP calls (not integration).
- Prefer minimal test data.

Serializers to test:
- WishlistGiftSerializer: gift is nested GiftSerializer(read_only=True). Verify output contains nested gift dict with correct id and name.
- CreateGiftForWishlistSerializer: validate_link and validate_image should return "" when given empty string or None; status defaults to Gift.Status.AVAILABLE; cost can be None.
- WishlistSerializer: gifts representation should be empty list when no gifts; after creating WishlistGift relation, gifts output should include the gift (id or nested object depending on serializer behavior).

Create tests:
1) test_wishlist_gift_serializes_nested_gift
2) test_create_gift_serializer_empty_link_becomes_empty_string
3) test_create_gift_serializer_empty_image_becomes_empty_string
4) test_wishlist_serializer_gifts_empty_list_when_no_relations
5) test_wishlist_serializer_gifts_contains_gift_after_relation

"""


import unittest
from gifts.models import Gift
from wishlists.models import Wishlist, WishlistGift
from wishlists.serializers import WishlistSerializer, WishlistGiftSerializer, CreateGiftForWishlistSerializer
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model

User = get_user_model()

class WishlistSerializersTestCase(TestCase):

    def setUp(self):
        # Create a user for testing        
        self.user = User.objects.create_user(email='testuser', password='testpass')

        # Create a wishlist for testing
        self.wishlist = Wishlist.objects.create(name='Test Wishlist', user=self.user)

    def test_wishlist_gift_serializes_nested_gift(self):
        gift = Gift.objects.create(user_id=1, name='Test Gift', link='http://example.com', image='http://example.com/image.jpg', status=Gift.Status.AVAILABLE)
        wishlist_gift = WishlistGift.objects.create(wishlist=self.wishlist, gift=gift)

        serializer = WishlistGiftSerializer(wishlist_gift)
        data = serializer.data

        self.assertIn('gift', data)
        self.assertEqual(data['gift']['id'], gift.id)
        self.assertEqual(data['gift']['name'], gift.name)

    def test_create_gift_serializer_empty_link_becomes_empty_string(self):
        serializer = CreateGiftForWishlistSerializer(data={
            'name': 'Test Gift',
            'link': None,
            'image': 'http://example.com/image.jpg',
            'status': Gift.Status.AVAILABLE,
            'cost': 10.0
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['link'], '')

    def test_create_gift_serializer_empty_image_becomes_empty_string(self):
        serializer = CreateGiftForWishlistSerializer(data={
            'name': 'Test Gift',
            'link': 'http://example.com',
            'image': '',
            'status': Gift.Status.AVAILABLE,
            'cost': 10.0
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['image'], '')

    def test_wishlist_serializer_gifts_empty_list_when_no_relations(self):
        serializer = WishlistSerializer(self.wishlist)
        data = serializer.data

        self.assertIn('gifts', data)
        self.assertEqual(data['gifts'], [])

    def test_wishlist_serializer_gifts_contains_gift_after_relation(self):
        
        gift = Gift.objects.create(user_id=1, name='Test Gift', link='http://example.com', image='http://example.com/image.jpg', status=Gift.Status.AVAILABLE)
        WishlistGift.objects.create(wishlist=self.wishlist, gift=gift)