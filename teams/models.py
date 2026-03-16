from django.db import models
from django.utils.text import slugify


class TeamMember(models.Model):
    # Basic Information
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)

    # URL slug for pretty URLs
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    # Social Links
    linkedin = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)

    # Description
    short_description = models.TextField(max_length=500)

    # Media
    image = models.ImageField(upload_to='team/', blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Meta class for better admin display
    class Meta:
        ordering = ['name']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)