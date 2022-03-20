from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Vehicle, Announcement, Reservation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username')


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id','brand','model','license_plate','color','type','user']

class SwaggerVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id','brand','model','license_plate','color','type']

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class SwaggerAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id','date','wait_time','price','allow_wait','location', 'longitude', 'latitude',
        'zone', 'limited_mobility', 'status', 'observation', 'rated', 'vehicle']

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

class SwaggerCreateReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['announcement']

class SwaggerUpdateReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['date','n_extend','cancelled','rated','announcement', 'user']

