from django.db import models


class Outlet(models.Model):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    gst_number = models.CharField(max_length=50, blank=True, verbose_name='GST number')
    timezone = models.CharField(max_length=50, default='Pacific/Port_Moresby')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
