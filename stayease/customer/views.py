from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import TemplateView,View,DetailView
from useraccount.models import RoomType,Booking,Review
from useraccount.forms import BookingForm
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

# Create your views here.


class UserView(View):
    def get(self,request):
        room_types = RoomType.objects.all()
        # bookings = Booking.objects.filter(user=request.user)
        # booked_room_ids = bookings.values_list('room_type__id', flat=True)
        if request.user.is_authenticated:
            booked_room_ids = Booking.objects.filter(user=request.user).values_list('room_type__id', flat=True)
        else:
            booked_room_ids = []

        return render(request, 'user.html', {
            'room_types': room_types,
            'booked_room_ids': booked_room_ids})
    

class ContactView(View):
    def get(self,request):
        return render(request,"contact.html")
    

class RoomDetailView(LoginRequiredMixin,DetailView):
    login_url = '/login'
    model = RoomType
    template_name = 'roomdetails.html'
    context_object_name = 'room'  


@login_required(login_url='/login')
def book_room(request, room_id):
    room = get_object_or_404(RoomType, id=room_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.room_type = room
            request.session['booking_data'] = {
                'room_id': room.id,
                'check_in': str(booking.check_in),
                'check_out': str(booking.check_out),
                'guests': booking.guests,
                'quantity': booking.quantity,
            }
            return redirect('booking_preview')
    else:
        form = BookingForm()
    return render(request, 'bookroom.html', {'form': form, 'room': room})


def confirm_booking(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(RoomType, id=room_id)
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        guests = request.POST.get('guests')
        quantity = request.POST.get('quantity')

        # Save booking to database
        Booking.objects.create(
            user=request.user,
            room_type=room,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            quantity=quantity,
            status='Confirmed'  # optional status field
        )

        return redirect('bookingsuccess')
    

def booking_success(request):
    return render(request, 'bookingsuccess.html')


# def user_bookings(request):
#     today = date.today()
#     bookings = Booking.objects.filter(user=request.user).order_by('-check_in')

#     upcoming = bookings.filter(check_in__gte=today)
#     previous = bookings.filter(check_out__lt=today)

#     return render(request, 'userbooking.html', {
#         'upcoming_bookings': upcoming,
#         'previous_bookings': previous
#     })


@login_required
def upcoming_bookings(request):
    today = date.today()
    bookings = Booking.objects.filter(user=request.user, check_in__gte=today).order_by('check_in')
    return render(request, 'upcomingbooking.html', {'bookings': bookings})


@login_required
def previous_bookings(request):
    today = date.today()
    bookings = Booking.objects.filter(user=request.user, check_out__lt=today).order_by('-check_out')
    return render(request, 'previousbooking.html', {'bookings': bookings})


@login_required
def add_review(request, room_id):
    room = get_object_or_404(RoomType, id=room_id)
    has_booking = Booking.objects.filter(user=request.user, room_type=room).exists()

    if not has_booking:
        return HttpResponse("You are not allowed to review this room.")

    if request.method == 'POST':
        rating = request.POST['rating']
        comment = request.POST['comment']
        Review.objects.create(user=request.user, room_type=room, rating=rating, comment=comment)
        return redirect('allreviews')

    return render(request, 'addreview.html', {'room': room})


def all_reviews(request):
    reviews = Review.objects.select_related('room_type', 'user').all().order_by('-date_posted')
    return render(request, 'allreviews.html', {'reviews': reviews})
