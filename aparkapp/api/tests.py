from django.test import TestCase
from rest_framework.test import APIClient
from api.models import User, Vehicle, Announcement, Reservation,Profile
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
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue('error' in response.data)

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
            license_plate="Testing1",
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


    # APP - 20/03/2022 - Test update vehicle with token access in the header
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


class UserTestCase(TestCase):
    access = ""
    refresh = ""
    # APP - 19/03/2022 - Create user and get tokens
    def setUp(self):
        self.user = User(
            username='testing_login',
        )
        self.user.set_password('admin123')
        self.user.save()

        user = User(
            username="prueba",
            email="test@gmail.com",
            first_name="Testing",
            last_name="Testing"
        )
        user.user = self.user
        user.save()

        profile = Profile(
            id= self.user.id,
            phone= "692069179",
	        birthdate= "2022-03-15",
            user= self.user
        )
        profile.save()

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

    # APP - 21/03/2022 - Test update user with token access in the header
    def test_update_user(self):
        client = APIClient()
        response = client.put(
                '/api/users/', {
                "username": "testing_login2",
                "email": "test@gmail.es",
                "first_name": "Testing",
                "last_name": "Testing"
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # APP - 21/03/2022 - Test get user with token access in the header
    def test_get_user(self):
        client = APIClient()
        response = client.get('/api/users/',HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # APP - 21/03/2022 - Test delete vehicle with token access in the header
    def test_delete_user(self):
        client = APIClient()
        response = client.delete('/api/users/',HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    # APP - 21/03/2022 - Test get profile with token access in the header
    def test_get_profile(self):
        client = APIClient()
        response = client.get('/api/profiles/',HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # APP - 21/03/2022 - Test update user with token access in the header
    def test_update_profile(self):
        client = APIClient()
        response = client.put(
                '/api/profiles/', {
                "phone": "692069173",
	            "birthdate": "2022-03-15"
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AnnouncementTestCase(TestCase):
    
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

    def test_create_announcement(self):
        client = APIClient()       
        response = client.post('/api/announcements/', {
                 
                    "date": "2022-08-14 13:45",
                    "wait_time": 5,
                    "price": 2,
                    "allow_wait": True,
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
                    "allow_wait": True,
                    "price": 2,
                    "latitude": 38.35865724531185,
                    "longitude": -5.986121868933244,
                    "vehicle": 1 #This vehicle does not belong to the user 
                },
         format='json',
        HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
    
    def test_create_announcement_fail_bad_request(self):
        client = APIClient()
        
        response = client.post('/api/announcements/', {
                    "date": "2022-08-14 13:53",
                    "wait_time": 5,
                    "allow_wait": True,
                    #"price": 2,  Price it's a mandatory field
                    "latitude": 38.35865724531185,
                    "longitude": -5.986121868933244,
                    "vehicle": self.vehicle.id 
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
                    "allow_wait": True,
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
                    "allow_wait": True,
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
                    "allow_wait": True,
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

    def test_delete_announcement_fail(self):
        client = APIClient()
        response = client.delete('/api/announcement/58/', #This ID does not exists
        HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'No existe el anuncio que desea borrar.')

    def test_delete_announcement_unauthorized(self):
        client = APIClient()
        response = client.delete('/api/announcement/'+ str(self.announcement3.id)+'/',
        HTTP_AUTHORIZATION='Bearer {0}'.format(self.access))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, 'No se puede borrar un anuncio que usted no ha publicado.')

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
            '/api/reservations/',
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
                '/api/reservations/', {
                    "date": "2022-03-21T23:19:13.277Z",
                    "n_extend": 0,
                    "user": 1,
                    "announcement": 1
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.access)
        )

        second_response = client.post(
                '/api/reservations/', {
                    "date": "2022-03-22T23:19:13.277Z",
                    "n_extend": 0,
                    "user": 2,
                    "announcement": 3
            },
            format='json',
            HTTP_AUTHORIZATION='Bearer {0}'.format(self.second_access)
        )

        third_response = client.post(
                '/api/reservations/', {
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


        self.assertTrue('error' in response.data)

