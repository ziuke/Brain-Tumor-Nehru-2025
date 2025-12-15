from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Register(AbstractUser):
    usertype = models.IntegerField(default=0)
    phone = models.IntegerField(default=0)
    name = models.CharField(max_length=200, default='', null=True)
    place = models.CharField(max_length=200,  default='', null=True)
    reject_reason = models.TextField(default='', null=True)
    image = models.FileField(null=True,upload_to='uploads/')
    is_approved = models.BooleanField(default=False)
    experience = models.CharField(max_length=200, default='')
    qualification = models.CharField(max_length=50,default='')
    specialization = models.CharField(max_length=50,default='')
    location = models.CharField(max_length=200,  default='', null=True)
    lat = models.FloatField(max_length=200, null=True)
    long = models.FloatField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    

class PredictionResult(models.Model):
    """Model to store uploaded brain scan images and their prediction results"""
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='predictions')
    uploaded_image = models.ImageField(upload_to='predictions/')
    predicted_class = models.CharField(max_length=50)
    confidence = models.FloatField()
    all_probabilities = models.JSONField(default=dict, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.predicted_class} ({self.confidence:.2%})"

