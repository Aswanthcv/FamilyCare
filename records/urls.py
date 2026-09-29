from django.urls import path

from . import views

app_name = 'records'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.home, name='dashboard'),
    path('members/add/', views.add_member, name='add_member'),
    path('members/<int:member_id>/', views.member_detail, name='member_detail'),
    path('members/<int:member_id>/edit/', views.edit_member, name='edit_member'),
    path('members/<int:member_id>/delete/', views.delete_member, name='delete_member'),
    path('members/<int:member_id>/tests/add/', views.add_test_result, name='add_test_result'),
    path('test-results/<int:test_result_id>/edit/', views.edit_test_result, name='edit_test_result'),
    path('test-results/<int:test_result_id>/delete/', views.delete_test_result, name='delete_test_result'),
    path('test-results/<int:test_result_id>/report/', views.view_test_report, name='view_test_report'),
    path('members/<int:member_id>/medical-reports/add/', views.add_medical_report, name='add_medical_report'),
    path('medical-reports/<int:report_id>/edit/', views.edit_medical_report, name='edit_medical_report'),
    path('medical-reports/<int:report_id>/delete/', views.delete_medical_report, name='delete_medical_report'),
    path('medical-reports/<int:report_id>/report/', views.view_medical_report, name='view_medical_report'),
    path('members/<int:member_id>/doctor-visits/add/', views.add_doctor_visit, name='add_doctor_visit'),
    path('doctor-visits/<int:visit_id>/edit/', views.edit_doctor_visit, name='edit_doctor_visit'),
    path('doctor-visits/<int:visit_id>/', views.doctor_visit_detail, name='doctor_visit_detail'),
    path('doctor-visits/<int:visit_id>/delete/', views.delete_doctor_visit, name='delete_doctor_visit'),
    path('doctor-visits/<int:visit_id>/document/', views.view_visit_document, name='view_visit_document'),
    path('', views.home, name='home'),
]
