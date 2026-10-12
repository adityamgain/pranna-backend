from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from destinations.models import Destination
from journey.models import Journey
from packages.models import Package


class EventQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def upcoming(self):
        now = timezone.now()
        return self.filter(Q(end__gte=now) | Q(end__isnull=True, start__gte=now))

    def overlapping(self, range_start, range_end):
        """Events that intersect [range_start, range_end)."""
        return self.filter(start__lt=range_end).filter(
            Q(end__gte=range_start) | Q(end__isnull=True, start__gte=range_start)
        )


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('retreat', 'Retreat'),
        ('workshop', 'Workshop'),
        ('ceremony', 'Ceremony'),
        ('class', 'Class'),
        ('festival', 'Festival'),
        ('trek', 'Trek'),
        ('other', 'Other'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='other')
    icon = models.CharField(max_length=50, blank=True,
                            help_text="Font Awesome icon class (e.g., 'fa-om', 'fa-music')")

    # Descriptions
    short_description = models.TextField(max_length=500, blank=True)
    description = models.TextField(blank=True)

    # Schedule
    start = models.DateTimeField(db_index=True)
    end = models.DateTimeField(null=True, blank=True, db_index=True,
                               help_text="Leave blank for events without a fixed end time")
    all_day = models.BooleanField(default=False)

    # Location
    location = models.CharField(max_length=255, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='events')

    # Related offerings
    journey = models.ForeignKey(Journey, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='events')
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='events')

    # Pricing & Capacity
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_display = models.CharField(max_length=100, blank=True,
                                     help_text="Custom price string (e.g., 'Free', '$120')")
    capacity = models.PositiveIntegerField(null=True, blank=True)
    spots_left = models.PositiveIntegerField(null=True, blank=True)
    registration_url = models.URLField(blank=True)

    # Media & Appearance
    featured_image = models.ImageField(upload_to='events/featured/', blank=True, null=True)
    color_hex = models.CharField(max_length=7, blank=True,
                                 help_text="Calendar colour hex code (e.g., '#1f463b')")

    # Flags
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EventQuerySet.as_manager()

    class Meta:
        ordering = ['start', 'title']

    def __str__(self):
        return f"{self.title} ({self.start:%Y-%m-%d})"

    def clean(self):
        if self.end and self.start and self.end < self.start:
            raise ValidationError({'end': 'End must be after start.'})
        if self.capacity is not None and self.spots_left is not None and self.spots_left > self.capacity:
            raise ValidationError({'spots_left': 'Spots left cannot exceed capacity.'})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or 'event'
            slug = f"{base}-{self.start:%Y-%m-%d}" if self.start else base
            candidate, n = slug, 2
            while Event.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{slug}-{n}"
                n += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def effective_end(self):
        return self.end or self.start

    @property
    def is_sold_out(self):
        return self.spots_left == 0

    def local_dates(self):
        """Calendar dates (in the current timezone) this event covers."""
        first = timezone.localtime(self.start).date()
        last = timezone.localtime(self.effective_end).date()
        return [first + timedelta(days=i) for i in range((last - first).days + 1)]
