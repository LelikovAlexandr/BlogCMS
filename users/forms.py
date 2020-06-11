from django import forms

from users.models import User


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'subscribe_until', 'date_joined', 'init_password')
