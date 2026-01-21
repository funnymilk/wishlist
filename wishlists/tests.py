import unittest
from gifts.models import Gift
from wishlists.models import Wishlist, WishlistGift
from wishlists.serializers import WishlistSerializer, WishlistGiftSerializer, CreateGiftForWishlistSerializer
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model
from wishlists.services import add_gift_to_wishlist, create_and_add_gift_to_wishlist

User = get_user_model()

class WishlistSerializersTestCase(TestCase):

    def setUp(self):
        # Create a user for testing        
        self.user = User.objects.create_user(email='testuser', password='testpass')

        # Create a wishlist for testing
        self.wishlist = Wishlist.objects.create(name='Test Wishlist', user=self.user)

    def test_wishlist_gift_serializes_nested_gift(self):
        gift = Gift.objects.create(user_id=self.user.id, name='Test Gift', link='http://example.com', image='http://example.com/image.jpg', status=Gift.Status.AVAILABLE)
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
        
        gift = Gift.objects.create(user_id=self.user.id, name='Test Gift', link='http://example.com', image='http://example.com/image.jpg', status=Gift.Status.AVAILABLE)
        WishlistGift.objects.create(wishlist=self.wishlist, gift=gift)
        serializer = WishlistSerializer(self.wishlist)
        data = serializer.data
        self.assertIn('gifts', data)
        self.assertEqual(len(data['gifts']), 1)
        self.assertEqual(data["gifts"][0], gift.id)


class TestWishlistServices(TestCase):

    def setUp(self):
        # Create a user for testing        
        self.user = User.objects.create_user(email='testuser', password='testpass')

        # Create a wishlist for testing
        self.wishlist = Wishlist.objects.create(name='Test Wishlist', user=self.user)

    @patch("wishlists.services.WishlistGift")
    @patch('wishlists.services.Gift')
    def test_create_and_add_gift_to_wishlist_creates_gift(self, MockGift, MockWishlistGift):
        gift_data = {
            'name': 'New Gift',
            'link': 'http://example.com',
            'cost': 20.0,
            'image': 'http://example.com/image.jpg',
            'status': Gift.Status.AVAILABLE
        }

        mock_gift_instance = Mock()
        MockGift.objects.create.return_value = mock_gift_instance

        MockWishlistGift.objects.filter.return_value.exists.return_value = False
        MockWishlistGift.objects.create.return_value = Mock()

        result = create_and_add_gift_to_wishlist(
            user=self.user,
            wishlist=self.wishlist,
            gift_data=gift_data
        )

        MockGift.objects.create.assert_called_once_with(user=self.user, **gift_data)
        self.assertEqual(result.gift, mock_gift_instance)
        self.assertEqual(result.wishlist_gift, MockWishlistGift.objects.create.return_value)

    @patch('wishlists.services.WishlistGift')
    def test_create_gift_to_wishlist_raises_if_gift_already_in_wishlist(self, MockWishlistGift):
        gift_data = {
            'name': 'Existing Gift',
            'link': 'http://example.com',
            'cost': 20.0,
            'image': 'http://example.com/image.jpg',
            'status': Gift.Status.AVAILABLE
        }

        mock_gift_instance = Mock()
        mock_gift_instance.id = 1

        with patch('wishlists.services.Gift.objects.create', return_value=mock_gift_instance):
            MockWishlistGift.objects.filter.return_value.exists.return_value = True

            with self.assertRaises(ValidationError) as context:
                create_and_add_gift_to_wishlist(
                    user=self.user,
                    wishlist=self.wishlist,
                    gift_data=gift_data
                )

            self.assertEqual(str(context.exception.detail[0]), "Gift already in this wishlist.")
        MockWishlistGift.objects.filter.assert_called_once_with(wishlist=self.wishlist, gift=mock_gift_instance)

    @patch('wishlists.services.WishlistGift')
    def test_add_gift_to_wishlist(self, MockWishlistGift):
        mock_gift_instance = Mock()
        mock_gift_instance.id = 1

        with patch('wishlists.services.Gift.objects.get', return_value=mock_gift_instance):
            MockWishlistGift.objects.filter.return_value.exists.return_value = False
            mock_wishlist_gift_instance = Mock()
            MockWishlistGift.objects.create.return_value = mock_wishlist_gift_instance

            result = add_gift_to_wishlist(
                user=self.user,
                wishlist=self.wishlist,
                gift_id=mock_gift_instance.id
            )

        self.assertEqual(result.gift, mock_gift_instance)
        self.assertEqual(result.wishlist_gift, mock_wishlist_gift_instance)
        MockWishlistGift.objects.filter.assert_called_once_with(wishlist=self.wishlist, gift=mock_gift_instance)
        MockWishlistGift.objects.create.assert_called_once_with(wishlist=self.wishlist, gift=mock_gift_instance)

    @patch('wishlists.services.WishlistGift')
    def test_add_gift_to_wishlist_raises_if_gift_already_in_wishlist(self, MockWishlistGift):
        mock_gift_instance = Mock()
        mock_gift_instance.id = 1

        with patch('wishlists.services.Gift.objects.get', return_value=mock_gift_instance):
            MockWishlistGift.objects.filter.return_value.exists.return_value = True

            with self.assertRaises(ValidationError) as context:
                add_gift_to_wishlist(
                    user=self.user,
                    wishlist=self.wishlist,
                    gift_id=mock_gift_instance.id
                )

            self.assertEqual(str(context.exception.detail[0]), "Gift already in this wishlist.")
        MockWishlistGift.objects.filter.assert_called_once_with(wishlist=self.wishlist, gift=mock_gift_instance)

    def test_ensure_wishlist_ownership_raises_for_different_user(self):
        other_user = User.objects.create_user(email='otheruser', password='otherpass')
        with self.assertRaises(ValidationError) as context:
            from wishlists.services import _ensure_wishlist_ownership
            _ensure_wishlist_ownership(self.wishlist, other_user)
        self.assertEqual(str(context.exception.detail[0]), "You do not have permission to modify this wishlist.")

    def test_gift_not_found_raises(self):
        with patch('wishlists.services.Gift.objects.get', side_effect=Gift.DoesNotExist):
            with self.assertRaises(Exception) as context:
                add_gift_to_wishlist(
                    user=self.user,
                    wishlist=self.wishlist,
                    gift_id=999
                )
            self.assertEqual(str(context.exception), "Gift not found.")


