from django import forms

class NewUserForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    first_name = forms.CharField(label='First name', max_length=100)
    last_name = forms.CharField(label='Last name', max_length=100)
    email = forms.EmailField(label='E-mail', max_length=100)
    password = forms.CharField(label='Password', max_length=100)
    password2 = forms.CharField(label='Password (again)', max_length=100)
    antispam = forms.CharField(label='Verification question', max_length=100)

