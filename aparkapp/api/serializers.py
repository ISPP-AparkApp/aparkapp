from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from rest_framework import serializers
from api.models import Announcement, Profile, Reservation, Vehicle, Rating
from decimal import Decimal

### PROFILE SERIALIZERS
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
    
    def validate_birthdate(self, value):            
        if value > date.today() or value < date(1900,1,1):
            raise serializers.ValidationError("Inserte una fecha válida")
        elif (date.today().year - value.year) < 18:
            raise serializers.ValidationError("Debe tener 18 años para usar la aplicación")
        return value

    def validate_phone(self, value):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            user = request.user
        
        if Profile.objects.filter(phone=value).exists() and Profile.objects.get(phone=value).user != user:
            raise serializers.ValidationError("Ya existe un usuario registrado con el mismo número de teléfono")
        return value

class ProfileRegisterSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Profile
        fields = ['phone', 'birthdate', 'is_banned']

    def validate_birthdate(self, value):
        if value > date.today() or value < date(1900,1,1):
            raise serializers.ValidationError("Inserte una fecha válida, la fecha no puede ser posterior a la fecha actual ni anterior a 1/1/1900")
        elif (date.today().year - value.year) < 18:
            raise serializers.ValidationError("Debe tener al menos 18 años para usar la aplicación")
        return value

    def validate_phone(self, value):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            user = request.user
        
        if Profile.objects.filter(phone=value).exists() and Profile.objects.get(phone=value).user != user:
            raise serializers.ValidationError("Ya existe un usuario registrado con el mismo número de teléfono")
        return value

### BALANCE RELATED SERIALIZERS
def amount_is_valid(value):
    try:
        val=float(value)
        return round(Decimal(val), 2)
    except:
        raise ValidationError('Petición inválida, el número máximo de decimales permitidos es 2 y ha de usarse "." siguiendo el formato internacional')

class SwaggerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['phone', 'birthdate', 'is_banned']


class SwaggerProfileBalanceSerializer(serializers.Serializer):
    
    funds = serializers.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'), validators=[amount_is_valid])
    funds_currency = serializers.CharField(max_length=3, default='EUR')

class SwaggerBalanceRechargeSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'), validators=[amount_is_valid])


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


### RATINGS SERIALIZERS
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

class SwaggerRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['rate', 'comment']

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
        'zone', 'limited_mobility', 'status', 'observation', 'rated', 'announcement', 'vehicle']

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
        fields = ['id','date','cancelled','rated','announcement', 'user']
        
class SwaggerCreateReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['announcement']

class SwaggerUpdateReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['date','cancelled','rated','announcement', 'user']

class SwaggerCancelReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['cancelled']

class SimpleReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'rated', 'cancelled']


### GEOLOCATION SERIALIZERS

class GeolocationToAddressSerializer(serializers.Serializer):
    longitude = serializers.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    latitude=serializers.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])  

class GeolocationToCoordinatesSerializer(serializers.Serializer):
    location = serializers.CharField(max_length=1024)

### REGISTER SERIALIZERS

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    profile = ProfileRegisterSerializer()  
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
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario registrado con el mismo email")
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

class AnnouncementNestedReservationsSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only = True)
    reservation_set = SimpleReservationSerializer(many=True)
    class Meta:
        model = Announcement
        fields = ['id','date','wait_time','price','allow_wait','location', 'longitude', 'latitude',
        'zone', 'limited_mobility', 'status', 'observation', 'rated', 'cancelled', 'announcement', 'vehicle', 'reservation_set']