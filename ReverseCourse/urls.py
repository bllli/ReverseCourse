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
    # 站内信
    url(r'^letter/', include([
        url(r'^inbox/$', views.inbox, name='inbox'),
    ])),
    # course
    url(r'^courses/', include([
        url(r'^(\d+)/$', views.course_detail, name='course_detail'),
        url(r'^$', views.courses, name='courses'),
    ])),
    # user
    url(r'^users/(\w+)/$', views.user_detail, name='user_detail'),
    # group
    url(r'^groups/', include([
        url(r'^create/(\d+)/$', views.create_group, name='create_group'),
        url(r'^(\d+)/$', views.group_detail, name='group_detail'),
        url(r'^$', views.groups, name='groups')
    ]), name='group'),
    # invite 邀请
    url(r'^invite/', include([
        url(r'^(\d+)/(\d+)$', views.invite_into_group, name='invite_into_group'),
        url(r'^apply/(\d+)/$', views.apply_into_group, name='apply_into_group'),
        url(r'^accept/(.*)$', views.accept_invite, name='accept_invite'),
        url(r'^refuse/(.*)$', views.refuse_invite, name='refuse_invite'),
    ])),
    # index
    url(r'^$', views.index, name='index'),
]
