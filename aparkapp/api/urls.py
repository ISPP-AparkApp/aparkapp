from django.urls import URLPattern, path, include
from rest_framework_simplejwt import views as jwt_views
from .views import *


urlpatterns = [
    path('vehicles/', VehiclesAPI.as_view()),
    path('login/', jwt_views.TokenObtainPairView.as_view()),
    path('logout/',Logout.as_view()),
    path('refresh-token/',jwt_views.TokenRefreshView.as_view()),
]