from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register_patient/', views.register, {'role': 'patient'}, name='register_patient'),
    path('register_doctor/', views.register, {'role': 'doctor'}, name='register_doctor'),
    path('register_staff/', views.register, {'role': 'staff'}, name='register_staff'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('delete_appointment/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('manage_appointments/', views.manage_appointments, name='manage_appointments'),
    path('add_inventory/', views.add_inventory, name='add_inventory'),
    path('update_inventory/<int:id>/', views.update_inventory, name='update_inventory'),
    path('view_prescriptions/', views.view_prescriptions, name='view_prescriptions'),
    path('delete_prescription/<int:prescription_id>/', views.delete_prescription, name='delete_prescription'),
    path('generate-bill/<int:prescription_id>/', views.generate_bill, name='generate_bill'),
    path('view_prescriptions_and_bills/', views.view_prescriptions_and_bills, name='view_prescriptions_and_bills'),
    path('delete_bill/<int:bill_id>/', views.delete_bill, name='delete_bill'),
    path('manage_prescriptions/<int:patient_id>/', views.manage_prescriptions, name='manage_prescriptions'),
    path('update_prescription/<int:prescription_id>/', views.update_prescription, name='update_prescription'),
    path('inventory/<int:id>/delete/', views.delete_inventory, name='delete_inventory'),
    path('add_doctor/', views.add_doctor, name='add_doctor'),
    path('add_staff/', views.add_staff, name='add_staff'),
    path('delete_doctor/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
    path('delete_staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
]
    
