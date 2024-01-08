from django.contrib.auth import login, logout
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserCreateForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import CustomUser

class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('index')


class RegisterView(View):
    def get(self, request):
        if request.user.user_role == 'admin':
            return render(request, 'student_register.html')
        elif request.user.user_role == 'super':
            form = UserCreateForm()
            context = {
                'form': form
            }
            return render(request, 'register.html', context)
        else:
            messages.warning(request, "Sizga bu amal uchun admin tomonidan ruxsat berilmagan!")
            return render(request, '404.html')

    def post(self, request):
        if request.user.user_role == 'super':
            form = UserCreateForm(data=request.POST)
            if form.is_valid():
                form.save()
                return redirect('index')
            else:
                form = UserCreateForm()
                context = {
                    'form': form
                }
                return render(request, 'register.html', context)
        elif request.user.user_role == 'admin':
            all_users = CustomUser.objects.all()

            username = request.POST['username']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            password = request.POST['password']
            phone_number = request.POST['phone_number']
            user_role = 'student'
            user_type = 'stater'
            is_have = False

            for user in all_users:
                if user.username == username:
                    is_have = True
                    break

            if not is_have:
                student = CustomUser.objects.create(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    user_role=user_role,
                    user_type=user_type
                )
                student.set_password(password)
                student.save()
                messages.success(request, f"{first_name} {last_name} ro'yxatga olindi.")
                return render(request, 'student_register.html')
            else:
                messages.warning(request, f"{username} usernamesiga ega foydalanuvchi allaqachon mavjud.")
                return render(request, 'student_register.html')







class LoginView(View):
    def get(self, request):
        login_form = AuthenticationForm()
        return render(request, 'login.html', {'form': login_form})
    def post(self, request):
        login_form = AuthenticationForm(data=request.POST)

        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            messages.success(request, "Kirish muvaffaqiyatli amalga oshirildi.")

            return redirect("index")
        return render(request, 'login.html', {'form': login_form})

class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.info(request, "Muvaffaqiyatli chiqishni amalga oshirdingiz")
        return render(request, '404.html')

class ProfileView(LoginRequiredMixin, View):
    def get(self, request, username):
        if request.user.username == username:
            user = CustomUser.objects.get(username=username)
            context = {
                'user': user
            }
            return render(request, 'profile.html', context)
        else:
            messages.warning(request, 'Sizga uchbu sahifaga kirish mumkin emas')
            return render(request, '404.html')

    def post(self, request, username):
        if request.user.username == username:
            all_users = CustomUser.objects.all()
            user = CustomUser.objects.get(username=username)
            if not request.POST['username'] == '' or request.POST['first_name'] == '' or request.POST['last_name'] == '' or request.POST['phone_number'] == '':
                username = request.POST['username']
                is_have = False

                for prof in all_users:
                    if prof.username == username:
                        is_have = True
                        break
                if user.username == username:
                    is_have = False
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                phone_number = request.POST['phone_number']
                phone_number2 = request.POST['phone_number2']

                if not is_have:
                        user.username = username
                        user.first_name = first_name
                        user.last_name = last_name
                        user.phone_number = phone_number
                        user.phone_number2 = phone_number2
                        user.save()
                        messages.success(request, "Profilingiz muvaffaqiyatli o'zgartirildi.")
                        redirect_url = reverse('profile', kwargs={'username': user.username})
                        return redirect(redirect_url)
                else:
                    messages.warning(request, f"{username} usernamesiga ega foydalanuvchi allaqachon mavjud")
                    redirect_url = reverse('profile', kwargs={'username': user.username})
                    return redirect(redirect_url)
            else:
                redirect_url = reverse('profile', kwargs={'username': user.username})
                messages.warning(request, f"Barcha ma'lumotlarni to'liq holatda kiriting")
                return redirect(redirect_url)
            context = {
                'user': user
                }
            return render(request, 'profile.html', context)
        else:
            messages.warning(request, 'Sizga uchbu sahifaga kirish mumkin emas')
            return render(request, '404.html')
