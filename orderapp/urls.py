from django.urls import path
from . import views

urlpatterns = [
    path('menu/', views.MenuPage, name='menu'),
    path('cart/', views.CartPage, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orderlist/', views.orderlist, name='orderlist'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('analytics/sales/', views.sales_analytics, name='sales_analytics'),
    path('analytics/menu/', views.menu_analytics, name='menu_analytics'),
]