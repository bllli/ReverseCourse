import json

from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.contrib import auth
from django.contrib import messages

from .models import Article, Course
from .forms import LoginForm


def index(request):
    return render(request, 'index.html')


def login(request):
    if request.user.is_authenticated():
        messages.warning(request, '用户 {username}, 你已经登陆'.format(username=request.user.username))
        return HttpResponseRedirect('/')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            messages.success(request, '欢迎回来, {username}'.format(username=request.user.username))
            return HttpResponseRedirect('/')
        else:
            messages.error(request, '账号或密码错误')
    return render(request, 'login.html', {'login_form': form})


def logout(request):
    messages.success(request, '登出成功, Bye~')
    auth.logout(request)
    return HttpResponseRedirect('/')


def courses(request):
    queryset = Course.objects.all()
    query = request.GET.get('query') or None
    if query:
        queryset = queryset.filter(title__contains=query)
    p = Paginator(queryset, 5)
    page = request.GET.get('page') or 1
    try:
        course_list = p.page(page)
    except PageNotAnInteger:
        course_list = p.page(1)
    except EmptyPage:
        course_list = p.page(p.num_pages)
    print(course_list.number)
    return render(request, 'courses.html', {
        'courses': course_list,
        'query': query,
    })


def course(request, course_id):
    c = Course.objects.filter(pk=course_id).first()
    return render(request, 'course.html', {
        'course': c,
        'articles': c.article_set.all(),
    })
