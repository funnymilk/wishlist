import unittest
from unittest.mock import Mock, patch
from django.db import IntegrityError
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from ...serializers import UserRegistrationSerializer, UserLoginSerializer
from ...models import User


class TestUserRegistrationSerializerValidation(TestCase):
    """Unit tests for UserRegistrationSerializer validation logic."""

    def test_valid_data_passes_validation(self):
        """Test that valid registration data passes validation."""
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid, f"Expected valid, got errors: {serializer.errors}")

    def test_password_mismatch_raises_validation_error(self):
        """Test that mismatched passwords raise validation error."""
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password2': 'wrongpass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn('password', serializer.errors)

    def test_missing_password_field(self):
        """Test that missing password field fails validation."""
        data = {
            'email': 'newuser@example.com',
            'password2': 'testpass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)

    def test_missing_password2_field(self):
        """Test that missing password2 field fails validation."""
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)

    def test_missing_email_field(self):
        """Test that missing email field fails validation."""
        data = {
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)

    def test_invalid_email_format(self):
        """Test that invalid email format fails validation."""
        data = {
            'email': 'invalidemail',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn('email', serializer.errors)

    def test_empty_email(self):
        """Test that empty email fails validation."""
        data = {
            'email': '',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)

    def test_empty_password(self):
        """Test that empty password fails validation."""
        data = {
            'email': 'newuser@example.com',
            'password': '',
            'password2': ''
        }
        serializer = UserRegistrationSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)

    def test_create_user_from_serializer(self):
        """Test that serializer creates user correctly."""
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())


class TestUserLoginSerializerValidation(TestCase):
    """Unit tests for UserLoginSerializer validation logic."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_missing_email_field(self):
        """Test that missing email field fails validation."""
        data = {
            'password': 'testpass123'
        }
        serializer = UserLoginSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn('email', serializer.errors)

    def test_missing_password_field(self):
        """Test that missing password field fails validation."""
        data = {
            'email': 'test@example.com'
        }
        serializer = UserLoginSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn('password', serializer.errors)

    def test_invalid_email_format(self):
        """Test that invalid email format fails validation."""
        data = {
            'email': 'invalidemail',
            'password': 'testpass123'
        }
        serializer = UserLoginSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn('email', serializer.errors)

    def test_empty_email(self):
        """Test that empty email fails validation."""
        data = {
            'email': '',
            'password': 'testpass123'
        }
        serializer = UserLoginSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)

    def test_empty_password(self):
        """Test that empty password fails validation."""
        data = {
            'email': 'test@example.com',
            'password': ''
        }
        serializer = UserLoginSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)

    def test_invalid_credentials_rejected(self):
        """Test that invalid credentials are rejected."""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        serializer = UserLoginSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)

    def test_valid_credentials_accepted(self):
        """Test that valid credentials are accepted."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        serializer = UserLoginSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertTrue(is_valid)
        self.assertEqual(serializer.validated_data['user'].email, 'test@example.com')

    def test_nonexistent_user_login(self):
        """Test that login fails for nonexistent user."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        serializer = UserLoginSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)

class TestUserManager(TestCase):
    """Unit tests for UserManager methods."""

    def test_create_user_successful(self):
        """Test successful user creation."""
        email = 'newuser@example.com'
        password = 'testpass123'
        user = User.objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_without_email(self):
        """Test that creating a user without an email raises an error."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password='testpass123')

    def test_create_user_without_password(self):
        """Test that creating a user without an password raises an error."""
        user = User.objects.create_user(email='newuser@example.com', password=None)
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.email, 'newuser@example.com')

    def test_create_user_double_email(self):
        """Test that creating a user with duplicate email raises an error."""
        email = 'newuser@example.com'
        User.objects.create_user(email=email, password='testpass123')
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email=email, password='testpass123')

    def test_create_superuser_successful(self):
        """Test successful superuser creation."""
        email = 'superuser@example.com'
        password = 'superpass123'
        superuser = User.objects.create_superuser(email=email, password=password)
        self.assertEqual(superuser.email, email)
        self.assertTrue(superuser.check_password(password))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_without_is_staff(self):
        """Test that creating a superuser without is_staff=True raises an error."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='superuser@example.com', password='superpass123', is_staff=False)

    def test_create_superuser_without_is_superuser(self):
        """Test that creating a superuser without is_superuser=True raises an error."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='superuser@example.com', password='superpass123', is_superuser=False)

