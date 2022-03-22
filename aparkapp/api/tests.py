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
        
class AnnouncementsUserTestCase(TestCase):
    def setUp(self):
        self.user = User(username='user_test')
        self.user.set_password('aparkapp123')
        self.user.save()

        self.user2 = User(username='user_test2')
        self.user2.save()

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
            brand="Testing2",
            model="Testing2",
            license_plate="Testing2",
            color="Testing2",
            type="Segmento A",
            user = self.user2
        )
        self.vehicle2.save()

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

        self.announcement3 = Announcement(date="2022-08-14 17:43", wait_time=5,
            price=4,  allow_wait=True, location='Triana', latitude=38.35585724531185, longitude=-5.986231868933244,
            zone='Zona Azul', limited_mobility=False, status='Initial', observation='Ninguna', rated=False,
            vehicle=self.vehicle2, user=self.user2)
        self.announcement3.save()

        self.announcement4 = Announcement(date="2022-08-15 17:43", wait_time=5,
            price=4,  allow_wait=True, location='Triana', latitude=38.35585724531185, longitude=-5.986231868933244,
            zone='Zona Azul', limited_mobility=False, status='Initial', observation='Ninguna', rated=False,
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
        
    #Test search announcements by user
    def test_search_announcements_by_user(self):
        client = APIClient()
        response = client.get('/api/announcement/user/', format='json', HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()
        i=0
        for r in results:
            i++
        self.assertEqual(i, 2)
        
        
class AnnouncementStatusAPI(TestCase):
    def setUp(self):
        self.user = User(username='user_test')
        self.user.set_password('aparkapp123')
        self.user.save()

        self.user2 = User(username='user_test2')
        self.user2.save()

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
            brand="Testing2",
            model="Testing2",
            license_plate="Testing2",
            color="Testing2",
            type="Segmento A",
            user = self.user2
        )
        self.vehicle2.save()

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

        self.announcement3 = Announcement(date="2022-08-14 17:43", wait_time=5,
            price=4,  allow_wait=True, location='Triana', latitude=38.35585724531185, longitude=-5.986231868933244,
            zone='Zona Azul', limited_mobility=False, status='Initial', observation='Ninguna', rated=False,
            vehicle=self.vehicle2, user=self.user2)
        self.announcement3.save()

        self.announcement4 = Announcement(date="2022-08-15 17:43", wait_time=5,
            price=4,  allow_wait=True, location='Triana', latitude=38.35585724531185, longitude=-5.986231868933244,
            zone='Zona Azul', limited_mobility=False, status='Initial', observation='Ninguna', rated=False,
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
        
        
    def test_modify_announcement_status(self):
        client = APIClient()

        response = client.put('/api/announcements/status/' + str(self.announcement2.id)+'/', {
                    "Initial"
                }
        HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(self.announcement2, "Initial")

        
    def test_search_announcements(self):
        client = APIClient()
        response = client.get('/api/announcements/status/', format='json', HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
