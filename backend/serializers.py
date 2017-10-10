from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.reverse import reverse

from backend.models import Article, Course


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

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
        fields = ('id', 'url', 'title', 'content_md', 'author', 'belong')

    def get_url(self, obj):
        request = self.context['request']
        return reverse('article-detail', kwargs={'pk': obj.pk}, request=request)


class CourseSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    url = serializers.SerializerMethodField()

    author = serializers.ReadOnlyField(source='author.username')

    article_set = ArticleSerializer(many=True, read_only=True)

    detail = ArticleSerializer()

    class Meta:
        model = Course
        fields = ('id', 'url', 'title', 'author', 'article_set', 'detail')

    def get_url(self, obj):
        request = self.context['request']
        return reverse('course-detail', kwargs={'pk': obj.pk}, request=request)

    def create(self, validated_data):
        request = self.context['request']
        course = Course.objects.create(title=validated_data.get('title'),
                                       author=request.user)
        if validated_data.get('detail'):
            course.detail = Article.objects.create(title=validated_data.get('detail').get('title'),
                                                   content_md=validated_data.get('detail').get('content_md'),
                                                   author=request.user)
            course.save()
        return course

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title')
        if instance.detail:
            instance.detail.title = validated_data.get('detail').get('title')
            instance.detail.content_md = validated_data.get('detail').get('content_md')
            instance.detail.belong = None
            instance.detail.save()
        else:
            instance.detail = Article.objects.create(title=validated_data.get('detail').get('title'),
                                                     content_md=validated_data.get('detail').get('content_md'),
                                                     author=instance.author)
        instance.save()
        return instance


class UserSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    article_set = ArticleSerializer(many=True, read_only=True)
    course_set = CourseSerializer(many=True, read_only=True)

    # article_set = serializers.HyperlinkedRelatedField(view_name='article-detail', read_only=True, many=True)
    # course_set = serializers.HyperlinkedRelatedField(view_name='article-detail', read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'groups', 'article_set', 'course_set')
