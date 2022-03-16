from django.urls import URLPattern, path, include
from rest_framework_simplejwt import views as jwt_views
from .views import *

urlpatterns = [
    path('vehicles/', VehiclesAPI.as_view()),
    path('vehicles/update/<int:pk>/', VehiclesAPI.as_view()),
    path('vehicles/delete/<int:pk>/', VehiclesAPI.as_view()),
    path('vehicles/get/<int:pk>/', VehiclesAPI.as_view()),
    path('user/<int:pk>/', UsersAPI.as_view()),
    path('login/', jwt_views.TokenObtainPairView.as_view()),
    path('logout/', Logout.as_view()),
    path('announcements/', AnnouncementsAPI.as_view()),
    path('announcement/<int:pk>/', AnnouncementAPI.as_view()),
    path('refresh-token/', jwt_views.TokenRefreshView.as_view()),
    path('users/vehicles/<int:pk>/', UsersAPI.as_view())
]