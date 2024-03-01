# Create your models here.
from django.db import models

class RegisteredUser(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# models.py
from django.db import models

class AnalyzerData(models.Model):
    u_name = models.CharField(max_length=100,default="none")
    content_name = models.CharField(max_length=100)
    content_description = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    uploaded_file = models.FileField(upload_to='uploads/', blank=True, null=True)

    def __str__(self):
        return self.content_name
