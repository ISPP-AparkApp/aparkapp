from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import VehiclesAPI, AnnouncementAPI, AnnouncementsAPI, UsersAPI, ReservationAPI,ReservationsAPI, AnnouncementsUserAPI,ReservationByAnouncementAPI

urlpatterns = [
    path('vehicles/', VehiclesAPI.as_view()),
    path('login/', jwt_views.TokenObtainPairView.as_view()),
    path('refresh-token/',jwt_views.TokenRefreshView.as_view()),
    path('announcements/', AnnouncementsAPI.as_view()),
    path('announcement/<int:pk>/', AnnouncementAPI.as_view()),
    path('announcement/user/', AnnouncementsUserAPI.as_view()),
    path('users/vehicles/', UsersAPI.as_view()),
    path('reservation/<int:pk>/', ReservationAPI.as_view()),
    path('reservation/anouncement/<int:pk>/', ReservationByAnouncementAPI.as_view()),
    path('reservations',ReservationsAPI.as_view()),
]
