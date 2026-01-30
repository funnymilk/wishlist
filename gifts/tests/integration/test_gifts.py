""" Integration tests for gift. Create"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from gifts.models import Gift

class GiftIntegrationTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='example@test.ru',
            password='strongpassword123'
        )
        
        self.user2 = User.objects.create_user(
            email='example2@test.ru',
            password='strongpassword123'
        )

        self.gifts_url = reverse("gift-list")
        

    def test_create_gift_as_user1(self):
        """ Test creating a gift as user1. """
        self.client.force_authenticate(user=self.user1)

        data = {
            'name': 'New Gift',
            'description': 'This is a new gift',
            'link': 'http://example.com/gift',
            'image': 'http://example.com/image.jpg',
            'cost': '29.99'
        }
        response = self.client.post(self.gifts_url, data, format='json')
        gift_id = response.data["id"]
        gift = Gift.objects.get(id=gift_id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # проверяем ответ успешный и статус
        self.assertEqual(gift.name, data["name"]) # чек что у подарка правильное имя        
        self.assertEqual(gift.user, self.user1) #чек что подарок привязан к юзеру1

    def test_list_isolate_gifts_per_user(self):
        """ Test that users can only see their own gifts. """
        Gift.objects.create(
            name='User1 Gift',
            link='http://example.com/user1gift',
            cost='19.99',
            image='http://example.com/image1.jpg',
            user=self.user1
        )

        Gift.objects.create(
            name='User2 Gift',
            link='http://example.com/user2gift',
            image='http://example.com/image2.jpg',
            cost='19.99', 
            user=self.user2
        )

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.gifts_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK) #получили ответ и правильный статус
        self.assertEqual(len(response.data), 1) #проверяем что у юзера1 1 подарок, и не создалось лишних
        self.assertEqual(response.data[0]['name'], 'User1 Gift') #проверяем что что подарок правильный создался, и название подарка совпадает

    def test_list_no_cross_user_gifts(self):
        """ Test that user2 cannot see gifts of user1. """
        Gift.objects.create(
            name='User1 Gift',
            link='http://example.com/user1gift',
            image='http://example.com/image1.jpg',
            cost='19.99',
            user=self.user1
        )

        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.gifts_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK) #проверяем ответ и статус
        self.assertEqual(len(response.data), 0)  # проверяем что юзеру2 недоступны подарки юзера1

    def test_unauthenticated_access(self):
        """ Test that unauthenticated users cannot access gift endpoints. """
        response = self.client.get(self.gifts_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) #проверяем что неавторизованный юзер не может получить доступ

    def test_retrieve_gift_detail(self):
        """ Test retrieving gift detail for the authenticated user. """
        gift = Gift.objects.create(
            name='Detail Gift',
            link='http://example.com/detailgift',
            image='http://example.com/imagedetail.jpg',
            cost='39.99',
            user=self.user1
        )
        gift_detail_url = reverse("gift-detail", args=[gift.id])

        self.client.force_authenticate(user=self.user1)        
        response = self.client.get(gift_detail_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK) #проверяем ответ и статус
        self.assertEqual(response.data['name'], gift.name) #проверяем что название подарка совпадает
        self.assertEqual(response.data['link'], gift.link) #проверяем что ссылка подарка совпадает

    def test_update_gift(self):
        """ Test updating a gift's details. """
        gift = Gift.objects.create(
            name='Old Gift',
            link='http://example.com/oldgift',
            image='http://example.com/imageold.jpg',
            cost='49.99',
            user=self.user1,
            status=Gift.Status.AVAILABLE
        )
        gift_update_url = reverse("gift-detail", args=[gift.id])

        self.client.force_authenticate(user=self.user1)

        updated_data = {
            'name': 'Updated Gift',
            'link': 'http://example.com/updatedgift',
            'image': 'http://example.com/imageupdated.jpg',
            'cost': '59.99',
            'status': Gift.Status.RESERVED
        }
        response = self.client.put(gift_update_url, updated_data, format='json')
        

        self.assertEqual(response.status_code, status.HTTP_200_OK) #проверяем ответ и статус
        self.assertEqual(response.data["name"], updated_data["name"])
        self.assertEqual(response.data["link"], updated_data["link"])
        gift.refresh_from_db()
        self.assertEqual(gift.status, Gift.Status.RESERVED)


    def test_delete_gift(self):
        """ Test deleting a gift. """
        gift = Gift.objects.create(
            name='Delete Gift',
            link='http://example.com/deletegift',
            image='http://example.com/imagedelete.jpg',
            cost='69.99',
            user=self.user1
        )
        gift_delete_url = reverse("gift-detail", args=[gift.id])

        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(gift_delete_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT) #проверяем ответ и статус
        self.assertFalse(Gift.objects.filter(id=gift.id).exists()) #проверяем что подарок удален из базы