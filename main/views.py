from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.urls import reverse
from django.views import View
from users.models import CustomUser
from .models import Group, GroupStudent, Payment, Money, Spending, \
    KindOfSpending, GivenSalary, Attendance, AttendanceStudent, Days, Course
from datetime import datetime

from django.contrib import messages
from .utilits import readnumber

class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        len_act = len(CustomUser.objects.filter(user_role='student', user_type='active'))
        len_lid = len(CustomUser.objects.filter(user_role='student', user_type='stater'))
        len_dep = len(CustomUser.objects.filter(user_role='student', is_pay=False, user_type='active'))
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            students = CustomUser.objects.filter(user_role='student').order_by('-arrival_day')
            teachers = CustomUser.objects.filter(user_role='teacher')
            groups = Group.objects.all()
            payments = Payment.objects.all().order_by('-pay_date')
            context = {
                'students': students,
                'teachers': teachers,
                'groups': groups,
                'payments': payments,
                'act_len': len_act,
                'len_lid': len_lid,
                'len_dep': len_dep,

            }
            return render(request, 'index.html', context)
        elif request.user.user_role == 'teacher':
            return render(request, 'indext.html')
        else:
            messages.warning(request, "Sizga ushbu sahifaga kirish uchun admin tomonidan ruxsat berilmagan!")
            return redirect('logout')

class PaymentView(LoginRequiredMixin, View):
    def get(self, request, username):
        if request.user.user_role == 'super' or request.user.user_role == 'admin':
            user = CustomUser.objects.get(username=username)
            groups = user.groupstudent_set.all
            group_students = GroupStudent.objects.filter(student=user)

            context = {
                'user': user,
                'groups': groups,
                'group_students': group_students
            }
            return render(request, 'payment.html', context)
        else:
            messages.warning(request, 'Sizga ushbu amal uchun admin tomonidan ruxsat berilmagan')
            return render(request, '404.html')
    def post(self, request, username):
        if request.POST['cash'] == '' or request.POST['card'] == '':
            messages.warning(request, "Karta yoki Qaqt pul bo'sh qolishi mumkin emas.")
            return render(request, '404.html')
        months = [
            "Yanvar",
            "Fevral",
            "Mart",
            "Aprel",
            "May",
            "Iyun",
            "Iyul",
            "Avgust",
            "Sentabr",
            "Oktabr",
            "Noyabr",
            "Dekabr",
        ]
        user = CustomUser.objects.get(username=username)

        groups = user.groupstudent_set.all
        context = {
            'user': user,
            'groups': groups
        }
        group_id = request.POST['group']
        if group_id == '':
            messages.warning(request, f"{user.first_name} {user.last_name} biriktirilgan guruh mavjud emas. ")
            return render(request, 'payment.html')
        cash = int(request.POST['cash'])
        card = int(request.POST['card'])
        date = request.POST['date']
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        year = date_obj.year
        month = months[date_obj.month-1]
        group = Group.objects.get(id=int(group_id))
        count = cash+card
        all_payments = Payment.objects.all()
        for pay in all_payments:
            if pay.student == user and pay.month == month and pay.year == year and pay.group == group:
                messages.warning(request, f"{user.first_name} {user.last_name} allaqachon {month} oyi uchun to'lovni amalga oshirgan")
                return render(request, 'payment.html', context)

        group_student = get_object_or_404(GroupStudent, student=user, group=group)
        sale = group_student.sale

        sale_count = group_student.count
        if sale:
            if sale_count <= count:
                success = True
                dept = False
                dept_count = 0
                user.is_pay = True
                user.dept = False
                user.dept_count = dept_count
            else:
                success = False
                dept = True
                dept_count = sale_count - count
                user.is_pay = False
                user.dept = True
                user.dept_count = dept_count
        elif group.pay > count:
            success = False
            dept = True
            dept_count = group.pay - count
            user.is_pay = False
            user.dept = True
            user.dept_count = dept_count
        elif group.pay <= count:
            success = True
            dept = False
            dept_count = 0
            user.is_pay = True
            user.dept = False
            user.dept_count = dept_count
        user.save()
        payment = Payment.objects.create(
            year=year,
            count=count,
            card=card,
            cash=cash,
            student=user,
            month=month,
            date=date_obj,
            group=group,
            success=success,
            dept=dept,
            dept_count=dept_count
        )
        payment.save()

        all_money = Money.objects.get(id=1)
        card_money = Money.objects.get(id=2)
        cash_money = Money.objects.get(id=3)
        all_money.count = count + all_money.count
        card_money.count = card + card_money.count
        cash_money.count = cash + cash_money.count
        all_money.save()
        cash_money.save()
        card_money.save()
        messages.success(request,
                         f"{user.username}. {month} oy uchun {int(cash) + int(card)} sum tolov qilindi!")
        return render(request, 'payment.html', context)

class PaymentDetailView(LoginRequiredMixin, View):
    def get(self, request, payment_id):
        if request.user.user_role == 'super' or request.user.user_role == 'admin':
            if Payment.objects.get(id=payment_id):
                payment = Payment.objects.get(id=payment_id)
                groups = payment.student.groupstudent_set.all
                user = payment.student
                group_students = GroupStudent.objects.filter(student=user)
                context = {
                    'payment': payment,
                    'groups': groups,
                    'group_students': group_students
                }
                return render(request, 'payment_edit.html', context)
            else:
                messages.warning(request, f"Bunday to'lov mavjud emas")
                return render(request, 'index.html')
        else:
            messages.warning(request, "Sizga uchbu amal uchun admin tomonidan ruxsat berilmagan.")
            return render(request, '404.html')

    def post(self, request, payment_id):
        months = [
            "Yanvar",
            "Fevral",
            "Mart",
            "Aprel",
            "May",
            "Iyun",
            "Iyul",
            "Avgust",
            "Sentabr",
            "Oktabr",
            "Noyabr",
            "Dekabr",
        ]
        try:
            if request.POST['cash'] == '' or request.POST['card'] == '':
                messages.warning(request, "Karta yoki Qaqt pul bo'sh qolishi mumkin emas.")
                return render(request, '404.html')
            payment = get_object_or_404(Payment, id=payment_id)
            username = request.POST['username']
            user = CustomUser.objects.get(username=username)
            groups = user.groupstudent_set.all()

            group_id = request.POST['group']
            cash = int(request.POST['cash'])
            card = int(request.POST['card'])
            date = request.POST['date']
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            year = date_obj.year
            month = months[date_obj.month - 1]
            group = Group.objects.get(id=int(group_id))
            count = cash + card

            success = False
            dept = False
            dept_count = 0

            all_money = Money.objects.get(id=1)
            card_money = Money.objects.get(id=2)
            cash_money = Money.objects.get(id=3)

            group_student = get_object_or_404(GroupStudent, student=user, group=group)
            sale = group_student.sale
            sale_count = group_student.count
            if sale:
                if sale_count <= count:
                    success = True
                    dept = False
                    dept_count = 0
                    user.is_pay = True
                    user.dept = False
                    user.dept_count = dept_count
                else:
                    success = False
                    dept = True
                    dept_count = sale_count - count
                    user.is_pay = False
                    user.dept = True
                    user.dept_count = dept_count
            elif group.pay > count:
                success = False
                dept = True
                dept_count = group.pay - count
                user.is_pay = False
                user.dept = True
                user.dept_count = dept_count
            elif group.pay <= count:
                success = True
                dept = False
                dept_count = 0
                user.is_pay = True
                user.dept = False
                user.dept_count = dept_count
            user.save()


            # O'zgartirilgan malumotlar
            payment.year = year
            payment.student = user

            all_money.count = all_money.count - payment.count
            payment.count = count


            payment.month = month
            card_money.count = card_money.count - payment.card
            payment.card = card

            cash_money.count = cash_money.count - payment.cash
            payment.cash = cash


            payment.date = date_obj
            payment.group = group
            payment.success = success
            payment.dept = dept
            payment.dept_count = dept_count

            payment.save()
            all_money.count = payment.count + all_money.count
            card_money.count = payment.card + card_money.count
            cash_money.count = payment.cash + cash_money.count

            all_money.save()
            cash_money.save()
            card_money.save()

            context = {
                'payment': payment,
                'groups': groups,
            }

            if success:
                messages.info(request,
                              f"{user.first_name} {user.last_name}ning to'lovi {month} oyi uchun qabul qilindi !")
            elif dept:
                messages.warning(request,
                                 f"{user.first_name} {user.last_name}da {month} oyi uchun {dept_count} so'm qarzdorlik mavjud")

            return render(request, 'payment_edit.html', context)

        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            return render(request, 'payment_edit.html')

class StudentsView(View):
    def get(self, request):
        login_form = AuthenticationForm()
        if request.user.user_role == "admin" or request.user.user_role == 'super':
            students = CustomUser.objects.filter(user_role='student', user_type='active').order_by('-arrival_day')
            search_query = request.GET.get('q')
            if search_query:
                students = students.filter(first_name__icontains=search_query)

            context = {
                'students': students
            }
            return render(request, 'students.html', context)
        else:
            messages.warning(request, "Sizga ushbu sahifaga kirish uchun admin tomonidan ruxsat berilmagan!")
            return render(request, '404.html')

class LidsView(View):
    def get(self, request):
        login_form = AuthenticationForm()
        if request.user.user_role == "admin" or request.user.user_role == 'super':
            students = CustomUser.objects.filter(user_role='student', user_type='stater').order_by('-arrival_day')
            search_query = request.GET.get('q')
            if search_query:
                students = students.filter(first_name__icontains=search_query)

            context = {
                'students': students
            }
            return render(request, 'students.html', context)
        else:
            messages.warning(request, "Sizga ushbu sahifaga kirish uchun admin tomonidan ruxsat berilmagan!")
            return render(request, 'login.html', {'form': login_form})

class TestView(View):
    def get(self, request):
        login_form = AuthenticationForm()
        if request.user.user_role == "admin" or request.user.user_role == 'super':
            students = CustomUser.objects.filter(user_role='student', user_type='test').order_by('-arrival_day')
            search_query = request.GET.get('q')
            if search_query:
                students = students.filter(first_name__icontains=search_query)

            context = {
                'students': students
            }
            return render(request, 'students.html', context)
        else:
            messages.warning(request, "Sizga ushbu sahifaga kirish uchun admin tomonidan ruxsat berilmagan!")
            return render(request, 'login.html', {'form': login_form})


class DeptView(View):
    def get(self, request):
        login_form = AuthenticationForm()
        if request.user.user_role == "admin" or request.user.user_role == 'super':
            students = CustomUser.objects.filter(user_role='student', is_pay=False, user_type='active').order_by('-arrival_day')
            search_query = request.GET.get('q')
            if search_query:
                students = students.filter(first_name__icontains=search_query)

            context = {
                'students': students
            }
            return render(request, 'students.html', context)
        else:
            messages.warning(request, "Sizga ushbu sahifaga kirish uchun admin tomonidan ruxsat berilmagan!")
            return render(request, 'login.html', {'form': login_form})

class TeacherView(View):
    def get(self, request):

        months = [
            "Yanvar",
            "Fevral",
            "Mart",
            "Aprel",
            "May",
            "Iyun",
            "Iyul",
            "Avgust",
            "Sentabr",
            "Oktabr",
            "Noyabr",
            "Dekabr",
        ]
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            teachers = CustomUser.objects.filter(user_role='teacher')
            year = datetime.now().year
            month = months[int(datetime.now().month) - 1]
            q_year = request.GET.get('year')
            q_month = request.GET.get('month')
            if q_year:
                year = q_year
            if q_month:
                month = q_month
            context = {
                'teachers': teachers,
                'year': year,
                'now_year': datetime.now().year,
                'month': month,
                'months': months,
                'years': [datetime.now().year-1, datetime.now().year+1, datetime.now().year+2]
            }
            return render(request, 'salary.html', context)
        elif request.user.user_role == 'teacher':
            teachers = CustomUser.objects.filter(username=request.user.username)
            year = datetime.now().year
            month = months[int(datetime.now().month) - 1]
            q_year = request.GET.get('year')
            q_month = request.GET.get('month')
            if q_year:
                year = q_year
            if q_month:
                month = q_month
            context = {
                'teachers': teachers,
                'year': year,
                'now_year': datetime.now().year,
                'month': month,
                'months': months,
                'years': [datetime.now().year - 1, datetime.now().year + 1, datetime.now().year + 2]
            }
            return render(request, 'salary.html', context)
        else:
            messages.error(request, "Sizga ushbu sahifaga kirish uchun admin tomonidan ruxsat berilmagan!")
            return render(request, '404.html')


class SalaryCalculateView(View):
    def get(self, request, username, year, month):
        if request.user.user_role == 'admin' or request.user.user_role == 'super' or request.user.user_role == 'teacher':
            teacher = get_object_or_404(CustomUser, username=username, user_role='teacher')
            groups = teacher.group_set.all()
            all_grs = []
            all_payments = []
            count = 0

            for group in groups:
                gr_count = 0


                for group_student in group.groupstudent_set.all():
                    # print(group_student)
                    sale = group_student.sale
                    is_sale = group_student.is_sale
                    student = group_student.student

                    payments = student.payment_set.filter(month=month, group=group, year=year)

                    for payment in payments:
                        all_payments.append(payment)
                        if sale == True:
                            if is_sale == True:
                                pay_count = group.pay
                                gr_count = gr_count + (pay_count * group.percentage / 100)
                                count = count + (pay_count * group.percentage / 100)
                            else:
                                gr_count = gr_count + (payment.count * group.percentage / 100)
                                count = count + (payment.count * group.percentage / 100)
                        else:
                            gr_count = gr_count + (payment.count * group.percentage / 100)
                            count = count + (payment.count * group.percentage / 100)
                group_salary = {
                    'group': group,
                    'count': int(gr_count),
                }
                all_grs.append(group_salary)


            count = int(count)
            rn = str(count)
            rr = readnumber(rn)

            context = {
                'teacher': teacher,
                'groups': groups,
                'payments': all_payments,
                'count': count,
                'count_read': rr,
                'all_grs': all_grs,
                'year': year,
                'month': month

            }
            return render(request, 'salary_calculate.html', context)
        else:
            messages.error(request, "Sizga ushbu safifaga kirish uchun admin tomonidan ruxsat berilmagan!")
            return render(request, '404.html')

    def post(self, request, username, year, month):
        if request.user.user_role == 'super':
            try:
                teacher = get_object_or_404(CustomUser, username=username, user_role='teacher')
                if request.POST['card'] == '' or request.POST['cash'] == '':
                    messages.warning(request, 'Karta va Naqt pulni aniq miqdorini kiriting')
                    return render(request, '404.html')
                else:
                    card = int(request.POST['card'])
                    cash = int(request.POST['cash'])
                    count = cash + card

                    salary = GivenSalary.objects.create(
                        teacher=teacher,
                        year=year,
                        month=month,
                        count=count,
                        card=card,
                        cash=cash
                    )
                    salary.save()
                    all_money = Money.objects.get(id=1)
                    all_card = Money.objects.get(id=2)
                    all_cash = Money.objects.get(id=3)

                    if all_cash.count < cash:
                        messages.warning(request, f"Naqt pul yetarli emas.")
                        return render(request, '404.html')

                    if all_card.count < card:
                        messages.warning(request, f"Kartada pul yetarli emas.")
                        return render(request, '404.html')
                    all_money.count = all_money.count - count
                    all_cash.count = all_cash.count - cash
                    all_card.count = all_card.count - card

                    all_card.save()
                    all_money.save()
                    all_cash.save()

                    redirect_url = reverse('teacher_detail',
                                           kwargs={'username': username, 'year': year, 'month': month})
                    messages.success(request, f"{teacher.first_name} {teacher.last_name} uchun {count} so'm to'landi.")
                    return redirect(redirect_url)
            except Exception as e:
                messages.warning(request, f'Xato: {str(e)}')
                return render(request, '404.html')



        else:
            return render(request, '404.html')





class SpendingView(View):
    def get(self, request):
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            kinds = KindOfSpending.objects.all()
            spending = Spending.objects.all()
            context = {
                'kinds': kinds,
                'spendings': spending,
            }
            return render(request, 'spending.html', context)
        else:
            messages.warning(request, "Sizga uchbu sahifaga kirish uchun admin tomonidan ruxsat berilmagan!")
            return render(request, '404.html')

    def post(self, request):
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            kinds = KindOfSpending.objects.all()
            spending = Spending.objects.all()
            context = {
                'kinds': kinds,
                'spendings': spending,
            }
            cash = int(request.POST['cash'])
            card = int(request.POST['card'])
            count = int(cash+card)
            kind = request.POST['kind']
            user = request.user
            comment = request.POST['comment']
            for_smt = KindOfSpending.objects.get(name=kind)
            spending = Spending.objects.create(
                count=count,
                card=card,
                cash=cash,
                user=user,
                for_smt=for_smt,
                comment=comment
            )
            spending.save()
            all_money = Money.objects.get(id=1)
            card_money = Money.objects.get(id=2)
            cash_money = Money.objects.get(id=3)
            all_money.count = all_money.count - count
            card_money.count = card_money.count - card
            cash_money.count = cash_money.count - cash
            all_money.save()
            cash_money.save()
            card_money.save()

            messages.warning(request, f"{for_smt} uchun {count} so'm xarajat qabul qilindi!")
            return render(request, 'spending.html', context)
        else:
            messages.warning(request, 'Sizga ushbu amal uchun admin tomonidan ruxsat berilmagan!')
            return render(request, '404.html')

class GroupStudentView(LoginRequiredMixin, View):
    def get(self, request, username):
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            student = get_object_or_404(CustomUser, username=username, user_role='student')
            groups = Group.objects.all()
            context = {
                'student': student,
                'groups': groups
            }
            return render(request, 'add_group.html', context)
        else:
            messages.warning(request, f"Sizga bu amal uchun admin tomonidan ruxsat berilmagan.")
            return render(request, '404.html')

    def post(self, request, username):
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            student = get_object_or_404(CustomUser, username=username, user_role='student')
            group_name = request.POST['group']
            group = get_object_or_404(Group, name=group_name)
            groupstudents = GroupStudent.objects.filter(student=student)
            date = request.POST['date']
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            for groupstudent in groupstudents:
                if groupstudent.group == group:
                    messages.warning(request, f"{student.first_name} {student.last_name} allaqachon {group}ga qo'shilgan")
                    return redirect('students_list')
            new_grst = GroupStudent.objects.create(
                student=student,
                group=group,
                started_day=date
            )
            new_grst.save()
            student.user_type = 'active'
            student.save()
            messages.success(request, f"{student.first_name} {student.last_name} {group}ga qo'shildi.")
            return redirect('students_list')
        else:
            messages.warning(request, f"Sizga bu amal uchun admin tomonidan ruxsat berilmagan.")
            return render(request, '404.html')


class EditPasswordView(View):
    def get(self, request, username):
        if request.user.user_role == 'super':
            user = get_object_or_404(CustomUser, username=username)
            context = {
                'user': user
            }
            return render(request, 'edit_password.html', context)
        else:
            messages.warning(request, f"Sizga uchbu amal uchun admin tomonidan ruxsat berilmagan!")
            return render(request, '404.html')

    def post(self, request, username):
        user = get_object_or_404(CustomUser, username=username)
        password = request.POST['password']
        user.set_password(password)
        user.save()
        messages.success(request, "Parol o'zgartirildi.")
        return redirect('index')

class AllGroupsView(View):
    def get(self, request):
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            groups = Group.objects.all()
            context = {
                'groups': groups
            }
            return render(request, 'groups.html', context)
        elif request.user.user_role == 'teacher':
            teacher = request.user
            groups = teacher.group_set.all()
            context = {
                'groups': groups
            }
            return render(request, 'groups.html', context)
        else:
            messages.warning(request, f"Sizga ushbu amal uchun admin tomonidan ruxsat berilmagan")
            return render(request, '404.html')

class GroupDetailView(View):
    def get(self, request, group_id):
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            months = [
                "Yanvar",
                "Fevral",
                "Mart",
                "Aprel",
                "May",
                "Iyun",
                "Iyul",
                "Avgust",
                "Sentabr",
                "Oktabr",
                "Noyabr",
                "Dekabr",
            ]
            year = datetime.now().year
            month = months[int(datetime.now().month) - 1]
            group = get_object_or_404(Group, id=group_id)
            students_gr = GroupStudent.objects.filter(group=group)

            students = []
            for student in students_gr:
                if student.student.user_type == 'active':
                    students.append(student.student)
            payments = Payment.objects.filter(group=group).order_by('-pay_date')
            context = {
                'group': group,
                'students': students,
                'payments': payments,
                'now_year': datetime.now().year,
                'month': month,
                'year': year,
                'months': months,
                'years': [datetime.now().year - 1, datetime.now().year + 1, datetime.now().year + 2]

            }
            return render(request, 'group_detail.html', context)
        elif request.user.user_role == 'teacher':
            teacher = request.user
            months = [
                "Yanvar",
                "Fevral",
                "Mart",
                "Aprel",
                "May",
                "Iyun",
                "Iyul",
                "Avgust",
                "Sentabr",
                "Oktabr",
                "Noyabr",
                "Dekabr",
            ]
            year = datetime.now().year
            month = months[int(datetime.now().month) - 1]
            groups = teacher.group_set.all()
            is_have = False
            for group in groups:
                if group.id == group_id:
                    is_have = True
                    break

            if not is_have:
                messages.warning(request, "Ushbu guruh ma'lumotlarini ko'rish uchun sizga ruxsat berilmagan ")
                return render(request, '404.html')
            group = get_object_or_404(Group, id=group_id)
            students_gr = GroupStudent.objects.filter(group=group)

            students = []
            for student in students_gr:
                if student.student.user_type == 'active':
                    students.append(student.student)
            payments = Payment.objects.filter(group=group).order_by('-pay_date')
            context = {
                'group': group,
                'students': students,
                'payments': payments,
                'now_year': datetime.now().year,
                'month': month,
                'year': year,
                'months': months,
                'years': [datetime.now().year - 1, datetime.now().year + 1, datetime.now().year + 2]

            }
            return render(request, 'group_detail.html', context)
        else:
            messages.warning(request, "Sizga uchbu amal uchun admin tomonidan ruxsat berilmagan.")
            return render(request, '404.html')

class GroupPayment(View):
    def get(self, request, group_id, year, month):
        months = [
            "Yanvar",
            "Fevral",
            "Mart",
            "Aprel",
            "May",
            "Iyun",
            "Iyul",
            "Avgust",
            "Sentabr",
            "Oktabr",
            "Noyabr",
            "Dekabr",
        ]
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            group = get_object_or_404(Group, id=group_id)
            students_gr = GroupStudent.objects.filter(group=group)
            students = []
            q_year = request.GET.get('year')
            q_month = request.GET.get('month')
            if q_year and q_year:
                redirect_url = reverse('group_pay', kwargs={'group_id': group.id, 'year': q_year, 'month': q_month})
                return redirect(redirect_url)
            for student in students_gr:
                students.append(student.student)
            payments = Payment.objects.filter(year=year, month=month, group=group)

            st_py = []
            for student in students:
                is_have = False
                group_student = get_object_or_404(GroupStudent, student=student, group=group)
                sale = group_student.sale
                is_sale = group_student.is_sale
                sale_count = group_student.count
                if payments:
                    for payment in payments:
                        if payment.student.id == student.id:
                            is_have = True
                            break
                        else:
                            payment = None
                else:
                    payment = None
                st_py.append(
                    {
                        'student': student,
                        'is_pay': is_have,
                        'payment': payment,
                        'sale': sale,
                        'is_sale': is_sale,
                        'sale_count': sale_count
                    }
                )

            context = {
                'group': group,
                'st_py': st_py,
                'year': year,
                'month': month,
                'now_year': datetime.now().year,
                'months': months,
                'years': [datetime.now().year - 1, datetime.now().year + 1, datetime.now().year + 2],
                'payments': payments
            }
            print(st_py)
            return render(request, 'group_pay.html', context)
        elif request.user.user_role == 'teacher':
            teacher = request.user
            groups = teacher.group_set.all()
            is_have = False
            for group in groups:
                if group.id == group_id:
                    is_have = True
                    break

            if not is_have:
                messages.warning(request, "Ushbu guruh ma'lumotlarini ko'rish uchun sizga ruxsat berilmagan ")
                return render(request, '404.html')
            group = get_object_or_404(Group, id=group_id)
            students_gr = GroupStudent.objects.filter(group=group)
            students = []
            q_year = request.GET.get('year')
            q_month = request.GET.get('month')
            if q_year and q_year:
                redirect_url = reverse('group_pay', kwargs={'group_id': group.id, 'year': q_year, 'month': q_month})
                return redirect(redirect_url)
            for student in students_gr:
                students.append(student.student)
            payments = Payment.objects.filter(year=year, month=month, group=group)
            if not payments:
                messages.warning(request, f"{year} {month} oyi uchun to'lovlar mavjud emas")
                return render(request, '404.html')
            st_py = []
            for student in students:
                is_have = False
                for payment in payments:
                    if payment.student.id == student.id:
                        is_have = True
                        break
                    else:
                        payment = None
                st_py.append(
                    {
                        'student': student,
                        'is_pay': is_have,
                        'payment': payment,

                    }
                )

            context = {
                'group': group,
                'st_py': st_py,
                'year': year,
                'month': month,
                'now_year': datetime.now().year,
                'months': months,
                'years': [datetime.now().year - 1, datetime.now().year + 1, datetime.now().year + 2],
                'payments': payments
            }
            print(st_py)
            return render(request, 'group_pay.html', context)
        else:
            messages.warning(request, "Sizga uchbu amal uchun admin tomonidan ruxsat berilmagan.")
            return render(request, '404.html')

class AllPayments(View):
    def get(self, request):
        payments = Payment.objects.all().order_by('-pay_date')
        context = {
            'payments': payments
        }
        return render(request, 'payments.html', context)



class StaticticsView(LoginRequiredMixin, View):
    def get(self, request):
        months = [
            "Yanvar",
            "Fevral",
            "Mart",
            "Aprel",
            "May",
            "Iyun",
            "Iyul",
            "Avgust",
            "Sentabr",
            "Oktabr",
            "Noyabr",
            "Dekabr",
        ]
        if request.user.user_role == 'super':
            year = datetime.now().year
            month = months[datetime.now().month-1]
            if request.GET.get('year'):
                year = request.GET.get('year')
            if request.GET.get('month'):
                month = request.GET.get('month')
            all_money = Money.objects.get(id=1)
            all_card = Money.objects.get(id=2)
            all_cash = Money.objects.get(id=3)
            s_am = str(int(all_money.count))
            s_cd = str(int(all_card.count))
            s_cs = str(int(all_cash.count))
            r_am = readnumber(s_am)
            r_cd = readnumber(s_cd)
            r_cs = readnumber(s_cs)
            salaries = GivenSalary.objects.filter(year=year, month=month)
            spendings = Spending.objects.all()
            fil_sp = []
            sp_count = 0
            sp_card = 0
            sp_cash = 0
            sl_count = 0
            sl_card = 0
            sl_cash = 0
            for spending in spendings:
                date = spending.created_date
                date_str = str(date)
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                month_s = months[date_obj.month-1]
                year_s = date_obj.year
                print(month_s)
                print(type(month_s))
                print(type(month))
                print(month)
                if month_s == month and year_s == year:
                    sp_count = sp_count + spending.count
                    sp_card = sp_card + spending.card
                    sp_cash = sp_cash + spending.cash
                    fil_sp.append(spending)
            for salary in salaries:
                sl_count = sl_count + salary.count
                sl_card = sl_card + salary.card
                sl_cash = sl_cash + salary.cash




            context = {
                'all_money': all_money,
                'all_card': all_card,
                'all_cash': all_cash,
                'r_money': r_am,
                'r_card': r_cd,
                'r_cash': r_cs,
                "sl_count": sl_count,
                'sl_cash': sl_cash,
                'sl_card': sl_card,
                'sp_count': sp_count,
                'sp_cash': sp_cash,
                'sp_card': sp_card,
                'salaries': salaries,
                'spendings': fil_sp,
                'year': year,
                'now_year': datetime.now().year,
                'month': month,
                'months': months,
                'years': [datetime.now().year-1, datetime.now().year+1, datetime.now().year+2]
            }


            return render(request, 'statistics.html', context)
        else:
            messages.warning(request, f"Sizga ushbu amal uchun admin tomonidan ruxsat berilmagan")
            return render(request, '404.html')

class GivenSalaryListView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.user_role == 'super':
            given_salaries = GivenSalary.objects.all()
            context = {
                'salaries': given_salaries
            }
            return render(request, 'salary_list.html', context)
        else:
            messages.warning(request, "Sizga uchbu amal uchun admin tomonidan ruxsat berilmagan.")
            return render(request, '404.html')


class AttendanceView(View):
    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        teacher = group.teacher
        if request.user == teacher or request.user.user_role == 'super':
            students = []
            group_students = group.groupstudent_set.all()
            for group_student in group_students:
                if group_student.student.user_type == 'active':
                    students.append(group_student.student)

        else:
            pass

        context = {
            'group': group,
            'students': students
        }
        return render(request, 'attendance.html', context)

    def post(self, request, group_id):
        months = [
            "Yanvar",
            "Fevral",
            "Mart",
            "Aprel",
            "May",
            "Iyun",
            "Iyul",
            "Avgust",
            "Sentabr",
            "Oktabr",
            "Noyabr",
            "Dekabr",
        ]
        group = get_object_or_404(Group, id=group_id)
        teacher = group.teacher
        if request.user == teacher or request.user.user_role == 'super':
            try:
                date = request.POST['date']
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            except Exception as e:
                messages.warning(request, f"Davomat sanasini kiritish majburiy !")
                return redirect('attendance', group_id)


            if Attendance.objects.filter(group=group, day=date_obj.day, year=date_obj.year, month=months[date_obj.month-1]):
                messages.warning(request, f"{date}. {group} guruhi uchun allaqachon davomat olingan")
                return redirect('attendance', group_id)
            attendance = Attendance.objects.create(
                group=group,
                day=date_obj.day,
                year=date_obj.year,
                month=months[date_obj.month-1],

            )
            students = []
            group_students = group.groupstudent_set.all()
            for group_student in group_students:
                if group_student.student.user_type == 'active':
                    students.append(group_student.student)

            count = 0
            for student in students:
                try:
                    on_off = request.POST.get(f"student_{student.username}")
                    print(request.POST.get(f"student_{student.username}"))
                    if on_off == 'on':
                        nb = True
                        count = count + 1
                    else:
                        nb = False
                except Exception as e:
                    messages.error(request, f"{e}")
                attendance_student = AttendanceStudent.objects.create(
                    student=student,
                    attendance=attendance,
                    nb=nb
                )
                attendance_student.save()
            percentage = count/len(students)*100
            attendance.percentage = percentage
            attendance.save()

            messages.info(request, f"{date} uchun davomat qabul qilindi")
            return redirect('index')

class AttendanceHistoryView(View):
    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        teacher = group.teacher
        if request.user == teacher or request.user.user_role == 'super' or request.user.user_role == 'admin':
            attendance = Attendance.objects.filter(group=group).order_by('-created_date')
            context = {
                'attendance': attendance
            }

            return render(request, 'att_history.html', context)
        else:
            messages.warning(request, 'Sizga ushbu amal uchun admin tomonidan ruxsat berilamagan.')
            return render(request, '404.html')

class AttendanceEditView(View):
    def get(self, request, attend_id):
        attend = get_object_or_404(Attendance, id=attend_id)
        teacher = attend.group.teacher
        group = attend.group
        if request.user == teacher or request.user.user_role == 'super':
            att_students = AttendanceStudent.objects.filter(attendance=attend)



        else:
            pass

        context = {
            'group': group,
            'att_students': att_students
        }
        return render(request, 'attendance_edit.html', context)

    def post(self, request, attend_id):
        months = [
            "Yanvar",
            "Fevral",
            "Mart",
            "Aprel",
            "May",
            "Iyun",
            "Iyul",
            "Avgust",
            "Sentabr",
            "Oktabr",
            "Noyabr",
            "Dekabr",
        ]
        attend = get_object_or_404(Attendance, id=attend_id)
        group = attend.group
        teacher = group.teacher
        if request.user == teacher or request.user.user_role == 'super':
            date = request.POST['date']
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            attendance = Attendance.objects.create(
                group=group,
                day=date_obj.day,
                year=date_obj.year,
                month=months[date_obj.month - 1],

            )
            students = []
            group_students = group.groupstudent_set.all()
            for group_student in group_students:
                if group_student.student.user_type == 'active':
                    students.append(group_student.student)

            count = 0
            for student in students:
                try:
                    on_off = request.POST.get(f"student_{student.username}")
                    if on_off == 'on':
                        nb = True
                        count = count + 1
                    else:
                        nb = False
                except Exception as e:
                    messages.error(request, f"{e}")

            percentage = count / len(students) * 100
            attendance.percentage = percentage
            attendance.save()

            messages.info(request, f"{date} uchun davomat qabul qilindi")
            return redirect('index')

class RemoveStudentView(View):
    def get(self, request, username, group_id):
        student = get_object_or_404(CustomUser, username=username, user_role='student')
        group = get_object_or_404(Group, id=group_id)
        if request.user == group.teacher or request.user.user_role == 'admin' or request.user.user_role == 'super':
            if Payment.objects.filter(student=student, group=group):
                student.user_type = 'deleted'
                student.save()
                messages.success(request, f"{student.first_name} {student.last_name} guruhdan chetlashtirildi !")
                return redirect('group_detail', group_id)
            elif GroupStudent.objects.filter(group=group, student=student):
                grst = get_object_or_404(GroupStudent, group=group, student=student)
                grst.delete()
                student.user_type = 'pause'
                student.save()
                messages.success(request, f"{student.first_name} {student.last_name} guruhdan chetlashtirildi !")
                return redirect('group_detail', group_id)
            else:
                messages.warning(request, f'xato')
                return redirect('group_detail', group_id)
        else:
            return redirect('index')


class AddGroupStudent(View):
    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        context = {
            'group': group
        }
        return render(request, 'addstudentbyteacher.html', context)
    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if request.user == group.teacher or request.user.user_role == 'admin' or request.user.user_role == 'super':
            try:
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                phone_number = request.POST['phone_number']
                phone_number2 = request.POST['phone_number2']
            except Exception as e:
                messages.warning(request, 'Xatolik mavjud')

            student = CustomUser.objects.create(
                group=group,
                first_name=first_name,
                last_name=last_name,

                phone_number=phone_number,
                phone_number2=phone_number2,
                user_type='active',
                user_role='student'
            )
            student.save()
            add_gr = GroupStudent.objects.create(student=student, group=group)
            add_gr.save()
        messages.success(request, f"{student.first_name} {student.last_name} {group.name}ga qo'shildi.")
        return redirect('group_detail', group_id)


class CreateGroupView(View):
    def get(self, request):
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            teachers = CustomUser.objects.filter(user_role='teacher')
            days = Days.objects.all()
            course = Course.objects.all()
            context = {
                'teachers': teachers,
                'days': days,
                'course': course
            }
            return render(request, 'create_group.html', context)
        else:
            messages.warning(request, 'Sizga ushbu amal uchun admin tomonidan ruxsta berilmagan')
            return redirect('index')
    def post(self, request):
        teacher_id = request.POST['teacher']
        name = request.POST['name']
        course_id = request.POST['course']
        price = request.POST['price']
        percentage = request.POST['percentage']
        hour = request.POST['hour']
        minute = request.POST['minute']
        day_id = request.POST['day']
        teacher = get_object_or_404(CustomUser, id=teacher_id, user_role='teacher')
        course = get_object_or_404(Course, id=course_id)
        day = get_object_or_404(Days, id=day_id)

        group = Group.objects.create(
            name=name,
            pay=price,
            teacher=teacher,
            day=day,
            hour=hour,
            minut=minute,
            course=course,
            type=True,
            percentage=percentage
        )

        group.save()
        messages.success(request, f"{name} guruhi yaratildi!")
        return redirect('index')


class DeleteStudentView(View):
    def get(self, request, username):
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            student = get_object_or_404(CustomUser, username=username, user_role='student')
            student.delete()
        return redirect('lids_list')

class SettingGroupView(View):
    def get(self, request, group_id, username):
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            group = get_object_or_404(Group, id=group_id)
            student = get_object_or_404(CustomUser, username=username)
            group_student = get_object_or_404(GroupStudent, group=group, student=student)
            is_sale = group_student.is_sale
            sale = group_student.sale
            count = group_student.count
            context = {
                'is_sale': is_sale,
                'sale': sale,
                'count': count,
                'student': student,
                'group': group
            }
            return render(request, 'group_setting.html', context)
        else:
            messages.warning(request, "Sizga ushbu amal uchun ruxsat berilmagan")
            return redirect('index')
    def post(self, request, group_id, username):
        if request.user.user_role == 'admin' or request.user.user_role == 'super':
            group = get_object_or_404(Group, id=group_id)
            student = get_object_or_404(CustomUser, username=username, user_role='student')
            group_student = get_object_or_404(GroupStudent, group=group, student=student)
            is_sale_1 = request.POST.get('is_sale')
            sale_1 = request.POST.get('sale')
            if is_sale_1 == 'on':
                is_sale = True
            else:
                is_sale = False
            if sale_1 == 'on':
                sale = True
            else:
                sale = False
            count = int(request.POST['count'])
            group_student.is_sale = is_sale
            group_student.sale = sale
            group_student.count = count
            group_student.save()

            messages.success(request, 'Chegirma qabul qilindi.')
            return redirect('group_detail', group_id)
        else:
            messages.warning(request, "Sizga ushbu amal uchun ruxsat berilmagan")
            return redirect('index')

class PaymentDeleteView(View):
    def get(self, request, payment_id):
        if request.user.user_role == 'super':
            paymet = get_object_or_404(Payment, id=int(payment_id))
            all_money = Money.objects.get(id=1)
            all_card = Money.objects.get(id=2)
            all_cash = Money.objects.get(id=3)

            all_money.count = all_money.count - paymet.count
            all_card.count = all_card.count - paymet.card
            all_cash.count = all_cash.count - paymet.cash

            all_money.save()
            all_card.save()
            all_cash.save()
            paymet.delete()
            messages.success(request, f"To'lov o'chirildi")
            return redirect('payments')


        else:
            messages.success(request, f"Faqat super admin kirishi mumkin")
            return render(request, '404.html')
