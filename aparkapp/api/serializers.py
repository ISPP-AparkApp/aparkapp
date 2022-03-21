from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Profile
from api.models import Vehicle, Announcement, Reservation
from django.core.validators import MinValueValidator, MaxValueValidator

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

class GeolocationToAddressSerializer(serializers.Serializer):
    longitude = serializers.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    latitude=serializers.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])  
    one_result = serializers.BooleanField(default=False)

class GeolocationToCoordinatesSerializer(serializers.Serializer):
    location = serializers.CharField(max_length=1024)
    country_code= serializers.CharField(max_length=2, default="ES")
    one_result = serializers.BooleanField(default=False)
    raw= serializers.BooleanField(default=True)