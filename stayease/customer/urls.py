from django.urls import path
from .views import *
from . import views


urlpatterns=[
    path('user',UserView.as_view(),name='user'),
    path('contact',ContactView.as_view(),name='contact'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='roomdetails'),
    path('rooms/<int:room_id>/book/', views.book_room, name='bookroom'),
    path('rooms/<int:room_id>/confirm/', views.confirm_booking, name='confirmbooking'),
    path('booking/success/', views.booking_success, name='bookingsuccess'),

]