from asyncio import ProactorEventLoop
from pyexpat import model
from django.shortcuts import render
import jwt
from django.contrib.auth.models import User
from .models import Profile, User, Vehicle, Announcement, Reservation
from api.serializers import UserSerializer,VehicleSerializer, ProfileSerializer
import datetime
from api.serializers import VehicleSerializer, AnnouncementSerializer, ReservationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters, generics
from rest_framework.permissions import IsAuthenticated,BasePermission
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken,BlacklistedToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt import views as jwt_views
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema


class VehiclesAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self,pk):
        try:
            return Vehicle.objects.get(id=pk)
        except Vehicle.DoesNotExist:
            raise Http404

    @swagger_auto_schema(request_body=VehicleSerializer)
    def post(self,request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = VehicleSerializer(data=data)

        query = Vehicle.objects.filter(license_plate=data["license_plate"],user=data["user"])
        if serializer.is_valid() and not query:
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request, pk):
        vehicle = self.get_object(pk)
        serializer = VehicleSerializer(vehicle, data=request.data)

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
        return Response(VehicleSerializer(get_object_or_404(Vehicle, pk=pk)).data)

class UsersAPI(APIView):
    permission_classes = [IsAuthenticated]
    model = Profile

    def get_object(self,pk):
        try:
            return Profile.objects.get(id=pk)
        except Profile.DoesNotExist:
            raise Http404

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
    
class ProfileApi(APIView):
    permission_classes = [IsAuthenticated]
    model=Profile

    def get_object(self,pk):
        try:
            return Profile.objects.get(id=pk)
        except Profile.DoesNotExist:
            raise Http404

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

    @swagger_auto_schema(request_body=AnnouncementSerializer)
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

    @swagger_auto_schema(request_body=AnnouncementSerializer)
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
            res=Response("No se ha encontrado tal reserva en tu historial",status.HTTP_400_BAD_REQUEST)
        return res      

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
            response=Response("No se han encontrado reservas para este usuario",status=status.HTTP_200_OK)
        return response

    @swagger_auto_schema(request_body=ReservationSerializer)        
    def post(self, request):
        announcementToBook=get_object_or_404(Announcement,pk=request.data['announcement'])
        temp_date=datetime.datetime.now()
        if Reservation.objects.filter(announcement=announcementToBook):
            response= Response("El anuncio ya está reservado.",status=status.HTTP_409_CONFLICT)
        elif announcementToBook.user == request.user:
            response= Response("No puedes reservar tu propio anuncio.",status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            Reservation.objects.create(date=datetime.datetime(temp_date.year, temp_date.month, temp_date.day, temp_date.hour, temp_date.minute), n_extend=0,
            user=request.user,announcement=announcementToBook)
            response=Response("La reserva ha sido creada",status=status.HTTP_201_CREATED)

        return response

