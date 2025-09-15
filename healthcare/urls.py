from django.urls import path
from . import views

app_name = 'healthcare'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('demo-login/<str:user_type>/', views.demo_login_view, name='demo_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('debug/', views.debug_user_info, name='debug_user_info'),
    path('admin/manage-users/', views.admin_manage_users, name='admin_manage_users'),
    path('admin/view-analytics/', views.admin_view_analytics, name='admin_view_analytics'),
    path('admin/appointments/', views.admin_appointments, name='appointments'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/reports/user/', views.user_reports, name='user_reports'),
    path('admin/reports/appointment/', views.appointment_reports, name='appointment_reports'),
    path('admin/reports/financial/', views.financial_reports, name='financial_reports'),
    path('admin/reports/system/', views.system_reports, name='system_reports'),
    path('admin/reports/download/<str:report_type>/', views.download_pdf, name='download_pdf'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    path('admin/backup/', views.admin_backup, name='admin_backup'),
    path('admin/export-data/', views.admin_export_data, name='admin_export_data'),
    path('admin/update-profile/', views.admin_update_profile, name='admin_update_profile'),
    path('admin/change-password/', views.admin_change_password, name='admin_change_password'),
    
    # Doctor Dashboard Actions
    path('doctor/add-patient/', views.add_patient, name='add_patient'),
    path('doctor/add-doctor/', views.add_doctor, name='add_doctor'),
    path('doctor/book-appointment/', views.book_appointment, name='book_appointment'),
    path('doctor/view-reports/', views.view_reports, name='view_reports'),
    path('doctor/start-consultation/', views.start_consultation, name='start_consultation'),
    path('doctor/show-appointments/', views.show_appointments, name='show_appointments'),
    path('doctor/my-patients/', views.my_patients, name='my_patients'),
    path('doctor/schedule/', views.schedule, name='schedule'),
    path('doctor/manage-schedule/', views.manage_schedule, name='manage_schedule'),
    path('doctor/request-time-off/', views.request_time_off, name='request_time_off'),
    path('doctor/prescriptions/', views.prescription_history, name='prescription_history'),
    path('doctor/prescriptions/new/', views.create_prescription, name='create_prescription'),
    path('doctor/settings/', views.doctor_settings, name='doctor_settings'),
    path('doctor/settings/update-profile/', views.doctor_update_profile, name='doctor_update_profile'),
    path('doctor/settings/change-password/', views.doctor_change_password, name='doctor_change_password'),
    path('doctor/settings/notification-settings/', views.doctor_notification_settings, name='doctor_notification_settings'),
    path('doctor/settings/practice-settings/', views.doctor_practice_settings, name='doctor_practice_settings'),
    
    # Patient Details
    path('patient/<int:id>/', views.view_patient, name='view_patient'),
    
    # Doctor Details
    path('doctor/<int:id>/', views.view_doctor, name='view_doctor'),
    
    # CSRF Test
    path('test-csrf/', views.test_csrf, name='test_csrf'),
]
