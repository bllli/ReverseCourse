from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.reverse import reverse

from backend.models import Article, Course


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups', 'password')


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
    url_field_name = 'url'
    serializer_url_field = 'url'
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        required=True,
    )

    url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('url', 'title', 'content_md', 'author')

    def get_url(self, obj):
        request = self.context['request']
        return reverse('article-detail', kwargs={'pk': obj.pk}, request=request)


class CourseSerializer(serializers.ModelSerializer):
    article_set = ArticleSerializer(many=True, read_only=True)

    url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('url', 'title', 'article_set')

    def get_url(self, obj):
        request = self.context['request']
        return reverse('course-detail', kwargs={'pk': obj.pk}, request=request)
