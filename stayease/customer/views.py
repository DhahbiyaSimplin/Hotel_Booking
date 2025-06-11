from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import TemplateView,View,DetailView
from account.models import RoomType,Booking
from account.forms import BookingForm

# Create your views here.


class UserView(View):
    def get(self,request):
        room_types = RoomType.objects.all()
        return render(request, 'user.html', {'room_types': room_types})
    

class ContactView(View):
    def get(self,request):
        return render(request,"contact.html")
    

class RoomDetailView(DetailView):
    model = RoomType
    template_name = 'roomdetails.html'
    context_object_name = 'room'  



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