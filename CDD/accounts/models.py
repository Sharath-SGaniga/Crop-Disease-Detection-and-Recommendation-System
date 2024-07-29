from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    image = models.ImageField(upload_to='disease_images/')

    def __str__(self):
        return f" - {self.image.name}"

class Disease(models.Model):
    disease = models.CharField(max_length=255)
    image = models.ForeignKey(Image,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.disease} - {self.image.image.name}"



