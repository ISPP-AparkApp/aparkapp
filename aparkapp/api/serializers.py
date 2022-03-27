from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Profile
from api.models import Vehicle, Announcement, Reservation
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'birthdate']

class SwaggerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'birthdate']

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username','email','first_name','last_name']

class SwaggerUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username','email','first_name','last_name']
 
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

class AnnouncementSerializer(serializers.ModelSerializer):
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

class VehicleRegisterSerializer(serializers.ModelSerializer):
    #license_plate = serializers.CharField(required=True, validators=[UniqueValidator(queryset=Vehicle.objects.all().values_list('license_plate',flat=True))])
    
    class Meta:
        model = Vehicle
        fields = ['brand','model','license_plate','color','type', 'user']

class RegisterSerializer(serializers.ModelSerializer):
    #vehicle = VehicleRegisterSerializer()

    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    #password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        extra_kwargs = {'first_name': {'required': True},
                     'last_name': {'required': True}
                        }

        # def validate(self,attrs):
        #     if attrs['password'] != attrs['password2']:
        #         raise serializers.ValidationError({'password': 'Password fields did not match.'})
            
        #     return attrs

        def create(self, validated_data):
            user = User.objects.create(username=validated_data['username'],
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name']
            )  

            user.set_password(validated_data['password'])
            user.save()

        #     v=Vehicle.objects.create(VehicleRegisterSerializer(), validated_data=vehicle_data)
        #     v.save()
        #     print(validated_data)
        #     user = User.objects.update_or_create(validated_data)

            return user

class ProfileRegisterSerializer(serializers.ModelSerializer):
    #user = RegisterSerializer()
    #birthdate = serializers.DateField(required=True)
    class Meta:
        model = Profile
        fields = ['phone', 'birthdate', 'user']
        extra_kwargs = {'phone': {'required': True}
                        }
        # def create(self, validated_data):
        #     user_data = validated_data.pop('user')
        #     user = RegisterSerializer.create(RegisterSerializer(), validated_data=user_data)
        #     profile = Profile.objects.update_or_create(user=user,**validated_data)

        #     return profile

class SwaggerRegisterField(serializers.JSONField):
    class Meta:
        swagger_schema_fields = {
            "username": "username",
            "password": "password",
            "email": "email",
            "first_name": "first_name",
            "last_name": "last_name",
            "profile": {
                "phone": "phone",
                "birthdate": "birthdate"
            },
            "vehicle":{
                "brand": "brand",
                "model": "model",
                "color": "color",
                "type": "type"
            }
        }

class SwaggerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
    
    register = SwaggerRegisterField()