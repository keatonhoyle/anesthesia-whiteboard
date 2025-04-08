from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('edit/<str:room>/', views.edit_entry, name='edit_entry'),
    path('add/', views.add_entry, name='add_entry'),
    path('login/', views.login_view, name='login'),
    path('select-division/', views.select_division, name='select_division'),
    path('select-hospital/', views.select_hospital, name='select_hospital'),
    path('logout/', views.logout_view, name='logout'),
]