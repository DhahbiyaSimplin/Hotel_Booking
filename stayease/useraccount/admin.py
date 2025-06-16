from django.contrib import admin
from .models import RoomType,Booking,Review

# Register your models here.



admin.site.register(RoomType)
admin.site.register(Booking)
admin.site.register(Review)