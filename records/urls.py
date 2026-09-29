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
    path('', views.home, name='home'),
]
