from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from journey.models import Journey  # Import Journey model


class GalleryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, default='fa-image')
    featured_image = models.ImageField(upload_to='gallery/categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gallery Category"
        verbose_name_plural = "Gallery Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class GalleryImage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    caption = models.CharField(max_length=500, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    image = models.ImageField(
        upload_to='gallery/images/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp'])]
    )
    high_res_image = models.ImageField(upload_to='gallery/high-res/', blank=True, null=True)

    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='images'
    )

    # NEW: Many-to-many relationship with Journey
    journeys = models.ManyToManyField(
        Journey,
        through='GalleryImageJourney',
        related_name='gallery_images',
        blank=True,
        help_text="Select journeys this image is associated with"
    )

    location = models.CharField(max_length=200, blank=True, null=True)
    date_taken = models.DateField(blank=True, null=True)
    photographer = models.CharField(max_length=100, blank=True, null=True)

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while GalleryImage.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


# NEW: Through model for GalleryImage and Journey relationship
class GalleryImageJourney(models.Model):
    """
    Through model for many-to-many relationship between GalleryImage and Journey
    Allows storing additional metadata about the relationship
    """
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name='image_journeys')
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name='journey_images')

    # Optional: Add metadata about the relationship
    is_primary = models.BooleanField(default=False, help_text="Is this the primary image for this journey?")
    caption = models.CharField(max_length=255, blank=True, null=True,
                               help_text="Specific caption for this journey-image pairing")
    order = models.PositiveIntegerField(default=0, help_text="Order of this image within the journey")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gallery Image - Journey Link"
        verbose_name_plural = "Gallery Image - Journey Links"
        ordering = ['order', 'image__title']
        unique_together = ('image', 'journey')  # Prevent duplicate relationships

    def __str__(self):
        return f"{self.image.title} → {self.journey.name}"


class GalleryAlbum(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='gallery/albums/', blank=True, null=True)
    images = models.ManyToManyField(GalleryImage, related_name='albums', blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gallery Album"
        verbose_name_plural = "Gallery Albums"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class GalleryTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class GalleryImageTag(models.Model):
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name='image_tags')
    tag = models.ForeignKey(GalleryTag, on_delete=models.CASCADE, related_name='tag_images')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('image', 'tag')

    def __str__(self):
        return f"{self.image.title} - {self.tag.name}"