from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView, PasswordsChangeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/<slug:username>', ProfileView.as_view(), name='profile'),
    path('profile/change-password/', PasswordsChangeView.as_view(template_name='change_password.html'), name='change_password'),
]