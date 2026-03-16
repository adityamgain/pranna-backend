from django.db import models
from merchandise_category.models import MerchandiseCategory

class Merchandise(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        MerchandiseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merchandise_items'
    )
    description = models.TextField()
    quick_facts = models.JSONField(default=list, help_text="List of quick facts as JSON array")
    story = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='merchandise/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Merchandise"
        verbose_name_plural = "Merchandise Items"

    def __str__(self):
        return self.name