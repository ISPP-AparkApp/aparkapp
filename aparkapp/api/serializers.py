from os import stat
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status

from api.models import Vehicle


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password'
        ]
        extra_kwargs = {'password':{'write_only':True, 'required': True}}

    def create(self,validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id','brand','model','license_plate','color','type','user']

    # def create(self,validated_data):
    #     query = Vehicle.objects.filter(license_plate=validated_data["license_plate"])
    #     if(query):
    #         vehicle = Vehicle.objects.create(**validated_data)
    #     return vehicle