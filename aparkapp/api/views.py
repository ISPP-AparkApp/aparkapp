from django.shortcuts import render
import jwt
from .models import Profile, User, Vehicle
from api.serializers import UserSerializer,VehicleSerializer, ProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken,BlacklistedToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt import views as jwt_views
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

    def get_object(self,pk):
        try:
            return Vehicle.objects.get(id=pk)
        except Vehicle.DoesNotExist:
            raise Http404

    def post(self,request):
        serializer = VehicleSerializer(data=request.data)

        query = Vehicle.objects.filter(license_plate=request.data["license_plate"],user=request.data["user"])
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
        vehicle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get(self, request, pk):
        vehicle = self.get_object(pk)
        serializer = VehicleSerializer(vehicle, data=request.data)

        if serializer.is_valid():
            return Response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)

class UsersAPI(APIView): 
    permission_classes = [IsAuthenticated&IsTokenValid]
    model = Profile

    def get_object(self,pk):
        try:
            return Profile.objects.get(id=pk)
        except Profile.DoesNotExist:
            raise Http404

    def put(self,request,pk):
        post = self.get_object(pk)
        serializer = ProfileSerializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)