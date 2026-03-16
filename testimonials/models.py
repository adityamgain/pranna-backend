from django.db import models

class Testimonial(models.Model):
    author_name = models.CharField(max_length=200)
    author_location = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    rating = models.IntegerField(default=5)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.author_name
