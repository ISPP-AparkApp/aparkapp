from django.test import TestCase
from api.models import User, Vehicle, Reservation, Announcement
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

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


class ReservationTestCase(TestCase):
    access = ""
    refresh = ""
    second_access =""
    second_refresh = ""
    
    def setUp(self):
        self.user = User(
            id=1,
            username='user_for_reservation',
        )
        self.user.set_password('prueba12345')
        self.user.save()

        self.second_user = User(
            id=2,
            username='second_user',
        )
        self.second_user.set_password('Mecpe1234567')
        self.second_user.save()

        self.third_user = User(
            id=3,
            username='third_user',
        )
        self.third_user.set_password('pepperoni1234567')
        self.third_user.save()

        vehicle = Vehicle(
            id=1,
            brand="Audi",
            model="X5",
            license_plate="4982 FW",
            color="Red",
            type="Segmento A"
        )
        vehicle.user = self.user
        vehicle.save()

        second_vehicle = Vehicle(
            id=2,
            brand="BMW",
            model="Z3",
            license_plate="7777 NN",
            color="Black",
            type="Segmento D"
        )
        second_vehicle.user = self.second_user
        second_vehicle.save()

        third_vehicle = Vehicle(
            id=3,
            brand="Cupra",
            model="M1",
            license_plate="3128 FC",
            color="Grey",
            type="Segmento E"
        )
        third_vehicle.user = self.third_user
        third_vehicle.save()
        
        announcement=Announcement(
            id=1,
            date=make_aware(datetime.now()),
            wait_time=3,
            price=7,
            location="",
            longitude=35.3,
            latitude=14,
            vehicle=vehicle,
            user=self.user
        )
        announcement.save()

        second_announcement=Announcement(
            id=2,
            date=make_aware(datetime.now()),
            wait_time=1,
            price=4,
            location="",
            longitude=96.3,
            latitude=23.7,
            vehicle=second_vehicle,
            user=self.second_user
        )
        second_announcement.save()

        third_announcement=Announcement(
            id=3,
            date=make_aware(datetime.now()+timedelta(hours=3)),
            wait_time=1,
            price=4,
            location="",
            longitude=33,
            latitude=55,
            vehicle=second_vehicle,
            user=self.second_user
        )
        third_announcement.save()

        reservation=Reservation(
            id=1,
            date=announcement.date+timedelta(hours=2),
            n_extend=0,
            user=self.second_user,
            announcement=announcement
        )
        reservation.save()

        second_reservation=Reservation(
            id=2,
            date=announcement.date+timedelta(hours=7),
            n_extend=0,
            user=self.user,
            announcement=second_announcement
        )
        second_reservation.save()

        api_client = APIClient()
        response = api_client.post(
                '/api/login/', {
                'username': 'user_for_reservation',
                'password': 'prueba12345'
            },
            format='json'
        )
        self.access = response.data['access']
        self.refresh = response.data['refresh']  

        second_login = api_client.post(
                '/api/login/', {
                'username': 'second_user',
                'password': 'Mecpe1234567',
            },
            format='json'
        )
        self.second_access = second_login.data['access']
        self.second_refresh = second_login.data['refresh']  
        
    # APP - 20/03/2022 - Test which get a valid reservation given its ID and invalid one
    def test_get_reservation(self):
        client = APIClient()

        first_response = client.get(
            '/api/reservation/1/',
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        second_response = client.get(
            '/api/reservation/999/',
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertTrue(first_response.data['announcement'])

        self.assertTrue(second_response.status_code, status.HTTP_404_NOT_FOUND)

    # APP - 20/03/2022 - Test which retrieve list of reservations of the logged user
    def test_get_reservations(self):
        client = APIClient()

        response = client.get(
            '/api/reservations',
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )  
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # APP - 20/03/2022 - Test which creates a reservation for an announcement already reserved
    def test_delete_reservation(self):
        client = APIClient()
        first_response = client.delete(
            '/api/reservation/2/',
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        second_response = client.delete(
            '/api/reservation/1/',
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        self.assertEqual(first_response.status_code, status.HTTP_204_NO_CONTENT)       
        self.assertEqual(second_response.status_code, status.HTTP_404_NOT_FOUND)  

    # APP - 20/03/2022 - Test which creates three reservations one already reserved, one from itself and another valid
    def test_create_reservation(self):
        client = APIClient()
        first_response = client.post(
                '/api/reservations', {
                    "date": "2022-03-21T23:19:13.277Z",
                    "n_extend": 0,
                    "user": 1,
                    "announcement": 1
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )

        second_response = client.post(
                '/api/reservations', {
                    "date": "2022-03-22T23:19:13.277Z",
                    "n_extend": 0,
                    "user": 2,
                    "announcement": 3
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.second_access)
        )

        third_response = client.post(
                '/api/reservations', {
                    "date": "2022-03-23T23:19:13.277Z",
                    "n_extend": 0,
                    "user": 1,
                    "announcement": 3
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        self.assertEqual(first_response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(second_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(third_response.status_code, status.HTTP_201_CREATED)

    # APP - 20/03/2022 - Test which updates reservations one which doesn't exist, one already reserved 
    # and one valid
    def test_update_reservation(self):
        client = APIClient()
        first_response = client.put(
                '/api/reservation/1/', {
                    "date": "2022-03-21T23:19:13.277Z",
                    "n_extend": 1,
                    "user": 2,
                    "announcement": 99
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        second_response = client.put(
                '/api/reservation/1/', {
                    "date": "2022-03-21T23:19:13.277Z",
                    "n_extend": 1,
                    "user": 2,
                    "announcement": 2
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )

        third_response = client.put(
                '/api/reservation/2/', {
                    "date": "2022-03-21T23:19:13.277Z",
                    "n_extend": 1,
                    "user": 3,
                    "announcement": 3
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        self.assertEqual(first_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(third_response.status_code, status.HTTP_204_NO_CONTENT)