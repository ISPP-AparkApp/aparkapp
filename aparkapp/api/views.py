from django.shortcuts import render
import jwt
from .models import User, Vehicle
from api.serializers import UserSerializer,VehicleSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken,BlacklistedToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt import views as jwt_views
import uuid



# Create your views here.
class VehiclesAPI(APIView):
    # View protected
    permission_classes = [IsAuthenticated]

    def post(self,request):
        data = request.data
        data['user'] = request.user.id
        print(data)
        serializer = VehicleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)








