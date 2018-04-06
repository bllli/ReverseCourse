# -*- coding:utf-8 -*-
from django.conf.urls import url

from backend import course_views

urlpatterns = [
    url(r'^(\d+)/$', course_views.course_detail, name='detail'),
    url(r'^$', course_views.courses, name='list'),
    url(r'^task/(\d+)/$', course_views.task_list, name='task_list'),
]
