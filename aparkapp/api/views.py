import datetime

from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import make_aware
from api.auxiliary import post_reservation_logic
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from api.serializers import (AnnouncementNestedVehicleSerializer,
                             AnnouncementSerializer,
                             GeolocationToAddressSerializer,
                             GeolocationToCoordinatesSerializer,
                             ProfileSerializer, RegisterSerializer,
                             ReservationSerializer,
                             SwaggerAnnouncementSerializer,
                             SwaggerCancelAnnouncementSerializer,
                             SwaggerCancelReservationSerializer,
                             SwaggerCreateReservationSerializer,
                             SwaggerProfileSerializer,
                             SwaggerUpdateAnnouncementSerializer,
                             SwaggerUpdateReservationSerializer,
                             SwaggerUserSerializer, SwaggerVehicleSerializer,
                             SwaggerVehicleSerializerId,
                             UserNestedProfileSerializer, UserSerializer,
                             VehicleSerializer, VehicleSerializerId,
                             RatingSerializer, SwaggerRatingSerializer)


from rest_framework_simplejwt.views import TokenObtainPairView
from .geolocator import address_to_coordinates, coordinates_to_address
from .models import Announcement, Profile, Rating, Reservation, User, Vehicle
from django.contrib.auth import authenticate
from rest_framework import permissions, exceptions

class NotIsBanned(permissions.BasePermission):
    message = "El usuario está baneado"
    def has_permission(self, request, view):
        profile = Profile.objects.get(user__username=request.user.username)
        if profile.is_banned:
            raise exceptions.PermissionDenied(detail=self.message) 
        return True

class Login(TokenObtainPairView):
    serialer_class = TokenObtainPairSerializer

    def post(self,request,*args,**kwargs):
        username = request.data.get('username','')
        password = request.data.get('password','')
        user = authenticate(username=username, password=password)
        if user:
            login_serializer = self.serialer_class(data=request.data)
            if login_serializer.is_valid():
                profile = Profile.objects.get(user__username=username)
                if profile.is_banned:
                    return Response({'error': 'El usuario está bloqueado'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response({
                        'access': login_serializer.validated_data['access'],
                        'refresh': login_serializer.validated_data['refresh'],
                        'message': 'Inicio de sesión realizado con éxito'
                    }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Contraseña o nombre de usuario incorrectos'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Contraseña o nombre de usuario incorrectos'}, status=status.HTTP_400_BAD_REQUEST)

class VehiclesAPI(APIView):
    permission_classes = [IsAuthenticated & NotIsBanned]
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
    permission_classes = [IsAuthenticated & NotIsBanned]
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
    permission_classes = [IsAuthenticated & NotIsBanned]
    swagger_tags= ["Endpoints de usuarios"]

    def get(self,request):
        pk = request.user.id
        user = User.objects.get(pk=pk)
        vehicles = Vehicle.objects.filter(user=user)
        vehicle_serializer = VehicleSerializer(vehicles, many=True)
        return Response(vehicle_serializer.data, status=status.HTTP_200_OK)


class UsersAPI(APIView):
    permission_classes = [IsAuthenticated & NotIsBanned]
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
    permission_classes = [IsAuthenticated & NotIsBanned]
    swagger_tags= ["Endpoints de usuarios"]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserNestedProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProfileApi(APIView):
    permission_classes = [IsAuthenticated & NotIsBanned]
    model=Profile
    swagger_tags= ["Endpoints de perfiles"]

    def get_object(self,user):
        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            raise Http404

    @swagger_auto_schema(request_body=SwaggerProfileSerializer)
    def put(self, request, *args, **kwargs):
        user = request.user
        profile = self.get_object(user)
        serializer = ProfileSerializer(profile,data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get(self, request):

        return Response(ProfileSerializer(get_object_or_404(Profile, user=request.user)).data)


class AnnouncementsAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated & NotIsBanned]
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
        res_list = Reservation.objects.filter(cancelled=False)
        ann_id_list = list(res_list.values_list('announcement', flat=True))
        query = Announcement.objects.exclude(user=request.user).exclude(id__in=ann_id_list).exclude(
            cancelled=True).exclude(date__lt=make_aware(datetime.datetime.now()))
        
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
        except Exception as e:
            data['location'] = str(direction[0])

        serializer = AnnouncementSerializer(data=data)
        query = Announcement.objects.filter(date=data["date"], vehicle=data["vehicle"])

        #Validation to publish an announcement with your own vehicles
        user = User.objects.get(pk=request.user.id)
        query2 = Vehicle.objects.filter(user=user)

        if query:
            if query.get().cancelled:
                res=Response("El anuncio ya está reservado", status=status.HTTP_409_CONFLICT)    
        if query2:
            vhs = query2.all().values()
            ls = [v['id'] for v in vhs]
            if data['vehicle'] not in ls:
                return Response("No se puede crear un anuncio con un vehículo ajeno.", status=status.HTTP_406_NOT_ACCEPTABLE)

        if serializer.is_valid() and not query:
            serializer.save()
            res = Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            res=Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return res    

class myAnnouncementsAPI(APIView):
    permission_classes = [IsAuthenticated & NotIsBanned]
    swagger_tags= ["Endpoints de anuncios"]

    def get(self, request):
        announcements = Announcement.objects.filter(user=request.user).order_by('date')
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
    permission_classes = [IsAuthenticated & NotIsBanned]
    swagger_tags= ["Endpoints de anuncios"]

    def get_object(self,pk):
        try:
            return Announcement.objects.get(id=pk)
        except Announcement.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        low = make_aware(datetime.datetime.now() - datetime.timedelta(minutes=10))
        major = make_aware(datetime.datetime.now() + datetime.timedelta(minutes=60))
        announcements =  Announcement.objects.filter(user=pk and status!='Departure', date__gte=low, date__lte=major)
        aux=[]
        for a in announcements:
            aux.append(AnnouncementSerializer(a).data)
        return Response(data=aux,status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=SwaggerUpdateAnnouncementSerializer)
    def put(self,request,pk):
        try:
            request_status= request.data.get("status")
            if request_status:
                announcement_to_update=Announcement.objects.get(pk=pk)
                if announcement_to_update:
                    if request_status=="AcceptDelay":
                        if announcement_to_update.n_extend>3:
                            res=Response("error: n_extend es mayor o igual a 3",status=status.HTTP_400_BAD_REQUEST)
                        else:
                            announcement_to_update.status = request_status
                            announcement_to_update.wait_time += 5
                            announcement_to_update.n_extend += 1
                            announcement_to_update.save()
                            res=Response(status=status.HTTP_204_NO_CONTENT)
                    else:
                        announcement_to_update.status = request_status
                        announcement_to_update.save()
                        res=Response(status=status.HTTP_204_NO_CONTENT)
            else:
                res=Response("La petición es inválida", status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            res=Response("No existe el anuncio especificado", status=status.HTTP_404_NOT_FOUND)
        
        return res
        
    
class AnnouncementAPI(APIView):
    permission_classes = [IsAuthenticated & NotIsBanned]
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

        if pk in announcement_list or request.user==an.user: 
            serializer = AnnouncementNestedVehicleSerializer(an)
            return Response(serializer.data)
        else:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(request_body=SwaggerAnnouncementSerializer)
    def put(self, request, pk):
        announcement = self.get_object(pk)
        res_list = Reservation.objects.all()
        announcement_list = list(res_list.values_list('announcement', flat=True))

        if request.user != announcement.user:
            return Response("No puede editar un anuncio de otro usuario", status=status.HTTP_401_UNAUTHORIZED)
        elif pk in announcement_list:
            return Response("No puede editar un anuncio reservado", status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
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
            except Exception as e:
                return Response("No existe el anuncio que desea borrar.", status.HTTP_400_BAD_REQUEST)

class CancelAnnouncementsAPI(APIView):
    permission_classes = [IsAuthenticated & NotIsBanned]
    swagger_tags= ["Endpoints de anuncios"]

    @swagger_auto_schema(request_body=SwaggerCancelAnnouncementSerializer)
    def put(self, request, pk):
        try:
            announcement_to_update= Announcement.objects.filter(pk=pk)
            res_list = Reservation.objects.all()
            announcement_list = list(res_list.values_list('announcement', flat=True))
            if request.user != announcement_to_update[0].user:
                return Response("No puede cancelar un anuncio de otro usuario", status=status.HTTP_401_UNAUTHORIZED)
            if announcement_to_update and pk not in announcement_list:
                announcement_to_update.update(cancelled=request.data["cancelled"])
                res = Response(status=status.HTTP_204_NO_CONTENT)
            elif pk in announcement_list:
                res = Response("No puede cancelar un anuncio reservado", status=status.HTTP_405_METHOD_NOT_ALLOWED)
            else:
                raise Exception()
        except Exception as e:
            res = Response("No existe el anuncio especificado o la petición es inválida", status=status.HTTP_404_NOT_FOUND)

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
    permission_classes = [IsAuthenticated & NotIsBanned]
    swagger_tags= ["Endpoints de reservas"]

    def get(self, request,pk):
        try:
            
            reservation=Reservation.objects.get(pk=pk)
            
            if request.user == reservation.user:
                res=Response(ReservationSerializer(reservation).data, status=status.HTTP_200_OK)
            else:
                res=Response("No puede ver las reservas de otros usuarios", status=status.HTTP_401_UNAUTHORIZED)
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
        except (MultipleObjectsReturned,ObjectDoesNotExist) as e:
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
    permission_classes = [IsAuthenticated & NotIsBanned]
    swagger_tags= ["Endpoints de reservas"]
    
    # Returns own reservations
    def get(self, request):
        reservations=Reservation.objects.filter(user=request.user).order_by('date')
        reservations_data=[]
        for r in reservations:
            reservations_data.append(ReservationSerializer(r).data)
        return Response(data=reservations_data,status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=SwaggerCreateReservationSerializer)        
    def post(self, request):
        return post_reservation_logic(request)

class CancelReservationAPI(APIView):
    permission_classes = [IsAuthenticated & NotIsBanned]
    swagger_tags= ["Endpoints de reservas"]

    @swagger_auto_schema(request_body=SwaggerCancelReservationSerializer)
    def put(self, request, pk):
        try:
            reservation_to_update= Reservation.objects.filter(pk=pk)
            if reservation_to_update:
                reservation_to_update.update(cancelled=request.data["cancelled"])
                res = Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise Exception()
        except Exception:
            res = Response("No existe la reserva especificada o la petición es inválida", status=status.HTTP_404_NOT_FOUND)

        return res

class GeolocationToCoordinatesAPI(APIView):
    permission_classes = [IsAuthenticated & NotIsBanned]
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
    permission_classes = [IsAuthenticated & NotIsBanned]
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
        serializer_data = RegisterSerializer(data=data, context={'request': request})
        if serializer_data.is_valid():
            serializer_data.save()
            return Response({"mensaje":"Registrado correctamente","user":serializer_data.data},status=status.HTTP_201_CREATED)       
        else:
            err = self.return_errors(serializer_data.errors)
            return Response({"error":err},status=status.HTTP_400_BAD_REQUEST)

class RatingAPI(APIView):
    permission_classes = [IsAuthenticated & NotIsBanned]
    swagger_tags=["Endpoints de valoraciones"]

    def get(self, request, pk):
        try:
            ratings = Rating.objects.filter(user=pk)
            serializer_class = RatingSerializer(ratings, many=True)
            return Response(serializer_class.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error":"No se han encontrado el usuario"}, status=status.HTTP_404_NOT_FOUND)

class CreateRatingAPI(APIView):
    permission_classes = [IsAuthenticated & NotIsBanned]
    swagger_tags=["Endpoints de valoraciones"]

    @swagger_auto_schema(request_body=SwaggerRatingSerializer)
    def post(self,request, object, pk):
        data = request.data.copy()

        if object=="announcement":
            obj = get_object_or_404(Announcement,pk=pk)
            res_list = Reservation.objects.filter(user=request.user).filter(cancelled=False)
            ann_id_list = list(res_list.values_list('announcement', flat=True))

            if pk not in ann_id_list:
                return Response("No puede valorar un anuncio que no ha reservado", status=status.HTTP_401_UNAUTHORIZED)
            elif obj.rated == True:
                return Response("El anuncio ya ha sido valorado", status=status.HTTP_405_METHOD_NOT_ALLOWED)
            else:
                data['user'] = obj.user.id
                serializer_data = RatingSerializer(data=data)     

        elif object=="reservation":
            obj = get_object_or_404(Reservation,pk=pk)
            owner_of_Announcement = obj.announcement.user
            
            if request.user != owner_of_Announcement:
                return Response("No puede valorar una reserva cuyo anuncio asociado no le pertenece", status=status.HTTP_401_UNAUTHORIZED)
            elif obj.rated == True:
                return Response("La reserva ya ha sido valorado", status=status.HTTP_405_METHOD_NOT_ALLOWED)
            else:
                data['user'] = obj.user.id
                serializer_data = RatingSerializer(data=data)
        else:
            return Response({"error":"Las únicas urls válidas son rating/announcement/pk y rating/reservation/pk"}, status=status.HTTP_409_CONFLICT)

        if serializer_data.is_valid():
                obj.rated = True
                obj.save()
                serializer_data.save()
                ratings = Rating.objects.filter(user=data["user"]).filter(rate=1)
                profile_user = Profile.objects.get(user=data["user"])
                if len(ratings) >= 10:
                    profile_user.is_banned = True
                    profile_user.save()
                return Response(serializer_data.data, status=status.HTTP_201_CREATED)
        else:
                return Response(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)

class AnnouncementHasReservationAPI(APIView):
    swagger_tags= ["Endpoints de anuncios"]

    def get(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)
        return Response(Reservation.objects.filter(announcement=announcement).exists())

