from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=20, help_text='请输入您的用户名')
    password = forms.CharField(label='密码', widget=forms.PasswordInput())

    # def clean(self):


class CreateGroupForm(forms.Form):
    name = forms.CharField(label='团队名', max_length=20)
