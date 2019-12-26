from django import forms
from django.core.exceptions import ValidationError
import re
from django.conf import settings

class UsernameField(forms.SlugField):
    def validate(self, value):
        super(UsernameField, self).validate(value)
        found_s = re.findall(r'^[\w-]+$', value)
        valid = bool(found_s) and found_s[0] == value
        if not valid:
            raise ValidationError('%s contains illegal characters for username' % value)
        for c in value:
            if c.isupper():
                raise ValidationError('Use only lowercase letters in username')

class VerificationField(forms.CharField):
    def validate(self, value):
        super(VerificationField, self).validate(value)
        valid = value.lower() == settings.VERIFICATION_ANSWER
        if not valid:
            raise ValidationError('%s is wrong answer for verification question' % value)

class NewUserForm(forms.Form):
    username = UsernameField(label='Username', help_text='Lowercase letters a-z only', max_length=100)
    first_name = forms.CharField(label='First name', max_length=100)
    last_name = forms.CharField(label='Last name', max_length=100)
    email = forms.EmailField(label='E-mail', max_length=100)
    password = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password (again)', max_length=100, widget=forms.PasswordInput)
    antispam = VerificationField(label='Verification question', max_length=100, help_text=settings.VERIFICATION_QUESTION)

    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password']

class PasswordChangeForm(forms.Form):
    username = UsernameField(label='Username', help_text='Lowercase letters a-z only', max_length=100)
    oldpassword = forms.CharField(label='Current password', max_length=100, widget=forms.PasswordInput)
    password = forms.CharField(label='New password', max_length=100, widget=forms.PasswordInput)
    password2 = forms.CharField(label='New password (again)', max_length=100, widget=forms.PasswordInput)
