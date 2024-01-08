from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.urls import reverse
from django.views import View
from users.models import CustomUser
from .models import Group, GroupStudent, Payment, Money, Spending, KindOfSpending, GivenSalary
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
            context = {
                'user': user,
                'groups': groups
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

        if group.pay > count:
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
                context = {
                    'payment': payment,
                    'groups': groups,
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

            if group.pay > count:
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

                    student = group_student.student

                    payments = student.payment_set.filter(month=month, group=group, year=year)

                    for payment in payments:
                        all_payments.append(payment)
                        gr_count = gr_count + (payment.count*group.percentage/100)
                        count = count + (payment.count*group.percentage/100)
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
            if not payments:
                messages.warning(request, f"{year} { month } oyi uchun to'lovlar mavjud emas")
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





