import string
import random

from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class Status:
    """描述状态

    此中的状态描述词均为抽象，如FINISHED 既可以为整件事情的结束（课程结束）亦可为某个状态的结束（团队组建完成）
    """
    CREATING = 1  # 创建中，还是草稿，尚未发布。仅创建者可以查看到。
    HOLDING = 2  # 已创建完成，等待其他操作。已公布，谁都能看到。
    STARTED = 3  # 已开始。
    SUBMITTED = 3  # 已提交。 STARTED 与 SUBMITTED 可混用
    FINISHED = 4  # 已结束。此时应拒绝非管理员的修改操作。
    REJECTED = 5  # 被驳回，需要修改后重新发起请求
    ACCEPTED = 6  # 被接收
    LOCKED = 7  # 已锁定


class User(AbstractUser):
    STUDENT = 1
    TEACHER = 2
    user_type = models.SmallIntegerField(choices=(
        (STUDENT, '学生'),
        (TEACHER, '教师'),
    ), default=STUDENT, verbose_name='用户类型')

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'


class Course(models.Model):
    """课程Model"""
    STATUS = (
        (Status.CREATING, '未提交'),  # 课程尚未提交。除提交教师本人外不可查看
        (Status.HOLDING, '待开始'),  # 课程已提交，但尚未开始。学生此时组队
        (Status.STARTED, '进行中'),  # 课程已经开启。
        (Status.FINISHED, '已结束'),  # 课程已经结束。统计，出结果、出成绩
    )
    title = models.CharField(max_length=200, verbose_name='课程名称')

    status = models.SmallIntegerField(choices=STATUS, default=Status.CREATING, verbose_name='课程状态')

    create_date = models.DateTimeField(default=now)
    start_date = models.DateTimeField(default=None, null=True, blank=True, verbose_name='课程开始时间')
    finish_date = models.DateTimeField(default=None, null=True, blank=True, verbose_name='课程结束时间')

    group_members_min = models.IntegerField(default=1, verbose_name='团队成员下限')
    group_members_max = models.IntegerField(default=20, verbose_name='团队成员上限')

    detail = models.TextField(null=True, default=None, blank=True, verbose_name='课程详情')
    author = models.ForeignKey(User, verbose_name='发布者(教师)')

    def __str__(self):
        return '课程: %s' % self.title

    def __repr__(self):
        return '<Course: %s by %s>' % (self.title, self.author)

    class Meta:
        ordering = ('create_date',)

    @staticmethod
    def get_public_course_queryset() -> QuerySet:
        return Course.objects.exclude(status=Status.CREATING)


class CourseGroup(models.Model):
    """团队Model"""
    STATUS = (
        (Status.CREATING, '创建中'),  # 团队创建中
        (Status.FINISHED, '已完成'),  # 团队组建完成，拒绝其他用户申请加入
        (Status.LOCKED, '已锁定'),  # 课程开始后禁止修改成员
    )
    name = models.CharField(max_length=100, verbose_name='小组名称')

    status = models.SmallIntegerField(choices=STATUS, default=Status.CREATING, verbose_name='团队状态')

    belong = models.ForeignKey(Course, verbose_name='本组所属课程')

    creator = models.ForeignKey(User, related_name='my_groups', verbose_name='组长')
    members = models.ManyToManyField(User, related_name='added_groups', verbose_name='组员')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

    def is_creator(self, user: User) -> bool:
        return True if self.creator == user else False

    def in_group(self, user: User) -> bool:
        return user in self.members.all() or user is self.creator

    def join(self, user: User):
        self.members.add(user)

    def leave(self, user: User):
        if self.in_group(user):
            self.members.remove(user)

    def can_join_group(self, user: User) -> bool:
        """确定指定用户能否加入团队"""
        return True if self.status is Status.CREATING and \
                       self.members.count() < self.belong.group_members_max and \
                       user in User.objects.exclude(added_groups__belong=self.belong).all() else False

    def can_leave_group(self, user: User) -> bool:
        """确定指定用户能否退出团队"""
        return True if user in self.members.all() and \
                       self.status is not Status.LOCKED else False

    def can_invite_user(self) -> bool:
        """队长是否可以邀请别人"""
        return True if self.status is not Status.LOCKED and \
                       self.members.count() < self.belong.group_members_max else False

    def already_invite(self, user: User) -> bool:
        """已经发送过邀请"""
        return True if user.notifications.filter(target_object_id=self.pk).unread() else False


class CourseArticle(models.Model):
    """课程文章Model

    由教师/教学辅导人员提供，属于某个课程
    """
    STATUS = (
        (Status.CREATING, '创建中'),  # 由 教师/教辅人员 创建课程文章，未提交
        (Status.SUBMITTED, '已发布'),  # 已发布
    )
    title = models.CharField(max_length=200, verbose_name='文章标题')
    content = models.TextField(verbose_name='文章内容')
    author = models.ForeignKey(User, related_name='article_set', verbose_name='文章作者')
    belong = models.ForeignKey(Course, related_name='article_set', null=True, verbose_name='所属课程')

    status = models.SmallIntegerField(choices=STATUS, default=Status.CREATING, verbose_name='文章状态')

    is_task_article = models.BooleanField(default=False, verbose_name='任务文章')
    deadline = models.DateTimeField(null=True, default=None, blank=True, verbose_name='学生上交截止时间')
    create_date = models.DateTimeField(default=now, verbose_name='创建时间')

    def __str__(self):
        return '<CourseArticle: %s by %r>' % (self.title, self.author)


class GroupArticle(models.Model):
    """团队文章Model

    由学生团队提交的学习成果文章，对应教师的任务文章
    """
    STATUS = (
        (Status.CREATING, '创建中'),  # 尚未提交
        (Status.SUBMITTED, '已提交'),  # 已经提交，等待教师审核/驳回修改
        (Status.FINISHED, '已审完'),  # 老师评分完成
        (Status.REJECTED, '被驳回'),  # 根据老师的提示继续修改回答
    )
    content = models.TextField(verbose_name='文章内容')

    status = models.SmallIntegerField(choices=STATUS, default=Status.CREATING, verbose_name='文章状态')

    # 评分总计
    score = models.DecimalField(decimal_places=2, max_digits=5, default=100.0)
    scoring_people = models.IntegerField(default=0)

    group = models.ForeignKey(CourseGroup, related_name='group_article_set')
    belong = models.ForeignKey(CourseArticle, related_name='group_article_set')

    create_date = models.DateTimeField(default=now, verbose_name='创建时间')
    submit_date = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')

    def __str__(self):
        return '<GroupArticle: %s by %r>' % (self.belong.title, self.group.name)

    @staticmethod
    def get_submitted_group_article() -> QuerySet:
        """获取已提交的团队文章

        Usage:
            queryset = get_submitted_group_article()
            article_set_for_a_group = queryset.filter(group=a_group).all()
            article_set_for_a_course = queryset.filter(course=a_course).all()
        """
        return GroupArticle.objects.filter(status=Status.SUBMITTED)

    def submit_article(self):
        self.status = Status.SUBMITTED
        self.submit_date = now()


class Evaluation(models.Model):
    """评价Model

    教师/教辅人员对学生提交的文章进行评价
    """
    author = models.ForeignKey(User, verbose_name='作者')
    article = models.ForeignKey('GroupArticle', verbose_name='评价的文章')

    comment = models.TextField(verbose_name='评价内容')
    # 是否为最终评价
    final = models.BooleanField(default=False)
    score = models.IntegerField(verbose_name='分数')

    delete = models.BooleanField(default=False)

    create_date = models.DateTimeField(default=now)

    def __str__(self):
        return '<Evaluation: for %s by %s>' % (self.article, self.author)


class Invite(models.Model):
    INVITE_USER_JOIN_GROUP = 1  # (团队队长)邀请(教师)加入团队
    INVITE_TEACHER_JOIN_COURSE = 2  # (课程负责人)邀请(其他教师)加入课程
    APPLY_JOIN_GROUP = 3  # (普通用户)向(团队队长)申请加入团队
    APPLY_QUIT_GROUP = 4  # (普通用户)向(团队队长)申请退出团队
    INVITE = (INVITE_USER_JOIN_GROUP, INVITE_TEACHER_JOIN_COURSE)  # 邀请
    APPLY = (APPLY_QUIT_GROUP, APPLY_JOIN_GROUP)  # 申请
    TYPE = (
        (INVITE_USER_JOIN_GROUP, '邀请加入团队'),
        (INVITE_TEACHER_JOIN_COURSE, '邀请管理课程'),
        (APPLY_JOIN_GROUP, '申请加入团队'),
        (APPLY_QUIT_GROUP, '申请退出团队'),
    )
    STATUS = (
        (Status.SUBMITTED, '已发出'),
        (Status.ACCEPTED, '已接受'),
        (Status.REJECTED, '已拒绝'),
    )
    code = models.CharField(max_length=10, verbose_name='邀请码')
    choice = models.IntegerField(choices=TYPE, default=INVITE_USER_JOIN_GROUP)
    creator = models.ForeignKey(User, related_name='send_code_set', verbose_name='邀请人')
    invitee = models.ForeignKey(User, related_name='receive_code_set', verbose_name='受邀人')
    course = models.ForeignKey(Course, related_name='code_set', null=True)
    group = models.ForeignKey(CourseGroup, related_name='code_set', null=True)

    @staticmethod
    def generate(creator: User, invitee: User, choice: int, group: CourseGroup = None, course: Course = None):
        pool_of_chars = string.ascii_letters + string.digits
        random_code = lambda x, y: ''.join([random.choice(x) for i in range(y)])
        code = random_code(pool_of_chars, 10)
        Invite.objects.create(creator=creator, invitee=invitee,
                              group=group, code=code, choice=choice, course=course)
        return code

    def check_code(self, user: User) -> bool:
        """判断使用该邀请码的用户是否有权限

        :argument user: 使用者
        """
        return True if (self.choice is Invite.INVITE_USER_JOIN_GROUP and user == self.invitee) or \
                       (self.choice in Invite.APPLY and user == self.group.creator) or \
                       (self.choice is Invite.INVITE_TEACHER_JOIN_COURSE and user == self.course.author) else False
