from django.db import models

class MerchandiseCategory(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Merchandise Category"
        verbose_name_plural = "Merchandise Categories"

    def __str__(self):
        return self.name