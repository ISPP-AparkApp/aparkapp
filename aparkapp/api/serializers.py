from rest_framework import serializers

from api.models import Announcement

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id','date','wait_time','price','allow_wait','location','zone','limited_mobility',
                'status','observation','rated','vehicle','user']
