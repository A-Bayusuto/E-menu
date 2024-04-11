from django import forms
from .models import OrderTable

class OrderStatusForm(forms.ModelForm):
    ORDER_STATUS_CHOICES = [
        ('Finished', 'Finished'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
    ]
    
    order_status = forms.ChoiceField(choices=ORDER_STATUS_CHOICES)

    class Meta:
        model = OrderTable
        fields = ['order_status']