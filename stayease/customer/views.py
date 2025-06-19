from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import TemplateView,View,DetailView
from useraccount.models import RoomType,Booking,Review,Offer
from useraccount.forms import BookingForm
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

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
    # ✅ Prevent booking if room is not available
    if not room.is_available:
        messages.error(request, "This room is currently not available for booking.")
        return redirect('user')  # or your rooms listing page

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
    room = get_object_or_404(RoomType, id=room_id)
     # ✅ Prevent confirming if not available
    if not room.is_available:
        messages.error(request, "This room is currently not available.")
        return redirect('user')  # or any appropriate page
    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        guests = request.POST.get('guests')
        quantity = request.POST.get('quantity')

        # Save booking to database
        booking = Booking.objects.create(
            user=request.user,
            room_type=room,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            quantity=quantity,
            status='Pending'  # optional status field
        )

        return redirect('paymentcheckout',booking_id=booking.id)
    

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


@csrf_exempt
def payment_checkout(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    # Calculate number of nights
    nights = (booking.check_out - booking.check_in).days
    amount_rupees = booking.room_type.price_per_night * booking.quantity * nights
    amount_paise = int(amount_rupees * 100)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment = client.order.create({
        "amount": amount_paise,  
        "currency": "INR",
        "payment_capture": 1
    })

    booking.razorpay_order_id = payment['id']
    booking.amount=amount_rupees
    booking.save()

    return render(request, "checkout.html", {
        "booking": booking,
        "payment": payment,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount_rupees": amount_rupees
    })


@csrf_exempt
def payment_success(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    # You may want to verify the payment using razorpay client here

    booking.status = 'Confirmed'
    booking.save()

    return render(request, 'bookingsuccess.html', {
        'booking': booking,
        'payment_id': request.POST.get('razorpay_payment_id'),
        'amount': booking.amount
    })


# def home(request):
#     offers = Offer.objects.all()
#     return render(request, 'home.html', {'offers': offers})
