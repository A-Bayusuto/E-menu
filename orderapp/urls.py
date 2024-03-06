from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.MenuPage, name='menu'),
    path('cart/', views.CartPage, name='cart'),
]