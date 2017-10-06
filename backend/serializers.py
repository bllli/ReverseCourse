from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.reverse import reverse

from backend.models import Article, Course


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()

    belong = serializers.HyperlinkedRelatedField(
        view_name='course-detail',
        queryset=Course.objects.all(),
        allow_null=True,
        required=False
    )

    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Article
        fields = ('url', 'title', 'content_md', 'author', 'belong')

    def get_url(self, obj):
        request = self.context['request']
        return reverse('article-detail', kwargs={'pk': obj.pk}, request=request)


class CourseSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    author = serializers.ReadOnlyField(source='author.username')

    article_set = ArticleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('url', 'title', 'author', 'article_set')

    def get_url(self, obj):
        request = self.context['request']
        return reverse('course-detail', kwargs={'pk': obj.pk}, request=request)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    article_set = ArticleSerializer(many=True, read_only=True)
    course_set = CourseSerializer(many=True, read_only=True)
    # article_set = serializers.HyperlinkedRelatedField(view_name='article-detail', read_only=True, many=True)
    # course_set = serializers.HyperlinkedRelatedField(view_name='article-detail', read_only=True, many=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups', 'article_set', 'course_set')
