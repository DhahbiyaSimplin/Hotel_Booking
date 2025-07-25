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
    path('bookings/upcoming/', views.upcoming_bookings, name='upcomingbookings'),
    path('bookings/previous/', views.previous_bookings, name='previousbookings'),
    path('reviews/', views.all_reviews, name='allreviews'),
    path('rooms/<int:room_id>/review/', views.add_review, name='addreview'),
    path("payment/<int:booking_id>/", views.payment_checkout, name="paymentcheckout"),
    path('payment/success/<int:booking_id>/', views.payment_success, name='paymentsuccess'),
]