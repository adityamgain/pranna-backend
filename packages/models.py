from django.db import models
from django.utils.text import slugify
from destinations.models import Destination
from journey.models import Journey

class Package(models.Model):
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True,
                            help_text="Font Awesome icon class (e.g., 'fa-spa', 'fa-pray')")

    # Descriptions
    short_description = models.TextField(max_length=500)
    description = models.TextField(help_text="Full description of the package")

    # Relationships
    locations = models.ManyToManyField(
        Destination,
        related_name='packages',
        blank=True,
        help_text="Destinations included in this package"
    )
    services = models.ManyToManyField(
        Journey,
        related_name='packages',
        blank=True,
        help_text="Journeys/services included (e.g., Sound Healing, Yoga)"
    )

    # Difficulty level
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all-levels', 'All Levels'),
    ]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='all-levels')

    # Pricing & Availability
    price_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Minimum price (for sorting)"
    )
    price_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Maximum price (for sorting)"
    )
    price_display = models.CharField(
        max_length=100, blank=True,
        help_text="Custom price string (e.g., '$1,600 - $2,200')"
    )
    in_stock = models.BooleanField(default=True, help_text="Whether spots are available")
    spots_left = models.IntegerField(default=0, blank=True)
    next_start_date = models.DateField(null=True, blank=True, help_text="Next scheduled start date")

    # Duration
    duration_days = models.IntegerField(
        null=True, blank=True,
        help_text="Duration in days (for sorting)"
    )
    duration_display = models.CharField(
        max_length=50, blank=True,
        help_text="Display duration (e.g., '7 days')"
    )

    # Features
    quick_facts = models.JSONField(
        default=list,
        help_text="List of package highlights/quick facts as JSON array"
    )
    savings_text = models.CharField(
        max_length=200, blank=True,
        help_text="Savings information (e.g., 'Save 8% compared to booking separately')"
    )

    # Media & Appearance
    featured_image = models.ImageField(upload_to='packages/featured/', blank=True, null=True)
    color_hex = models.CharField(
        max_length=7, blank=True,
        help_text="Accent color hex code (e.g., '#8E44AD')"
    )
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

    @property
    def price_range(self):
        """Returns a formatted price range string for display."""
        if self.price_display:
            return self.price_display
        if self.price_min and self.price_max:
            return f"${self.price_min} – ${self.price_max}"
        if self.price_min:
            return f"From ${self.price_min}"
        if self.price_max:
            return f"Up to ${self.price_max}"
        return "Contact for pricing"