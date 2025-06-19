from django.contrib import admin
from .models import RoomType,Booking,Review,Offer

# Register your models here.



admin.site.register(RoomType)
admin.site.register(Booking)
admin.site.register(Review)
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "badge_text", "badge_color")