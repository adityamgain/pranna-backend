from django.db import models
from django.utils.text import slugify


class Journey(models.Model):
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class (e.g., 'fa-om', 'fa-music')")

    # Descriptions
    short_description = models.TextField(max_length=500)
    description = models.TextField()

    # Level
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all-levels', 'All Levels'),
    ]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='all-levels')

    # Quick Facts (as JSON for flexibility)
    quick_facts = models.JSONField(default=list, help_text="List of quick facts as JSON array")

    # Included/Not Included Lists
    includes = models.JSONField(default=list, help_text="List of included items as JSON array")
    excludes = models.JSONField(default=list, help_text="List of excluded items as JSON array")

    # Media
    featured_image = models.ImageField(upload_to='journeys/featured/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)