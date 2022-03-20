from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import VehiclesAPI, AnnouncementAPI, AnnouncementsAPI, UsersVehiclesAPI, ReservationAPI, ReservationsAPI

urlpatterns = [
    path('vehicles/', VehiclesAPI.as_view()),
    path('login/', jwt_views.TokenObtainPairView.as_view()),
    path('refresh-token/',jwt_views.TokenRefreshView.as_view()),
    path('announcements/', AnnouncementsAPI.as_view()),
    path('announcement/<int:pk>/', AnnouncementAPI.as_view()),
    path('users/vehicles/', UsersVehiclesAPI.as_view()),
    path('reservation/<int:pk>/', ReservationAPI.as_view()),
    path('reservations',ReservationsAPI.as_view()),
]