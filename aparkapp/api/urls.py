from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .views import (AnnouncementAPI, AnnouncementsAPI, AnnouncementStatusAPI,
                    AnnouncementsUserAPI, CancelAnnouncementsAPI, CancelReservationAPI, GeolocationToAddressAPI,
                    GeolocationToCoordinatesAPI, ProfileApi, ReservationAPI,
                    ReservationByAnouncementAPI, ReservationsAPI, UsersAPI,
                    UsersVehiclesAPI, VehiclesAPI, VehiclesIdAPI,
                    myAnnouncementsAPI, RegisterAPI, UserAPI)

urlpatterns = [
    path('vehicles/', VehiclesAPI.as_view()),
    path('vehicles/<int:pk>/', VehiclesIdAPI.as_view()),
    path('users/', UsersAPI.as_view()),
    path('users/<int:pk>/', UserAPI.as_view()),
    path('profiles/', ProfileApi.as_view()),
    path('login/', jwt_views.TokenObtainPairView.as_view()),
    path('refresh-token/', jwt_views.TokenRefreshView.as_view()),
    path('announcements/', AnnouncementsAPI.as_view()),
    path('myAnnouncements/', myAnnouncementsAPI.as_view()),
    path('announcements/status/<int:pk>/', AnnouncementStatusAPI.as_view()),
    path('announcement/<int:pk>/', AnnouncementAPI.as_view()),
    path('announcement/user/', AnnouncementsUserAPI.as_view()),
    path('reservation/<int:pk>/', ReservationAPI.as_view()),
    path('reservation/anouncement/<int:pk>/', ReservationByAnouncementAPI.as_view()),
    path('reservations/', ReservationsAPI.as_view()),
    path('users/vehicles/', UsersVehiclesAPI.as_view()),
    path('reservation/<int:pk>/', ReservationAPI.as_view()),
    path('geolocatorToAddress/', GeolocationToAddressAPI.as_view()),
    path('geolocatorToCoordinates/', GeolocationToCoordinatesAPI.as_view()),
    path('register/', RegisterAPI.as_view()),
    path('cancel/announcement/<int:pk>/', CancelAnnouncementsAPI.as_view()),
    path('cancel/reservation/<int:pk>/', CancelReservationAPI.as_view()),
]
