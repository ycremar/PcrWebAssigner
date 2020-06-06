from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import password_validation
from django.utils.translation import gettext, gettext_lazy as _


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label=_("游戏内名称"), required=True, help_text='游戏内名称',\
        widget = forms.TextInput(attrs = {'class': 'w3-input w3-center'}))
    password1 = forms.CharField(
        label=_("密码"),
        strip=False,
        widget=forms.PasswordInput(attrs = {'class': 'w3-input w3-center'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("确认密码"),
        widget=forms.PasswordInput(attrs = {'class': 'w3-input w3-center'}),
        strip=False,
        help_text=_("输入和上面一致的密码。"),
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'password1', 'password2',)
        widgets = {
            'username': forms.TextInput(attrs = {'class': 'w3-input w3-center'}),
        }
        
class AdminChangePasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs = {'class': 'w3-input w3-center'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs = {'class': 'w3-input w3-center'}),
    )

class ChangePasswordForm(AdminChangePasswordForm):
    error_messages = {
        **SetPasswordForm.error_messages,
        'password_incorrect': _("Your old password was entered incorrectly. Please enter it again."),
    }
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'w3-input w3-center', 'autofocus': True}),
    )
    
    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password