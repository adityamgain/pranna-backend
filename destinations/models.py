from django.db import models
from django.utils.text import slugify


class Destination(models.Model):
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True,
                            help_text="Font Awesome icon class (e.g., 'fa-mountain', 'fa-water')")

    # Descriptions
    short_description = models.TextField(max_length=500)
    description = models.TextField(blank=True)

    # Tags (for filtering and categorization)
    tags = models.JSONField(default=list,
                            help_text="List of tags as JSON array (e.g., ['meditation', 'mountains', 'spiritual'])")

    # Media
    featured_image = models.ImageField(upload_to='destinations/featured/', blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
