from django.contrib import admin
from .models import Rating, Profile, Vehicle, Reservation, Announcement

# Register your models here.
admin.site.register(Rating)
admin.site.register(Profile)
admin.site.register(Vehicle)
admin.site.register(Reservation)
admin.site.register(Announcement)