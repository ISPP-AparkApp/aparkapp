from django.contrib.sessions.models import Session
from django.shortcuts import render
from .models import User, Vehicle

from api.serializers import UserSerializer,VehicleSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.http import Http404
from datetime import datetime
from .authentication_mixins import Authentication

# Create your views here.

class VehiclesAPI(Authentication,APIView):
    def post(self,request):
        serializer = VehicleSerializer(data=request.data)

        query = Vehicle.objects.filter(license_plate=request.data["license_plate"],user=request.data["user"])
        if serializer.is_valid() and not query:
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class UserToken(APIView):
    # Send username as param
    def get(self,request):
        username = request.GET.get('username')
        try:
            user_token = Token.objects.get(user = UserSerializer().Meta.model.objects.filter(username = username).first())
            return Response({'TOKEN': user_token.key})
        except:
            return Response({'error': 'Incorrect credentials'},status=status.HTTP_400_BAD_REQUEST)


class Login(ObtainAuthToken):
    def post(self,request):
        login_serializer = self.serializer_class(data=request.data,context={'request':request})
        if login_serializer.is_valid():
            user = login_serializer.validated_data['user']
            if user.is_active:
                token,is_created = Token.objects.get_or_create(user=user)
                user_serializer = UserSerializer(user)
                if is_created:
                    return Response({'TOKEN': token.key,'user':user_serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    all_sessions = Session.objects.filter(expire_date__gte = datetime.now())
                    if all_sessions.exists():
                        for session in all_sessions:
                            session_data = session.get_decoded()
                            if user.id == int(session_data.get('_auth_user_id')):
                                session.delete()
                    token.delete()
                    token = Token.objects.create(user=user)
                    return Response({'TOKEN': token.key,'user':user_serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Invalid to login'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Incorrect username or password'}, status=status.HTTP_400_BAD_REQUEST)

class Logout(APIView):
    def post(self,request):
        try:
            #Send token as param
            token = Token.objects.filter(key=request.GET.get('token')).first()
            if token:
                user = token.user
                # DELETE all sessions
                all_sessions = Session.objects.filter(expire_date__gte = datetime.now())
                if all_sessions.exists():
                    for session in all_sessions:
                        session_data = session.get_decoded()
                        if user.id == int(session_data.get('_auth_user_id')):
                            session.delete()
                session_message = "User sessions deleted"
                #Delete token
                token.delete()
                token_message = "Token deleted"

                return Response({'session_message': session_message,'token_message':token_message}, status=status.HTTP_201_CREATED)
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'error': 'Token not found'}, status=status.HTTP_409_CONFLICT)

            