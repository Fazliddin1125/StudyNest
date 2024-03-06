from django.urls import path
from .views import IndexView, PaymentView, PaymentDetailView,\
    StudentsView, LidsView, TestView, DeptView, TeacherView, \
    SalaryCalculateView, SpendingView, GroupStudentView, \
    EditPasswordView, AllGroupsView, GroupDetailView, GroupPayment, \
    AllPayments, StaticticsView, GivenSalaryListView, AttendanceView, \
    AttendanceHistoryView, RemoveStudentView, AddGroupStudent, CreateGroupView, DeleteStudentView, \
    SettingGroupView, PaymentDeleteView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('payment/<slug:username>/', PaymentView.as_view(), name='payment'),
    path('payment/<int:payment_id>/edit/', PaymentDetailView.as_view(), name='payment_edit'),
    path('student/', StudentsView.as_view(), name='students_list'),
    path('lids/', LidsView.as_view(), name='lids_list'),
    path('newstudent/', TestView.as_view(), name='test_list'),
    path('deptstudent/', DeptView.as_view(), name='dept_list'),
    path('teachers/', TeacherView.as_view(), name='teachers'),
    path('teachers/<slug:username>/<int:year>/<slug:month>/', SalaryCalculateView.as_view(), name='teacher_detail'),
    path('spending/', SpendingView.as_view(), name='spending'),
    path('student/add-group/<slug:username>/', GroupStudentView.as_view(), name='add_group'),
    path('edit-password/<slug:username>/', EditPasswordView.as_view(), name='edit_password'),
    path('group/', AllGroupsView.as_view(), name='groups'),
    path('statistics/', StaticticsView.as_view(), name='statistics'),
    path('group/<int:group_id>', GroupDetailView.as_view(), name='group_detail'),
    path('group/<int:group_id>/<int:year>/<slug:month>/', GroupPayment.as_view(), name='group_pay'),
    path('payments/', AllPayments.as_view(), name='payments'),
    path('g-salary/', GivenSalaryListView.as_view(), name='given_salary'),
    path('attendance/<int:group_id>/', AttendanceView.as_view(), name='attendance'),
    path('attendance/history/<int:group_id>/', AttendanceHistoryView.as_view(), name='attendance_history'),
    path('remove/<slug:username>/<int:group_id>/', RemoveStudentView.as_view(), name='remove'),
    path('add/<int:group_id>/', AddGroupStudent.as_view(), name='add_student_group'),
    path('create/group/', CreateGroupView.as_view(), name='create_group'),
    path('delete/<slug:username>/', DeleteStudentView.as_view(), name='delete_student'),
    path('delete/payment/<int:payment_id>', PaymentDeleteView.as_view(), name='delete_payment'),
    path('setting/<int:group_id>/<slug:username>/', SettingGroupView.as_view(), name='setting_group'),
]