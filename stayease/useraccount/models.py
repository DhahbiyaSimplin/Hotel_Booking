from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.IntegerField()
    features = models.TextField()
    image = models.ImageField(upload_to='room_images/')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class Booking(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    booked_on = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} | {self.room_type.name} x {self.quantity} | {self.check_in} to {self.check_out}"



class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.room_type.name} | {self.rating}/5"
    

class Offer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    badge_text = models.CharField(max_length=30, blank=True, null=True)  # e.g., "Limited Time"
    badge_color = models.CharField(max_length=20, default="primary")  # Bootstrap class like 'danger', 'success'
    icon = models.CharField(max_length=10, blank=True, null=True)  # Emoji or font-awesome class

    def __str__(self):
        return self.title
