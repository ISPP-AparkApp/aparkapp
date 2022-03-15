from django.shortcuts import render
import jwt
from .models import Vehicle, Announcement, Reservation
from api.serializers import VehicleSerializer, AnnouncementSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters, generics
from rest_framework.permissions import IsAuthenticated,BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken,BlacklistedToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt import views as jwt_views
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404

class IsTokenValid(BasePermission):
    def has_permission(self, request, view):
        user_id = request.user.id
        token = request.headers['Authorization'].split()[1]          
        is_allowed_user = True
        try:
            tokens = OutstandingToken.objects.filter(user_id=request.user.id)
            is_blackListed = BlacklistedToken.objects.get(token=tokens[len(tokens)-1])
            if is_blackListed:
                return False
        except BlacklistedToken.DoesNotExist:
            is_allowed_user = True
        return is_allowed_user

# Create your views here.
class VehiclesAPI(APIView):
    # View protected
    permission_classes = [IsAuthenticated&IsTokenValid]

    def post(self,request):
        serializer = VehicleSerializer(data=request.data)

        query = Vehicle.objects.filter(license_plate=request.data["license_plate"],user=request.data["user"])
        if serializer.is_valid() and not query:
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)

class AnnouncementsAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated&IsTokenValid]

    filter_backends = (filters.SearchFilter, filters.OrderingFilter,DjangoFilterBackend)

    search_fields = ('zone','location',)
    ordering_fields = ('price',)
    filterset_fields = ('vehicle__type',)

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_queryset(self):
        return Announcement.objects.all()

    def get(self,request):
        announcements = self.filter_queryset(self.get_queryset())
        serializer_class = AnnouncementSerializer(announcements,many=True)

        return Response(serializer_class.data)

class AnnouncementAPI(APIView):
    permission_classes = [IsAuthenticated&IsTokenValid]

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