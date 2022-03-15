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
    
    def put(self,request):
        post = self.get_object(request.vehicle.id)
        serializer = VehicleSerializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self):
        post = self.get_object(Vehicle.id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)

class UpdateDeleteUser (APIView): 
    permission_classes = [IsAuthenticated&IsTokenValid]
    model = Profile

    def put(self,request):
        post = self.get_object(request.user.id)
        serializer = ProfileSerializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self):
        post = self.get_object(Profile.id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
