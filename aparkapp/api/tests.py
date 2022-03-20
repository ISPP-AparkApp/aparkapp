from django.test import TestCase
from api.models import User, Vehicle, Announcement
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

class VehiclesTestCase(TestCase):
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
            brand="Testing",
            model="Testing",
            license_plate="Testing",
            color="Testing",
            type="Segmento A"
        )
        vehicle.user = self.user
        vehicle.save()

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

    # APP - 19/03/2022 - Test create vehicle with token access in the header
    def test_create_vehicle(self):
        client = APIClient()
        response = client.post(
                '/api/vehicles/', {
                    "brand":"Prueba",
                    "model":"Prueba",
                    "license_plate":"Testing2",
                    "color":"Prueba",
                    "type":"Segmento A"
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('mensaje' in response.data)
        self.assertTrue('vehículo' in response.data)

    # APP - 19/03/2022 - Test create a vehicle that already exists by the same user 
    def test_create_vehicle_validation(self):
        client = APIClient()
        response = client.post(
                '/api/vehicles/', {
                    "brand":"Prueba",
                    "model":"Prueba",
                    "license_plate":"Testing",
                    "color":"Prueba",
                    "type":"Segmento A"
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('error' in response.data)


class AnnouncementTestCase(TestCase):
    def setUp(self):
        self.user = User(username='user_test')
        self.user.set_password('aparkapp123')
        self.user.save()

        self.vehicle = Vehicle(
            brand="Testing",
            model="Testing",
            license_plate="Testing",
            color="Testing",
            type="Segmento A",
            user = self.user
        )
        
        self.vehicle.save()
        
        self.announcement = Announcement(date="2022-08-14 13:43", wait_time=5,
         price=2, latitude=38.35865724531185, longitude=-5.986121868933244, vehicle=self.vehicle, user = self.user)
        self.announcement.save()


        self.announcement2 = Announcement(date="2022-08-14 15:43", wait_time=5,
         price=2, latitude=38.35865724531185, longitude=-5.986121868933244, vehicle=self.vehicle, user = self.user)
        self.announcement2.save()


        client = APIClient()
        response = client.post(
                '/api/login/', {
                'username': 'user_test',
                'password': 'aparkapp123'
            },
            format='json'
        )
        
        self.access = response.data['access']

    def test_create_announcement(self):
        client = APIClient()       
        response = client.post('/api/announcements/', {
                 
                    "date": "2022-08-14 13:45",
                    "wait_time": 5,
                    "price": 2,
                    "latitude": 38.35865724531185,
                    "longitude": -5.986121868933244,
                    "vehicle": self.vehicle.id
                },
         format='json',
        HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_existing_announcement(self):
        client = APIClient()

        response = client.post('/api/announcements/', {
                    "date": "2022-08-14 13:43",
                    "wait_time": 5,
                    "price": 2,
                    "latitude": 38.35865724531185,
                    "longitude": -5.986121868933244,
                    "vehicle": self.vehicle.id
                },
         format='json',
        HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, 'Ya existe un anuncio para este vehículo a la misma hora.')

    
    def test_create_announcement_fail(self):
        client = APIClient()

        response = client.post('/api/announcements/', {
                    "date": "2022-08-14 13:43",
                    "wait_time": 5,
                    "price": 2,
                    "latitude": 38.35865724531185,
                    "longitude": -5.986121868933244,
                    "vehicle": -1 #This ID does not exist 
                },
         format='json',
        HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_modify_announcement(self):
        client = APIClient()

        response = client.put('/api/announcement/' + str(self.announcement.id)+'/', {
                    "date": "2022-08-14 14:00",
                    "wait_time": 5,
                    "price": 2,
                    "latitude": 38.35865724531185,
                    "longitude": -5.986121868933244,
                    "vehicle": self.vehicle.id  
                },
         format='json',
        HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #Test modify an existing announcement with the same date and vehicle from another exisiting announcement
    def test_modify_announcement_validation(self):
        client = APIClient()

        response = client.put('/api/announcement/' + str(self.announcement2.id)+'/', {
                    "date": "2022-08-14 13:43",
                    "wait_time": 10,
                    "price": 2,
                    "latitude": 38.35865724531185,
                    "longitude": -5.986121868933244,
                    "vehicle": self.vehicle.id  
                },
         format='json',
        HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, 'Ya existe un anuncio para este vehículo a la misma hora.')

    #Test modify an existing announcement with no price
    def test_modify_announcement_fails(self):
        client = APIClient()

        response = client.put('/api/announcement/' + str(self.announcement.id)+'/', {
                    "date": "2022-08-14 13:43",
                    "wait_time": 10,
                    "latitude": 38.35865724531185,
                    "longitude": -5.986121868933244,
                    "vehicle": self.vehicle.id  
                },
         format='json',
        HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_announcement(self):
        client = APIClient()
        response = client.delete('/api/announcement/' + str(self.announcement.id)+'/',
        HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class UserVehiclesTestCase(TestCase):
    def setUp(self):
        self.user = User(username='user_test')
        self.user.set_password('aparkapp123')
        self.user.save()

        self.vehicle = Vehicle(
            brand="Testing",
            model="Testing",
            license_plate="Testing",
            color="Testing",
            type="Segmento A",
            user = self.user
        )
        
        self.vehicle.save()

        self.vehicle2 = Vehicle(
            brand="Testing1",
            model="Testing1",
            license_plate="Testing1",
            color="Testing1",
            type="Segmento A1",
            user = self.user
        )
        
        self.vehicle2.save()

        client = APIClient()
        response = client.post(
                '/api/login/', {
                'username': 'user_test',
                'password': 'aparkapp123'
            },
            format='json'
        )
        
        self.access = response.data['access']

    def test_get_vehicles_by_user(self):
        client = APIClient()
        response = client.get('/api/users/vehicles/', HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
