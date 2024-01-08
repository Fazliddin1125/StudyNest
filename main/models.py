from django.db import models
from users.models import CustomUser
from django.utils import timezone

class Course(models.Model):
    name = models.CharField(max_length=50)
    comment = models.CharField(max_length=25, blank=True, null=True)
    type = models.BooleanField(default=True)


    def __str__(self):
        return self.name

class Days(models.Model):
    DAYS_CHOICES = (
        ('Dushanba', 'dushanba'),
        ('Seshanba', 'seshanba'),
        ('Chorshanba', 'chorshanba'),
        ('Pyshanba', 'payshanba'),
        ('Juma', 'juma'),
        ('Shanba', 'shanba'),
    )
    all_days = models.BooleanField(default=False)
    name = models.CharField(max_length=36)
    added_lesson = models.BooleanField(default=False)
    day1 = models.CharField(max_length=12, choices=DAYS_CHOICES)
    day2 = models.CharField(max_length=12, choices=DAYS_CHOICES)
    day3 = models.CharField(max_length=12, choices=DAYS_CHOICES)

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=50)
    pay = models.IntegerField()
    teacher = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    day = models.ForeignKey(Days, on_delete=models.PROTECT)
    hour = models.IntegerField(default=8)
    minut = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    type = models.BooleanField(default=True)
    percentage = models.IntegerField(default=50)


    def __str__(self):
        return self.name

class GroupStudent(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    arrival_day = models.DateField(auto_now_add=True)
    started_day = models.DateField(null=True, blank=True)
    pay_for = models.FloatField(default=0, null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)



    def __str__(self):
        return f"{self.student}--{self.group}"

class Payment(models.Model):
    MONTHS_CHOICES = (
        ("Yanvar", 'yanvar'),
        ("Fevral", 'fevral'),
        ("Mart", 'mart'),
        ("Aprel", 'aprel'),
        ("May", 'may'),
        ("Iyun", 'iyun'),
        ("Iyul", 'iyul'),
        ("Avgust", 'avgust'),
        ("Sentabr", 'sentabr'),
        ("Oktabr", 'oktabr'),
        ("Noyabr", 'noyabr'),
        ("Dekabr", 'dekabr'),
    )
    yil = timezone.now().year
    print(yil)
    count = models.IntegerField(default=0)
    card = models.IntegerField(default=0)
    cash = models.IntegerField(default=0)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    month = models.CharField(max_length=20, choices=MONTHS_CHOICES)
    year = models.IntegerField(default=yil)
    pay_date = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    success = models.BooleanField(default=False)
    dept = models.BooleanField(default=True)
    dept_count = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'year', 'month', 'group']

    def __str__(self):
        return f"{self.student}--{self.month}--{self.group}"

class Money(models.Model):
    name = models.CharField(max_length=25)
    count = models.IntegerField()

    def __str__(self):
        return self.name

class TeacherSalary(models.Model):
    MONTHS_CHOICES = (
        ("Yanvar", 'yanvar'),
        ("Fevral", 'fevral'),
        ("Mart", 'mart'),
        ("Aprel", 'aprel'),
        ("May", 'may'),
        ("Iyun", 'iyun'),
        ("Iyul", 'iyul'),
        ("Avgust", 'avgust'),
        ("Sentabr", 'sentabr'),
        ("Oktabr", 'oktabr'),
        ("Noyabr", 'noyabr'),
        ("Dekabr", 'dekabr'),
    )
    yil = timezone.now().year
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    count = models.IntegerField()
    give = models.IntegerField(null=True, blank=True)
    not_give = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=False)
    month = models.CharField(max_length=20, choices=MONTHS_CHOICES)
    year = models.IntegerField(default=yil)
    created_date = models.DateTimeField(auto_now_add=True)
    given_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ['teacher', 'month', 'year']

    def __str__(self):
        return f"{self.month} {self.teacher}"

class KindOfSpending(models.Model):
    name = models.CharField(max_length=50)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

class Spending(models.Model):
    count = models.IntegerField()
    card = models.IntegerField(default=0)
    cash = models.IntegerField(default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    created_date = models.DateField(auto_now_add=True)
    for_smt = models.ForeignKey(KindOfSpending, on_delete=models.PROTECT)
    comment = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.count}--{self.for_smt}"

class GivenSalary(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.Empty, blank=True, null=True)
    year = models.IntegerField()
    month = models.CharField(max_length=20)
    origin_count = models.IntegerField(blank=True, null=True)
    count = models.IntegerField()
    card = models.IntegerField(blank=True, null=True)
    cash = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher} {self.month}"

class Report(models.Model):
    year = models.IntegerField()
    month = models.CharField(max_length=20)
    salary = models.IntegerField()
    profit = models.IntegerField()
    spending = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.month




















