from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from api.models import Announcement, Profile, Reservation, Vehicle

### PROFILE SERIALIZERS

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'birthdate']

class SwaggerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'birthdate']

### USER SERIALIZERS

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username','email','first_name','last_name']

class SwaggerUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username','email','first_name','last_name']

### VEHICLE SERIALIZERS

class VehicleSerializerId(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id','brand','model','license_plate','color','type']

class SwaggerVehicleSerializerId(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['brand','model','license_plate','color','type']

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id','brand','model','license_plate','color','type','user']

class SwaggerVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id','brand','model','license_plate','color','type']

### ANNOUNCEMENTS SERIALIZERS

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class AnnouncementNestedVehicleSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only = True)
    class Meta:
        model = Announcement
        fields = '__all__'
class SwaggerAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id','date','wait_time','price','allow_wait','location', 'longitude', 'latitude',
        'zone', 'limited_mobility', 'status', 'observation', 'rated', 'vehicle']

class SwaggerUpdateAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [ 'status']


### RESERVATION SERIALIZERS

class ReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    announcement = AnnouncementNestedVehicleSerializer(read_only = True)
    class Meta:
        model = Reservation
        fields = ['id','date','n_extend','cancelled','rated','announcement', 'user']
        
class SwaggerCreateReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['announcement']

class SwaggerUpdateReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['date','n_extend','cancelled','rated','announcement', 'user']

class SwaggerCancelReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['cancelled']


### GEOLOCATION SERIALIZERS

class GeolocationToAddressSerializer(serializers.Serializer):
    longitude = serializers.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    latitude=serializers.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])  
    one_result = serializers.BooleanField(default=False)

class GeolocationToCoordinatesSerializer(serializers.Serializer):
    location = serializers.CharField(max_length=1024)
    country_code= serializers.CharField(max_length=2, default="ES")
    one_result = serializers.BooleanField(default=False)
    raw= serializers.BooleanField(default=True)
