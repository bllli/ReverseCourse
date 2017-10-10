from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Course(models.Model):
    title = models.CharField(max_length=200)

    create_date = models.DateTimeField(default=now)

    group_members_min = models.IntegerField(default=1)
    group_members_max = models.IntegerField(default=20)

    detail = models.OneToOneField('Article', null=True)
    author = models.ForeignKey(User)

    def __str__(self):
        return '<Course: %s by %r>' % (self.title, self.author)

    class Meta:
        ordering = ('create_date',)


class CourseGroup(models.Model):
    name = models.CharField(max_length=100)

    belong = models.ForeignKey(Course)

    creator = models.ForeignKey(User, related_name='my_groups')
    members = models.ManyToManyField(User, related_name='added_groups')

    locked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

    def is_creator(self, user):
        if self.creator is user:
            return True
        return False

    def in_group(self, user):
        return user in self.members.all() or user is self.creator

    def join(self, user):
        if not self.is_creator(user):
            self.members.add(user)

    def leave(self, user):
        if self.in_group(user):
            self.members.remove(user)

    def disband(self):
        self.delete()


class Comment(models.Model):
    STARS = (
        ('1', '一星'),
        ('2', '两星'),
        ('3', '三星'),
        ('4', '四星'),
        ('5', '五星'),
    )
    author = models.ForeignKey(User)
    article = models.ForeignKey('Article')
    star = models.CharField(choices=STARS, max_length=1)
    comment = models.TextField()

    create_date = models.DateTimeField(default=now)

    def __str__(self):
        return 'to %r, %s' % (self.article.title, self.star)


class Article(models.Model):
    title = models.CharField(max_length=200)
    content_md = models.TextField(null=True)
    content_html = models.TextField(null=True)

    author = models.ForeignKey(User, related_name='article_set')
    belong = models.ForeignKey(Course, related_name='article_set', null=True)

    create_date = models.DateTimeField(default=now)

    def add_comment(self, user, star, comment):
        self.comment_set.create(author=user, star=star, comment=comment)

    def __str__(self):
        return '<Article: %s by %r>' % (self.title, self.author)
