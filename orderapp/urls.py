from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.MenuPage, name='menu'),
    path('cart/', views.CartPage, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
]