from django.contrib import admin
from .models import Course, Days, KindOfSpending, Spending, Group, GroupStudent, Payment, Money, TeacherSalary, GivenSalary, Report

admin.site.register({Course, Days, KindOfSpending, Spending, Group, GroupStudent, Payment, Money, TeacherSalary, Report, GivenSalary})