from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.reverse import reverse

from backend.models import Article, Course


class UserSerializer(serializers.HyperlinkedModelSerializer):
    article_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Article.objects.all())

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups', 'article_set')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


#
# class CourseSerializer(serializers.Serializer):
#     pk = serializers.IntegerField(read_only=True)
#     # title =


# class ArticleSerializer(serializers.Serializer):
#     pk = serializers.IntegerField(read_only=True)
#     title = serializers.CharField(required=False, allow_blank=True, max_length=200)
#     content_md = serializers.CharField()
#     author_id = serializers.DjangoModelField(User)
#
#     def create(self, validated_data):
#         return Article.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         instance.title = validated_data.get('title', instance.title)
#         instance.content_md = validated_data.get('content_md', instance.title)
#         instance.save()
#         return instance


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()

    belong = serializers.HyperlinkedRelatedField(
        view_name='course-detail',
        queryset=Course.objects.all()
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
