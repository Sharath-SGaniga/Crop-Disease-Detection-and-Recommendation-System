from django.contrib import admin
from .models import profile,Image,Disease

# Register your models here.
admin.site.register(Image)
admin.site.register(profile)
admin.site.register(Disease)