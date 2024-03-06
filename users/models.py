import uuid
import random

from django.db import models
from django.contrib.auth.models import AbstractUser


class Target(models.Model):
    name = models.CharField(max_length=80)
    percentage = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

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
    visit_by = models.ForeignKey(Target, on_delete=models.SET(1), blank=True, null=True)
    study = models.CharField(max_length=150, default=" Nomalum ", null=True, blank=True)


    def check_username(self):
        if not self.username:
            temp_username = f'user-{uuid.uuid4().__str__().split("-")[-1]}' # instagram-23324fsdf
            print(temp_username)
            while CustomUser.objects.filter(username=temp_username):
                temp_username = f"{temp_username}{random.randint(0,9)}"
            self.username = temp_username

    def check_pass(self):
        if not self.password:
            temp_password = f'password-{uuid.uuid4().__str__().split("-")[-1]}' #  123456mfdsjfkd
            print(temp_password)
            self.password = temp_password

    def save(self, *args, **kwargs):
        self.clean()
        super(CustomUser, self).save(*args, **kwargs)

    def clean(self):
        self.check_username()
        self.check_pass()

