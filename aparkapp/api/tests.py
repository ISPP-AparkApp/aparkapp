from django.test import TestCase
from rest_framework.test import APIClient
from api.models import User, Vehicle, Announcement, Reservation
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
    access = ""

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
            price=3.5,  allow_wait=True, location='Reina Mercedes', latitude=38.35865724531185, longitude=-5.986121868933244,
            zone='Zona libre', limited_mobility=False, status='Initial', observation='Ninguna', rated=False,
            vehicle=self.vehicle, user=self.user)
        self.announcement.save()

        self.announcement2 = Announcement(date="2022-08-14 15:43", wait_time=5,
            price=2,  allow_wait=True, location='Triana', latitude=38.35865724531185, longitude=-5.986121868933244,
            zone='Zona libre', limited_mobility=False, status='Initial', observation='Ninguna', rated=False,
            vehicle=self.vehicle, user=self.user)
        self.announcement2.save()

        self.user2 = User(username='user_test2')
        self.user2.set_password('aparkapp123')
        self.user2.save()

        self.vehicle2 = Vehicle(
            brand="Testing2",
            model="Testing2",
            license_plate="Testing2",
            color="Testing2",
            type="Segmento A",
            user = self.user2
        )
        self.vehicle2.save()

        self.announcement3 = Announcement(date="2022-08-14 17:43", wait_time=5,
            price=4,  allow_wait=True, location='Triana', latitude=38.35585724531185, longitude=-5.986231868933244,
            zone='Zona azul', limited_mobility=False, status='Initial', observation='Ninguna', rated=False,
            vehicle=self.vehicle2, user=self.user2)
        self.announcement3.save()

        self.announcement4 = Announcement(date="2022-08-15 17:43", wait_time=5,
            price=4,  allow_wait=True, location='Triana', latitude=38.35585724531185, longitude=-5.986231868933244,
            zone='Zona azul', limited_mobility=False, status='Initial', observation='Ninguna', rated=False,
            vehicle=self.vehicle2, user=self.user2)
        self.announcement4.save()

        self.reservation = Reservation(date=self.announcement3.date, n_extend=1,
            cancelled=False, rated=False, user=self.user, announcement=self.announcement3)
        self.reservation.save()

       client = APIClient()
       response = client.post(
                '/api/login/', {
                'username': 'user_test',
                'password': 'aparkapp123'
            },
            format='json'
        )
        self.access = response.data['access']

    #Test list announcements with no authenticated user
    def test_get_announcements_unauthorized(self):
        client = APIClient()
        response = client.get('/api/announcements/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #Test list announcements with an authenticated user
    def test_get_announcements(self):
        client = APIClient()
        response = client.get('/api/announcements/', format='json', HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    #Test search announcements by location
    def test_search_announcements_by_location(self):
        client = APIClient()
        response = client.get('/api/announcements/?search=Triana', format='json', HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()
        for r in results:
            self.assertEqual(r['location'], 'Triana')
    
    #Test search announcements by zone
    def test_search_announcements_by_zone(self):
        client = APIClient()
        response = client.get('/api/announcements/?search=libre', format='json', HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()
        for r in results:
            self.assertEqual(r['zone'], 'Zona libre')

    #Test order announcements by price
    def test_order_announcements_by_price(self):
        client = APIClient()
        response = client.get('/api/announcements/?ordering=price', format='json', HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        results = response.json()
        self.assertLessEqual(results[0]['price'], results[1]['price'])

    #Test filter announcements by vehicle type
    def test_filter_announcements_by_vehicle_type(self):
        client = APIClient()
        response = client.get('/api/announcements/?vehicle__type=Segmento+A', format='json', HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        results = response.json()
        for r in results:
            vehicleId = r['vehicle']
            vehicle = Vehicle.objects.get(id=vehicleId)
            self.assertEqual(vehicle.type, 'Segmento A')

    #Test obtaining details of an advertisement that is reserved by the user
    def test_details_announcement(self):
        client = APIClient()
        response = client.get('/api/announcement/' + str(self.announcement3.id)+'/', format='json', HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    #Test obtaining details of an advertisement that is not reserved by the user
    def test_details_announcement_unauthorized(self):
        client = APIClient()
        response = client.get('/api/announcement/' + str(self.announcement4.id)+'/', format='json', HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)