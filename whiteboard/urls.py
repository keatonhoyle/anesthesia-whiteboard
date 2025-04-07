from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('edit/<str:room>/', views.edit_entry, name='edit_entry'),
    path('add/', views.add_entry, name='add_entry'),
]