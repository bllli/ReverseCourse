import string
import random

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name='课程名称')

    create_date = models.DateTimeField(default=now)

    group_members_min = models.IntegerField(default=1, verbose_name='团队成员下限')
    group_members_max = models.IntegerField(default=20, verbose_name='团队成员上限')

    detail = models.OneToOneField('Article', null=True, blank=True, verbose_name='课程详情')
    author = models.ForeignKey(User, verbose_name='发布者(教师)')

    def __str__(self):
        return '课程: %s' % self.title

    def __repr__(self):
        return '<Course: %s by %s>' % (self.title, self.author)

    class Meta:
        ordering = ('create_date',)


class CourseGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name='小组名称')

    belong = models.ForeignKey(Course, verbose_name='本组所属课程')

    creator = models.ForeignKey(User, related_name='my_groups', verbose_name='组长')
    members = models.ManyToManyField(User, related_name='added_groups', verbose_name='组员')

    locked = models.BooleanField(default=False, verbose_name='锁定')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

    def is_creator(self, user):
        if self.creator is user:
            return True
        return False

    def in_group(self, user):
        print(user)
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
    author = models.ForeignKey(User, verbose_name='作者')
    article = models.ForeignKey('Article', verbose_name='所属文章')
    star = models.CharField(choices=STARS, max_length=1, verbose_name='评价星级')
    comment = models.TextField(verbose_name='评价内容')

    create_date = models.DateTimeField(default=now)

    def __str__(self):
        return 'to %r, %s' % (self.article.title, self.star)


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name='文章标题')
    content_md = models.TextField(null=True, verbose_name='文章内容')
    content_html = models.TextField(null=True)

    author = models.ForeignKey(User, related_name='article_set', verbose_name='文章作者')
    belong = models.ForeignKey(Course, related_name='article_set', null=True)

    create_date = models.DateTimeField(default=now)

    def add_comment(self, user, star, comment):
        self.comment_set.create(author=user, star=star, comment=comment)

    def __str__(self):
        return '<Article: %s by %r>' % (self.title, self.author)


class InviteCode(models.Model):
    code = models.CharField(max_length=10, verbose_name='邀请码')
    creator = models.ForeignKey(User, related_name='send_code_set', verbose_name='邀请人')
    invitee = models.ForeignKey(User, related_name='receive_code_set', verbose_name='受邀人')
    group = models.ForeignKey(CourseGroup, related_name='code_set', null=True)

    @staticmethod
    def generate(creator: User, invitee: User, group: CourseGroup):
        pool_of_chars = string.ascii_letters + string.digits
        random_code = lambda x, y: ''.join([random.choice(x) for i in range(y)])
        code = random_code(pool_of_chars, 10)
        InviteCode.objects.create(creator=creator, invitee=invitee, group=group, code=code)
        return code

    def check_code(self, invitee):
        return True if self.invitee == invitee else False
