from django.contrib import admin
from .models import Menu, OrderDate, OrderTable, Supplier, UserProfile

class MenuAdmin(admin.ModelAdmin):
    list_display = ('item', 'category', 'price', 'cost_price', 'supplier', 'inStock')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            user_groups = request.user.groups.values_list('name', flat=True)
            if user_groups.exists():
                return qs.filter(supplier__name__in=user_groups)
            else:
                return qs.none()
        
class OrderTableAdmin(admin.ModelAdmin):
    list_display = ('table_id', 'supplier', 'menu', 'order_date', 'order_id', 'qty', 'total', 'total_cost', 'profit', 'order_status')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            # Get the group (supplier) the user belongs to
            user_groups = request.user.groups.values_list('name', flat=True)
            if user_groups.exists():
                return qs.filter(supplier__name__in=user_groups)
            else:
                # Return an empty queryset if the user is not in any supplier group
                return qs.none()

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'supplier')

# Register the models with their respective custom admin classes
admin.site.register(Menu, MenuAdmin)
admin.site.register(Supplier)
admin.site.register(OrderDate)
admin.site.register(OrderTable, OrderTableAdmin)
