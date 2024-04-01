from django.contrib import admin
from .models import Menu, OrderDate, OrderTable, Supplier

admin.site.register(Menu)
admin.site.register(Supplier)
admin.site.register(OrderDate)
admin.site.register(OrderTable)
