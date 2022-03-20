import datetime
from .models import Vehicle, Announcement, Reservation, User
from api.serializers import (VehicleSerializer, AnnouncementSerializer, ReservationSerializer, 
SwaggerVehicleSerializer, SwaggerAnnouncementSerializer,SwaggerCreateReservationSerializer, 
SwaggerUpdateReservationSerializer, GeolocationToAddressSerializer, GeolocationToCoordinatesSerializer)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters, generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from django.utils.timezone import make_aware
from .geolocator import coordinates_to_address, address_to_coordinates

class VehiclesAPI(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=SwaggerVehicleSerializer)
    def post(self,request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = VehicleSerializer(data=data)

        query = Vehicle.objects.filter(license_plate=data["license_plate"],user=data["user"])
        if serializer.is_valid() and not query:
            serializer.save()
            return Response({"mensaje":"Vehículo creado con éxito","vehículo":serializer.data},status=status.HTTP_201_CREATED)
        return Response({"error":"El usuario con id " + str(data["user"]) + " ya tiene asignado este vehículo"},status=status.HTTP_400_BAD_REQUEST)


class UsersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        pk = request.user.id
        user = User.objects.get(pk=pk)
        vehicles = Vehicle.objects.filter(user=user)
        vehicle_serializer = VehicleSerializer(vehicles, many=True)
        return Response(vehicle_serializer.data, status=status.HTTP_200_OK)

class AnnouncementsAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)

    serializer_class = AnnouncementSerializer
    search_fields = ('zone','location','longitude','latitude',)
    ordering_fields = ('price',)
    filterset_fields = ('vehicle__type',)

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


    def get_queryset(self):
        return Announcement.objects.all()


    def get(self, request):
        announcements = self.filter_queryset(self.get_queryset())
        serializer_class = AnnouncementSerializer(announcements,many=True)

        return Response(serializer_class.data)

    @swagger_auto_schema(request_body=SwaggerAnnouncementSerializer)
    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = AnnouncementSerializer(data=data)
        query = Announcement.objects.filter(date=data["date"], vehicle=data["vehicle"])

        if query:
            return Response("There's already an announcement for this vehicle at the same time.",status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid() and not query:
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)    

class AnnouncementAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self,pk):
        try:
            return Announcement.objects.get(id=pk)
        except Announcement.DoesNotExist:
            raise Http404

    def get(self,request,pk):
        an = self.get_object(pk)
        res_list = Reservation.objects.filter(user=request.user)
        aux = list(res_list.values_list('announcement'))
        announcement_list = []

        for announcement in aux:
            announcement_list.append(announcement[0])

        if pk in announcement_list:   
            serializer = AnnouncementSerializer(an)
            return Response(serializer.data)
        else:
            return Response({"detail": "Unauthorized"},status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(request_body=SwaggerAnnouncementSerializer)
    def put(self, request, pk):
        announcement = self.get_object(pk)

        serializer = AnnouncementSerializer(announcement, data=request.data)
        query = Announcement.objects.filter(date=request.data["date"], vehicle=request.data["vehicle"])
        if query:
            return Response("There's already an announcement for this vehicle at the same time.",status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid() and not query:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        announcement = self.get_object(pk)
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReservationAPI(APIView):
    
    def get(self, request,pk):
        return Response(ReservationSerializer(get_object_or_404(Reservation, pk=pk)).data)
    
    def delete(self, request, pk):
        try:
            reservation=Reservation.objects.get(pk=pk, user=request.user)
            reservation.cancelled=True
            reservation.announcement=None
            reservation.save()
            res=Response("La reserva se ha borrado con éxito",status.HTTP_204_NO_CONTENT)
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
            return Response("La reserva ha sido actualizada", status=status.HTTP_204_NO_CONTENT)
        else:
            response=Response("Los datos de la reserva introducidos no son válidos", status.HTTP_400_BAD_REQUEST)
        return response

class ReservationsAPI(APIView):

    # Returns own reservations
    def get(self, request):
        reservations=Reservation.objects.filter(user=request.user)
        reservations_data=[]
        if reservations:
            for r in reservations:
                reservations_data.append(ReservationSerializer(r).data)
            response=Response(data=reservations_data,status=status.HTTP_200_OK)
        else:
            response=Response("No se han encontrado reservas para este usuario",status=status.HTTP_404_NOT_FOUND)
        return response

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


class GeolocationToCoordinatesAPI(APIView):

    # I don't like this validation seems inefficient but not time to redo it for now
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
    
    @swagger_auto_schema(request_body=GeolocationToAddressSerializer) 
    def post(self, request):
        serializer = GeolocationToAddressSerializer(data=request.data)
        if serializer.is_valid():
            response=Response(coordinates_to_address((float(request.data['longitude']),
            float(request.data['latitude'])), bool(request.data.get('one_result', 'false'))), status=status.HTTP_200_OK)
        else:
            response=Response("Petición incorrecta", status=status.HTTP_400_BAD_REQUEST)
        return response
