from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('edit/<str:room>/', views.edit_entry, name='edit_entry'),
    path('add/', views.add_entry, name='add_entry'),
    path('login/', views.login_view, name='login'),
    path('select-site/', views.select_site, name='select_site'),
    path('logout/', views.logout_view, name='logout'),
]