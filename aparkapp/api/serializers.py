from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Profile
from api.models import Vehicle, Announcement, Reservation


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'birthdate']

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username','email','first_name','last_name']
 
class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id','brand','model','license_plate','color','type']


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'
