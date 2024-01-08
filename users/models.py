from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_ROLE_CHOICES = (
        ('student', "Student"),
        ('teacher', "Teacher"),
        ('admin', "Admin"),
        ('super', 'Super'),
    )

    USER_TYPE_CHOICES = (
        ("pause", 'Pause'),
        ('active', "Active"),
        ('stater', 'Stater'),
        ('deleted', 'Deleted'),
        ('test', 'Test'),
    )
    user_role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    birthday = models.DateField(null=True, blank=True)
    dept = models.BooleanField(blank=False, null=True, default=False)
    dept_count = models.IntegerField(default=0, blank=True, null=True)
    is_pay = models.BooleanField(default=False)
    salary = models.FloatField(null=True, blank=True)
    arrival_day = models.DateField(auto_now_add=True)
    started_day = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    phone_number2 = models.CharField(max_length=15, blank=True, null=True)


