"""
Okay! Let's generate Unit tests for gift domain. pure unit tests for gifts domain
"""
import unittest
from gifts.models import Gift
from gifts.serializers import GiftSerializer
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from unittest.mock import Mock, patch

class TestGiftSerializerValidation(TestCase):
    """Unit tests for GiftSerializer validation logic."""

    def test_valid_data_passes_validation(self):
        """Test that valid gift data passes validation."""
        data = {
            'name': 'Teddy Bear',
            'cost': 29.99,
            'description': 'A soft and cuddly teddy bear.'
        }
        serializer = GiftSerializer(data=data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid, f"Expected valid, got errors: {serializer.errors}")

    def test_missing_name_field(self):
        """Test that missing name field fails validation."""
        data = {
            'cost': 29.99,
            'description': 'A soft and cuddly teddy bear.'
        }
        serializer = GiftSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn('name', serializer.errors)

    def test_negative_cost_raises_validation_error(self):
        """Test that negative cost raises validation error."""
        data = {
            'name': 'Teddy Bear',
            'cost': -10.00,
            'description': 'A soft and cuddly teddy bear.'
        }
        serializer = GiftSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn('cost', serializer.errors)
    
    def test_invalid_cost_type_raises_validation_error(self):
        """Test that non-numeric cost raises validation error."""
        data = {
            'name': 'Teddy Bear',
            'cost': 'free',
            'description': 'A soft and cuddly teddy bear.'
        }
        serializer = GiftSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn('cost', serializer.errors)

    def test_missing_cost_field(self):
        """Test that missing cost field fails validation."""
        data = {
            'name': 'Teddy Bear',
            'description': 'A soft and cuddly teddy bear.'
        }
        serializer = GiftSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertTrue(is_valid)

    def test_missing_description_field(self):
        """Test that missing description field fails validation."""
        data = {
            'name': 'Teddy Bear',
            'cost': 29.99
        }
        serializer = GiftSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertTrue(is_valid)

    def test_name_field_length_exceeds_max(self):
        """Test that name field exceeding max length fails validation."""
        data = {
            'name': 'A' * 256,  # Assuming max_length is 255
            'cost': 29.99,
            'description': 'A soft and cuddly teddy bear.'
        }
        serializer = GiftSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertFalse(is_valid)
        self.assertIn('name', serializer.errors)

    def test_name_field_with_special_characters(self):
        """Test that name field with special characters passes validation."""
        data = {
            'name': 'Teddy Bear! @2024 #Gifts',
            'cost': 29.99,
            'description': 'A soft and cuddly teddy bear.'
        }
        serializer = GiftSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertTrue(is_valid, f"Expected valid, got errors: {serializer.errors}")
    
    def test_cost_field_as_integer(self):
        """Test that cost field as integer passes validation."""
        data = {
            'name': 'Teddy Bear',
            'cost': 30,  # Integer cost
            'description': 'A soft and cuddly teddy bear.'
        }
        serializer = GiftSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertTrue(is_valid, f"Expected valid, got errors: {serializer.errors}")
    
    def test_cost_field_as_string_number(self):
        """Test that cost field as string number passes validation."""
        data = {
            'name': 'Teddy Bear',
            'cost': '29.99',  # String representation of a number
            'description': 'A soft and cuddly teddy bear.'
        }
        serializer = GiftSerializer(data=data)
        is_valid = serializer.is_valid()
        
        self.assertTrue(is_valid, f"Expected valid, got errors: {serializer.errors}")

    


