from django.db import models

class Newsletter_Mails(models.Model):
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Newsletter Mails"
        ordering = ['-created_at']

    def __str__(self):
        return self.email