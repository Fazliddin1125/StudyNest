from django.contrib import admin
from .models import CustomUser, Target

admin.site.register(CustomUser)
admin.site.register(Target)
