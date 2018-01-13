from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

from backend import models


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=20, help_text='请输入您的用户名')
    password = forms.CharField(label='密码', widget=forms.PasswordInput())

    def update(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = auth.authenticate(username=username, password=password)
        return user

    def clean(self):
        user = self.update()
        if not user or not user.is_active:
            raise forms.ValidationError('登录失败,账号或密码错误')


class CreateGroupForm(forms.Form):
    name = forms.CharField(label='团队名', max_length=20)

    def clean(self):
        name = self.cleaned_data.get('name', None)
        if models.CourseGroup.objects.get(name=name):
            raise forms.ValidationError('这个名字已经有人捷足先登了，换一个试试吧')


class LetterForm(forms.Form):
    content = forms.CharField(label='信件内容')
