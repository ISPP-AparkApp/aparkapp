from os import stat
from django.contrib.auth.models import User
from rest_framework import serializers

from api.models import Vehicle, Announcement


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username')


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id','brand','model','license_plate','color','type','user']

    # def create(self,validated_data):
    #     query = Vehicle.objects.filter(license_plate=validated_data["license_plate"])
    #     if(query):
    #         vehicle = Vehicle.objects.create(**validated_data)
    #     return vehicle

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id','date','wait_time','price','allow_wait','location','zone','limited_mobility',
                'status','observation','rated','vehicle','user']
