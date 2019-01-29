from django.db import models

# Add your models here

class WaitTime(models.Model):
    appointment_id = models.CharField(max_length=15)
    wait_time = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
