from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator

class Gift(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        RESERVED = "reserved", "Reserved"
        GIFTED = "gifted", "Gifted"

    name = models.CharField(max_length=255)
    link = models.URLField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    image = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gifts",
    )

    def __str__(self) -> str:
        return self.name
