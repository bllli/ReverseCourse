from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

from backend import models


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=20, help_text='请输入您的用户名')
    password = forms.CharField(label='密码', widget=forms.PasswordInput())


class CreateGroupForm(forms.Form):
    name = forms.CharField(label='团队名', max_length=20)

    def clean(self):
        name = self.cleaned_data.get('name', None)
        if models.CourseGroup.objects.filter(name=name).exists():
            raise forms.ValidationError('这个名字已经有人捷足先登了，换一个试试吧')


class LetterForm(forms.Form):
    content = forms.CharField(label='信件内容')


class TaskForm(forms.Form):
    content = forms.CharField(label='内容')


class ScoreForm(forms.Form):
    comment = forms.CharField(label='评价内容')
    score = forms.IntegerField(label='得分')
