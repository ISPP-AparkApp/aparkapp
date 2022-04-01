from django.contrib.auth.models import User
from .models import Profile, User, Vehicle, Announcement, Reservation
from api.serializers import UserSerializer,VehicleSerializer, ProfileSerializer
import datetime
from api.geolocator import coordinates_to_address
from .models import Vehicle, Announcement, Reservation, User
from api.serializers import (VehicleSerializer, AnnouncementSerializer, ReservationSerializer, 
SwaggerVehicleSerializer, SwaggerAnnouncementSerializer,SwaggerCreateReservationSerializer, UserSerializer,
SwaggerUpdateReservationSerializer, GeolocationToAddressSerializer, GeolocationToCoordinatesSerializer, SwaggerVehicleSerializer,
VehicleSerializerId, SwaggerVehicleSerializerId,SwaggerUserSerializer,SwaggerProfileSerializer, SwaggerUpdateAnnouncementSerializer)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters, generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from api.geolocator import coordinates_to_address
from api.serializers import (AnnouncementSerializer,
                             GeolocationToAddressSerializer,
                             GeolocationToCoordinatesSerializer,
                             ProfileSerializer, ReservationSerializer,
                             SwaggerAnnouncementSerializer,
                             SwaggerCreateReservationSerializer,
                             SwaggerProfileSerializer,
                             SwaggerUpdateAnnouncementSerializer,
                             SwaggerUpdateReservationSerializer,
                             SwaggerUserSerializer, SwaggerVehicleSerializer,
                             SwaggerVehicleSerializerId, UserSerializer,
                             VehicleSerializer, VehicleSerializerId,
                             SwaggerCancelAnnouncementSerializer,SwaggerCancelReservationSerializer,
                             RegisterSerializer, 
                             AnnouncementNestedVehicleSerializer, UserNestedProfileSerializer)

from .geolocator import address_to_coordinates, coordinates_to_address
from .models import Announcement, Profile, Reservation, User, Vehicle
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

class VehiclesAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de vehiculos"]

    @swagger_auto_schema(request_body=SwaggerVehicleSerializer)
    def post(self,request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = VehicleSerializer(data=data)

        query = Vehicle.objects.filter(license_plate=data["license_plate"],user=data["user"])
        if serializer.is_valid() and not query:
            serializer.save()
            return Response({"mensaje":"Vehículo creado con éxito","vehículo":serializer.data},status=status.HTTP_201_CREATED)
        elif query:
            return Response({"error":"El usuario con id " + str(data["user"]) + " ya tiene asignado este vehículo"},status=status.HTTP_409_CONFLICT)
        else:
            return Response({"error":str(serializer.error_messages)},status=status.HTTP_400_BAD_REQUEST)
        
        

class VehiclesIdAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de vehiculos"]

    def get_object(self,pk):
        try:
            return Vehicle.objects.get(id=pk)
        except Vehicle.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(request_body=SwaggerVehicleSerializerId)
    def put(self,request, pk):
        vehicle = self.get_object(pk)
        serializer = VehicleSerializerId(vehicle, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        vehicle = self.get_object(pk)
        data = request.data.copy()
        data['user'] = request.user.id
        query = Vehicle.objects.filter(user=data['user']).count()
        if query > 1:
            vehicle.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response("You have only one vehicle registred",status=status.HTTP_401_UNAUTHORIZED)
    
    def get(self, request, pk):
        return Response(VehicleSerializerId(get_object_or_404(Vehicle, pk=pk)).data)

class UsersVehiclesAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de usuarios"]

    def get(self,request):
        pk = request.user.id
        user = User.objects.get(pk=pk)
        vehicles = Vehicle.objects.filter(user=user)
        vehicle_serializer = VehicleSerializer(vehicles, many=True)
        return Response(vehicle_serializer.data, status=status.HTTP_200_OK)


class UsersAPI(APIView):
    permission_classes = [IsAuthenticated]
    model = Profile
    swagger_tags= ["Endpoints de usuarios"]

    def get_object(self,pk):
        try:
            return Profile.objects.get(id=pk)
        except Profile.DoesNotExist:
            raise Http404

    @swagger_auto_schema(request_body=SwaggerUserSerializer)
    def put(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request):
        pk = request.user.id
        return Response(UserSerializer(get_object_or_404(User, pk=pk)).data)
    
    def delete(self, request):
        pk = request.user.id
        user=get_object_or_404(User,pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de usuarios"]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserNestedProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProfileApi(APIView):
    permission_classes = [IsAuthenticated]
    model=Profile
    swagger_tags= ["Endpoints de perfiles"]

    def get_object(self,pk):
        try:
            return Profile.objects.get(id=pk)
        except Profile.DoesNotExist:
            raise Http404

    @swagger_auto_schema(request_body=SwaggerProfileSerializer)
    def put(self, request, *args, **kwargs):
        pk = request.user.id
        user = self.get_object(pk)
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get(self, request):
        pk = request.user.id
        return Response(ProfileSerializer(get_object_or_404(Profile, pk=pk)).data)


class AnnouncementsAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de anuncios"]

    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)

    serializer_class = AnnouncementSerializer
    search_fields = ('zone','location','longitude','latitude',)
    ordering_fields = ('price',)
    filterset_fields = ('vehicle__type','date')

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


    def get_queryset(self, request):
        res_list = Reservation.objects.all()
        ann_id_list = list(res_list.values_list('announcement', flat=True))
        query = Announcement.objects.exclude(user=request.user).exclude(id__in=ann_id_list)
        
        return query


    def get(self, request):
        announcements = self.filter_queryset(self.get_queryset(request))
        serializer_class = AnnouncementSerializer(announcements,many=True)

        return Response(serializer_class.data)

    @swagger_auto_schema(tags=["Announcement Endpoints"],request_body=SwaggerAnnouncementSerializer)
    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id

        #Coordinates to adress
        coordinates = (float(data['latitude']), float(data['longitude']))
        direction = coordinates_to_address(coordinates)
        try:
            data['location'] = str(direction[0]['display_name'])
        except:
            data['location'] = str(direction[0])

        serializer = AnnouncementSerializer(data=data)
        query = Announcement.objects.filter(date=data["date"], vehicle=data["vehicle"])

        #Validation to publish an announcement with your own vehicles
        user = User.objects.get(pk=request.user.id)
        query2 = Vehicle.objects.filter(user=user)

        if query:
            return Response("Ya existe un anuncio para este vehículo a la misma hora.", status=status.HTTP_401_UNAUTHORIZED)

        if query2:
            vhs = query2.all().values()
            ls = [v['id'] for v in vhs]
            if data['vehicle'] not in ls:
                return Response("No se puede crear un anuncio con un vehículo ajeno.", status=status.HTTP_406_NOT_ACCEPTABLE)

        if serializer.is_valid() and not query:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class myAnnouncementsAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de anuncios"]

    def get(self, request):
        announcements = Announcement.objects.filter(user=request.user)
        serializer_class = AnnouncementNestedVehicleSerializer(announcements,many=True)

        return Response(serializer_class.data)

class AnnouncementsUserAPI(APIView):
    swagger_tags= ["Endpoints de anuncios"]

    def get(self,request):
        pk = request.user.id
        announcements = Announcement.objects.filter(user=pk)
        announcement_serializer = AnnouncementSerializer(announcements, many=True)

        return Response(announcement_serializer.data, status=status.HTTP_200_OK)

class AnnouncementStatusAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de anuncios"]

    def get_object(self,pk):
        try:
            return Announcement.objects.get(id=pk)
        except Announcement.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        low = datetime.datetime.now() - datetime.timedelta(minutes=10)
        major = datetime.datetime.now() + datetime.timedelta(minutes=60)
        announcements =  Announcement.objects.filter(user=pk and status!='Departure', date__gte=low, date__lte=major)
        aux=[]
        for a in announcements:
            aux.append(AnnouncementSerializer(a).data)
        return Response(data=aux,status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=SwaggerUpdateAnnouncementSerializer)
    def put(self,request,pk):
        try:
            if request.data.get("status"):
                announcement_to_update=Announcement.objects.filter(pk=pk)
                if announcement_to_update:
                    announcement_to_update.update(status=request.data["status"])
                    res=Response(status=status.HTTP_204_NO_CONTENT)
            else:
                res=Response("La petición es inválida", status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            res=Response("No existe el anuncio especificado", status=status.HTTP_404_NOT_FOUND)
        
        return res
        
    
class AnnouncementAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de anuncios"]

    def get_object(self,pk):
        try:
            return Announcement.objects.get(id=pk)
        except Announcement.DoesNotExist:
            raise Http404

    def get(self,request,pk):
        an = self.get_object(pk)
        res_list = Reservation.objects.filter(user=request.user)
        announcement_list = list(res_list.values_list('announcement', flat=True))

        if True or pk in announcement_list or request.user==an.user:  ##TODO: Check ALWAYS True
            serializer = AnnouncementNestedVehicleSerializer(an)
            return Response(serializer.data)
        else:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(request_body=SwaggerAnnouncementSerializer)
    def put(self, request, pk):
        announcement = self.get_object(pk)

        data = request.data.copy()
        data['user'] = announcement.user.id

        #Coordinates to address
        coordinates = (float(data['latitude']), float(data['longitude']))
        direction = coordinates_to_address(coordinates)
        try:
            data['location'] = str(direction[0]['display_name'])
        except:
            data['location'] = str(direction[0])
        serializer = AnnouncementSerializer(announcement, data=data)
        query = Announcement.objects.filter(date=data["date"], vehicle=data["vehicle"])
        
        if query and query.get().id != pk:
            return Response("Ya existe un anuncio para este vehículo a la misma hora.",status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
            try:
                announcement = self.get_object(pk)
                if announcement.user.id == request.user.id:
                    announcement.delete()
                    return Response(status.HTTP_200_OK)
                else:
                    return Response("No se puede borrar un anuncio que usted no ha publicado.", status.HTTP_401_UNAUTHORIZED)
            except:
                return Response("No existe el anuncio que desea borrar.", status.HTTP_400_BAD_REQUEST)

class CancelAnnouncementsAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de anuncios"]

    @swagger_auto_schema(request_body=SwaggerCancelAnnouncementSerializer)
    def put(self, request, pk):
        try:
            if request.data["cancelled"]:
                announcement_to_update= Announcement.objects.filter(pk=pk)
                if announcement_to_update:
                    announcement_to_update.update(cancelled=request.data["cancelled"])
                    res = Response("El anuncio se ha actualizado con éxito", status=status.HTTP_204_NO_CONTENT)
                else:
                    raise Exception()
            else:
                res = Response("La petición es inválida",status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            res = Response("No existe el anuncio especificado", status=status.HTTP_404_NOT_FOUND)

        return res

class ReservationByAnouncementAPI(APIView):
    swagger_tags= ["Endpoints de reservas"]

    def get(self, request,pk):
        reservation = Reservation.objects.filter(announcement=pk, cancelled=False)
        if reservation: 
            userId = reservation.get().user.id
            user= User.objects.filter(id=userId)
            user_serializer = UserSerializer(user.get())
            res=Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            res=Response("No se ha encontrado ninguna reserva asociada a ese anuncio", status=status.HTTP_404_NOT_FOUND)
        return res


class ReservationAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de reservas"]

    def get(self, request,pk):
        try:
            reservation=Reservation.objects.get(pk=pk)
            res=Response(ReservationSerializer(reservation).data, status=status.HTTP_200_OK)
        except (MultipleObjectsReturned,ObjectDoesNotExist) as e:
            res=Response("No se ha encontrado ninguna reserva con tal identificador", status=status.HTTP_404_NOT_FOUND)
        return res
    
    def delete(self, request, pk):
        try:
            reservation=Reservation.objects.get(pk=pk, user=request.user)
            reservation.cancelled=True
            reservation.announcement=None
            reservation.save()
            res=Response(status.HTTP_200_OK)
        except:
            res=Response("No existe tal reserva en tu historial",status.HTTP_404_NOT_FOUND)
        return res   

    @swagger_auto_schema(request_body=SwaggerUpdateReservationSerializer)        
    def put(self, request, pk):
        reservation_to_update=get_object_or_404(Reservation,pk=pk)
        serializer = ReservationSerializer(reservation_to_update, data=request.data)
        announcement_to_book=get_object_or_404(Announcement,pk=request.data['announcement'])
        if Reservation.objects.filter(announcement=request.data['announcement'], cancelled=False):
            response=Response("El anuncio especificado ya está reservado", status.HTTP_400_BAD_REQUEST)
        elif announcement_to_book.user == request.user:
            response= Response("No puedes asginar tu propio anuncio.",status=status.HTTP_405_METHOD_NOT_ALLOWED)
        elif serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            response=Response("Los datos de la reserva introducidos no son válidos", status.HTTP_400_BAD_REQUEST)
        return response

class ReservationsAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de reservas"]
    
    # Returns own reservations
    def get(self, request):
        reservations=Reservation.objects.filter(user=request.user)
        reservations_data=[]
        for r in reservations:
            reservations_data.append(ReservationSerializer(r).data)
        return Response(data=reservations_data,status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=SwaggerCreateReservationSerializer)        
    def post(self, request):
        announcement_to_book=get_object_or_404(Announcement,pk=request.data['announcement'])
        temp_date=make_aware(datetime.datetime.now())
        if Reservation.objects.filter(announcement=announcement_to_book):
            response= Response("El anuncio ya está reservado.",status=status.HTTP_409_CONFLICT)
        elif announcement_to_book.user == request.user:
            response= Response("No puedes reservar tu propio anuncio.",status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            Reservation.objects.create(date=datetime.datetime(temp_date.year, temp_date.month, temp_date.day, temp_date.hour, temp_date.minute), 
            n_extend=0, cancelled=False, rated=False, user=request.user, announcement=announcement_to_book)
            response=Response("La reserva ha sido creada",status=status.HTTP_201_CREATED)

        return response

class CancelReservationAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de reservas"]

    @swagger_auto_schema(request_body=SwaggerCancelReservationSerializer)
    def put(self, request, pk):
        try:
            if request.data["cancelled"]:
                reservation_to_update= Reservation.objects.filter(pk=pk)
                if reservation_to_update:
                    reservation_to_update.update(cancelled=request.data["cancelled"])
                    res = Response("La reserva se ha actualizado con éxito", status=status.HTTP_204_NO_CONTENT)
                else:
                    raise Exception()
            else:
                res = Response("La petición es inválida",status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            res = Response("No existe la reserva especificada", status=status.HTTP_404_NOT_FOUND)

        return res

class GeolocationToCoordinatesAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de geolocalización"]

    @swagger_auto_schema(request_body=GeolocationToCoordinatesSerializer) 
    def post(self, request):
        serializer = GeolocationToCoordinatesSerializer(data=request.data)
        if serializer.is_valid():
            response=Response(address_to_coordinates(request.data['location'],
            request.data.get('country_code', 'ES'), bool(request.data.get('one_result', 'false')),
            request.data.get('raw', 'true')), status=status.HTTP_200_OK)            
        else:
            response=Response("Petición incorrecta", status=status.HTTP_400_BAD_REQUEST)
        return response

class GeolocationToAddressAPI(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags= ["Endpoints de geolocalización"]

    @swagger_auto_schema(request_body=GeolocationToAddressSerializer) 
    def post(self, request):
        serializer = GeolocationToAddressSerializer(data=request.data)
        if serializer.is_valid():
            response=Response(coordinates_to_address((float(request.data['longitude']),
            float(request.data['latitude'])), bool(request.data.get('one_result', 'false'))), status=status.HTTP_200_OK)
        else:
            response=Response("Petición incorrecta", status=status.HTTP_400_BAD_REQUEST)
        return response
        
class RegisterAPI(APIView):
    permision_classes = (AllowAny,)
    swagger_tags=["Endpoints de registro"]

    def return_errors(self,dic):
        err = {}
        keys = dic.keys()
        for k in keys:
            if k == 'profile':
                profile = dic[k]
                if isinstance(profile, list):
                    err[k] = profile[0].capitalize()
                else:
                    for p in profile.keys():
                        err[p] = profile[p][0].capitalize()
            elif k == 'vehicles':
                vehicles = dic[k]
                for v in vehicles:
                    if isinstance(v, dict):
                        for vKey in v.keys():
                            if vKey == 'license_plate':
                                err[vKey] = v[vKey][0].replace('este license plate','esta matrícula').replace('vehicle','un vehículo').capitalize() 
                            elif vKey == 'type':
                                x = v[vKey][0].split("\"")
                                title = x[1] + x[2]
                                err[vKey] = title
                            else:
                                err[vKey] = v[vKey][0].capitalize()
                    else:
                        err[k] = vehicles[0].capitalize()
            elif k == 'password':
                    x = dic[k][0].split(".")
                    title = x[0] + '.'+ x[1] + '.'
                    err[k] = title
            else:
                    err[k] = dic[k][0].capitalize()
        
        return err

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        data = request.data.copy()
        serializer_data = RegisterSerializer(data=data)
        if serializer_data.is_valid():
            serializer_data.save()
            return Response({"mensaje":"Registrado correctamente","user":serializer_data.data},status=status.HTTP_201_CREATED)       
        else:
            err = self.return_errors(serializer_data.errors)
            return Response({"error":err},status=status.HTTP_400_BAD_REQUEST)
