from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User, Group,Permission

class CustomUserChangeForm(UserChangeForm):
    # groups = forms.ModelMultipleChoiceField(
    #     queryset=Group.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False
    # )
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions', 'password']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']

class user_email_form(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'User Email','type':'email'}),
            }