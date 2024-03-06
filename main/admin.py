from django.contrib import admin
from .models import Course, Days, KindOfSpending, Spending, Group, \
    GroupStudent, Payment, Money, TeacherSalary, GivenSalary, \
    Report, Attendance, AttendanceStudent

admin.site.register({Course, Days, KindOfSpending, Spending, Group, GroupStudent, Payment, Money, TeacherSalary, Report, \
                    GivenSalary, AttendanceStudent, Attendance})











