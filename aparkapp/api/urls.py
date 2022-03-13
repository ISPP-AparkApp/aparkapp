from django.urls import URLPattern, path, include
from .views import *

from rest_framework import routers

router = routers.DefaultRouter()
router.register('users', UserViewSet)


urlpatterns = [
    path('',include(router.urls)),
    path('vehicles/', VehiclesAPI.as_view()),
]