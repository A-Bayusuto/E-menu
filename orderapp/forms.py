from django import forms
from .models import OrderTable
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm as DjangoPasswordChangeForm


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


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        exclude = ('password', 'is_superuser', 'user_permissions')

class CustomPasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the old password field from the form
        del self.fields['old_password']