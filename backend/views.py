from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, mixins, generics
from rest_framework.decorators import api_view
from rest_framework import authentication
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.serializers import UserSerializer, GroupSerializer, ArticleSerializer, CourseSerializer
from backend.models import Article, Course
from backend.permissions import IsOwnerOrReadOnly


class DefaultMixin(object):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
        authentication.TokenAuthentication
    )

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    pagination_by = 25
    pagination_by_param = 'page_size'
    max_pagination_by = 100


class IsOwnerOrReadOnlyMixin(DefaultMixin):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    )


class UserViewSet(DefaultMixin, viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(DefaultMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class UserView(APIView):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.BasicAuthentication
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': str(request.user),
            'auth': str(request.auth)
        }
        return Response(content)


class ArticleViewSet(IsOwnerOrReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CourseViewSet(IsOwnerOrReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
