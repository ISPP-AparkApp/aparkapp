from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

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


class UserNestedProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class  Meta:
        model = User
        fields = ['username','email','first_name','last_name', 'profile']
        

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

class SwaggerCancelAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['cancelled']


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

### REGISTER SERIALIZERS

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    profile = ProfileSerializer()
    vehicles = SwaggerVehicleSerializerId(many=True)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'profile', 'vehicles')
        extra_kwargs = {'first_name': {'required': True},
                     'last_name': {'required': True}
                        }
 
    def validate_vehicles(self, value):
        if not value:
            raise serializers.ValidationError(("Inserte un vehículo"))
        return value

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        vehicles_data = validated_data.pop('vehicles')
        user = User.objects.create(username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )  

        user.set_password(validated_data['password'])
        user.save()

        Profile.objects.create(user=user, **profile_data)
        for vehicle_data in vehicles_data:
            Vehicle.objects.create(user=user, **vehicle_data)

        return user
