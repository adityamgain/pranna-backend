from django.db import models

class Booking(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    package = models.CharField(max_length=200, blank=True)
    booking_date = models.DateField()
    guests = models.IntegerField(default=1)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.booking_date}"
