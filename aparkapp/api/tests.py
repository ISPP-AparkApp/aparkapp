from django.test import TestCase
from api.models import User, Vehicle
from rest_framework.test import APIClient
from rest_framework import status


class AuthenticationTestCase(TestCase):
    # APP - 19/03/2022 - Create user for setup
    def setUp(self):
        user = User(
            username='testing_login',
        )
        user.set_password('admin123')
        user.save()

    # APP - 19/03/2022 - Login Test
    def test_login(self):
        client = APIClient()
        response = client.post(
                '/api/login/', {
                'username': 'testing_login',
                'password': 'admin123'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    # APP - 19/03/2022 - First login to get refresh token and then test refresh token-
    def test_refresh_token(self):
        client = APIClient()

        login_response = client.post(
                '/api/login/', {
                'username': 'testing_login',
                'password': 'admin123'
            },
            format='json'
        )

        response = client.post(
                '/api/refresh-token/', {
                'refresh': login_response.data['refresh'],
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

class VehiclesIDTestCase(TestCase):
    access = ""
    refresh = ""
    # APP - 19/03/2022 - Create user and vehicle, and get tokens
    def setUp(self):
        self.user = User(
            username='testing_login',
        )
        self.user.set_password('admin123')
        self.user.save()

        vehicle = Vehicle(
            id=99,
            brand="Testing",
            model="Testing",
            license_plate="Testing",
            color="Testing",
            type="Segmento A"
        )
        vehicle.user = self.user
        vehicle.save()

        vehicle2 = Vehicle(
            id=98,
            brand="Testing",
            model="Testing",
            license_plate="Testing",
            color="Testing",
            type="Segmento A"
        )
        vehicle2.user = self.user
        vehicle2.save()

        client = APIClient()
        response = client.post(
                '/api/login/', {
                'username': 'testing_login',
                'password': 'admin123'
            },
            format='json'
        )
        
        self.access = response.data['access']
        self.refresh = response.data['refresh']


    # APP - 20/03/2022 - Test create vehicle with token access in the header
    def test_update_vehicle(self):
        client = APIClient()
        response = client.put(
                '/api/vehicles/99/', {
                    "id": 99,
                    "brand":"Test",
                    "model":"Prueba",
                    "license_plate":"Testing2",
                    "color":"Prueba",
                    "type":"Segmento A"
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # APP - 20/03/2022 - Test get vehicle with token access in the header
    def test_get_vehicle(self):
        client = APIClient()
        response = client.get('/api/vehicles/99/',HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # APP - 20/03/2022 - Test delete vehicle with token access in the header
    def test_delete_vehicle(self):
        client = APIClient()
        response = client.delete('/api/vehicles/98/',HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        response2 = client.delete('/api/vehicles/99/',HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)
    

