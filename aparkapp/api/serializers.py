from os import stat
from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Profile

from api.models import Vehicle


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username')

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id','username', 'password', 'email', 'first_name', 'last_name', 'phone', 'birthdate')

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id','brand','model','license_plate','color','type','user']
