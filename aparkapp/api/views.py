from urllib import request, response
from django.http import Http404, HttpResponse
from django.shortcuts import render
from api.models import Reservation
from api.serializers import AnnouncementSerializer
from api.models import Announcement

from rest_framework import filters, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.

class AnnouncementsAPI(generics.ListAPIView):
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
        current_user = request.user
        if current_user.is_authenticated:
            announcements = self.filter_queryset(self.get_queryset())
            serializer_class = AnnouncementSerializer(announcements,many=True)
            return Response(serializer_class.data)
        else:
            return  Response({"detail": "Unauthorized"},status=status.HTTP_401_UNAUTHORIZED)


class AnnouncementAPI(APIView):
    def get_object(self,pk):
        try:
            return Announcement.objects.get(id=pk)
        except Announcement.DoesNotExist:
            raise Http404
            
    def get(self,request,pk):
        current_user = request.user
        an = self.get_object(pk)
        if current_user.is_authenticated:
            res_list = Reservation.objects.filter(user=current_user)
            print(res_list)
            announcement_list = res_list.values_list('announcement')

            if pk in announcement_list:   
                serializer = AnnouncementSerializer(an)
                return Response(serializer.data)
            else:
                return Response({"detail": "Unauthorized"},status=status.HTTP_401_UNAUTHORIZED)