"""ReverseCourse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
import notifications.urls

from backend import views

urlpatterns = [
    # Admin
    url(r'^admin/', admin.site.urls),
    # django-notifications-hq
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    # auth
    url(r'^auth/', include([
        url(r'^login/$', views.login, name='login'),
        url(r'^logout/$', views.logout, name='logout'),
    ]), name='auth'),
    # course
    url(r'^courses$', views.courses, name='courses'),
    url(r'^courses/(\d+)/$', views.course, name='course'),
    url(r'^users/(\w+)/$', views.user_detail, name='user_detail'),
    # group
    url(r'^groups/', include([
        url(r'^create/(\d+)/$', views.create_group, name='create_group'),
        url(r'^(\d+)/$', views.group_detail, name='group_detail'),
        url(r'^$', views.groups, name='groups')
    ]), name='group'),
    # index
    url(r'^$', views.index, name='index'),
]
