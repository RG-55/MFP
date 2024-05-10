from django.urls import path
from . import views 

urlpatterns = [
    path('', views.employees, name='employees'),
    path('add_employee', views.add_employee, name='add_employee'),
    path('update_employee/<int:pk>', views.update_employee, name='update_employee'),
    path('payslips', views.payslips, name='payslips'),
    path('delete_employee/<int:pk>/', views.delete_employee, name='delete_employee'), 
    path('add_overtime/<int:pk>/', views.add_overtime, name='add_overtime'), 
    path('view_payslip/<int:pk>/', views.view_payslip, name='view_payslip'), 
]