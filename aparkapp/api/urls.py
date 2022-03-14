from xml.etree.ElementInclude import include
from django.urls import path
from .views import *

from rest_framework import routers

urlpatterns = [
    path('announcements/', AnnouncementsAPI.as_view()),
    path('announcement/<int:pk>/', AnnouncementAPI.as_view()),
]