from django import forms
from .models import OrderTable
from django.contrib.auth.models import Group
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
    def __init__(self, *args, **kwargs):
        user_groups = kwargs.pop('user_groups', None)
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        if user_groups:
            self.fields['groups'].queryset = user_groups

    class Meta(UserChangeForm.Meta):
        exclude = ('password', 'is_superuser', 'user_permissions', 'last_login', 'date_joined')


class CustomUserChangeFormSuperUser(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        exclude = ('password', 'is_superuser', 'user_permissions', 'last_login', 'date_joined')

class CustomPasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the old password field from the form
        del self.fields['old_password']