from django.urls import URLPattern, path, include
from .views import *


urlpatterns = [
    path('vehicles/', VehiclesAPI.as_view()),
    path('login/',Login.as_view()),
    path('logout/',Logout.as_view()),
    path('refresh-token/',UserToken.as_view()),
]