""" Integration tests for user registration and login. """
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from users.serializers import UserRegistrationSerializer, UserLoginSerializer

class UserIntegrationTests(APITestCase):
    def setUp(self):
        self.registration_url = reverse("register")
        self.login_url = reverse("login")

    def test_user_registration(self):
        """ Test user registration endpoint. """
        data = {
            'email': 'example@test.ru',
            'password': 'strongpassword123',
            'password2': 'strongpassword123'
        }
        response = self.client.post(self.registration_url, data, format='json')
        user = User.objects.get(email=data["email"])

        self.assertTrue(user.check_password(data["password"]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=data['email']).exists())
        self.assertEqual(response.data['email'], data['email']) 
        self.assertIn('id', response.data)
        self.assertNotIn('password', response.data)
        self.assertNotIn('password2', response.data)
        
    def test_password_mismatch(self):
        """ Test registration with mismatched passwords. """
        data = {
            'email': 'example@test.ru',
            'password': 'strongpassword123',
            'password2': 'differentpassword123'
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=data['email']).exists()) 

    def test_duplicate_email_registration(self):
        """ Test registration with an already registered email. """
        User.objects.create_user(
            email='example@test.ru',
            password='strongpassword123'
        )
        data = {
            'email': 'example@test.ru',
            'password': 'anotherpassword123',
            'password2': 'anotherpassword123'
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(email='example@test.ru').exists())
        self.assertIn("email", response.data)

    def test_user_login(self):
        """ Test user login endpoint. """
        User.objects.create_user(
            email='example@test.ru',
            password='strongpassword123'
        )
        data = {
            'email': 'example@test.ru',
            'password': 'strongpassword123'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sessionid", response.cookies)
    
    def test_invalid_password_login(self):
        User.objects.create_user(
            email='example@test.ru',
            password='strongpassword123'
        )
        data = {
            'email': 'example@test.ru',
            'password': 'strongpasswor'
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(email='example@test.ru').exists())
        self.assertIn("Invalid email or password", str(response.data))

    def test_invalid_email_login(self):
        User.objects.create_user(
            email='example@test.ru',
            password='strongpassword123'
        )
        data = {
            'email': 'example12@test.ru',
            'password': 'strongpasswor'
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(email='example@test.ru').exists())
        self.assertIn("Invalid email or password", str(response.data))