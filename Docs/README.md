《翻转课堂》入坑Django
## 引言
大家好我是初学Django的菜鸟bllli，在知乎记录一下我通过完成创新项目《翻转课堂》网站来学习Django/Python的一些经历。

首先介绍一下项目背景，这个是我校的创新项目，按老师给的题目和需求来制作一个软件。很明显我拿到的项目就是翻转课堂了，全名叫《基于“创课”的高校翻转课堂教学平台》。

因为距离项目开始已经有一段时间了，让我从最开始部署环境、createapp啥的开始讲起是不可能的，
我想给大家分享的是我从拿到这个项目开始的思考，和对某些情况的处理办法。
代码都放在[我的Github](https://github.com/bllli/ReverseCourse)上。
我是初学者，会有一些处理的不太好的地方，还请各位朋友多多指点，谢谢！

书归正传，老师给出的东西画风是这样的

> 创课的内容与活动设计多围绕复杂的现实问题展开，鼓励学生结合兴趣组成项目小组，在指导教师团队的集体指导下开展协作探究。学生通过不断的动手设计、制作、修改与完善等，最终将创意变成现实的产品、方案与服务。培养了学生的协作学习能力和实践能力。

两个字，精辟！但仅靠这些外加脑补肯定弄不清楚项目的需求，瞎做一通不是老师想要的效果还得回炉重做。于是继续跟老师沟通。

## 要求
说实话我看到整理出这么多东西我头都大了，根本没见过这架势好伐？

右侧加粗的是我的内心os

- 一个网站 **没错，一个网站，B/S结构**
- 注册/登录/学生认证/教师认证 **注册、身份认证啥的不用急用django admin加几个小号就行了，先把登录做出来再说。**
- 学生能够自由结组 **小岳岳_我的天呐.jpg 这可咋整**
- 教师能够提交“课题”（课题页面中，教师能够发布多篇文章、资料） **这个好说，课题和文章是一对多关系，把属于同个课题的文档全查出来就行**
- 教师能够设定“课题”的某个阶段的截止日期 **停停停 脑壳痛 我先弄出前面的**
- 学生结组后，能够提交各个阶段的成果文章。
- 未提交的小组应收到（站内信/邮件）提示。
- 教师可以在课程后台界面看到各组提交成果状况，并进行评价/打分/要求修改。

说实话要是详细展开了研究，得研究好长时间，现在这个太缺细节。那咱们边写边分析吧。

## 数据库设计
常言道兵马未动粮草先行，咱们边设计数据库边去想怎么实现功能。


### 登录
托Django的福，登录不用咱忙活了，看文档直接用就ok[使用Django认证系统](http://python.usyiyi.cn/translate/django_182/topics/auth/default.html)

[我项目中登录登出的实现](https://github.com/bllli/ReverseCourse/commit/f84dcbb42f62d9e96ca9910ddeb51809c87ec394)
### 课程
很简单嘛！  
课程都有哪些属性？标题、课程介绍、作者(教师)  
教师与课程是一对多关系，一个教师可以申请多个课程，而一个课程只能由一名教师负责。一对多关系，在“多”的那边加个指向“一”的外键。  
教师可以向课程附加多篇文章，作为学习资料。

所以先弄文章的model: 文章应该有哪些属性？标题、作者、内容、创建日期。  
作者与文章，一对多关系，在文章里拉一条到User的外键；  
等一下，课程介绍也可以放到文章里面，统一管理。  
课程与(作为课程详情的)文章是一对一的，一个课程只能有一条详情，一条详情文章也只能属于一个课程，所以用了OneToOneField;  
课程与(教师提交的多条)文章是一对多的，一个课程可以有多条文章，在文章里拉一条到Course的外键。

(大家看到下面的content_md 和 content_html，我是想用户输入md格式文档，自动转换为html格式的，时间紧没来及弄)

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name='文章标题')
    content_md = models.TextField(null=True, verbose_name='文章内容')
    content_html = models.TextField(null=True)

    author = models.ForeignKey(User, related_name='article_set', verbose_name='文章作者')
    belong = models.ForeignKey(Course, related_name='article_set', null=True)

    create_date = models.DateTimeField(default=now)


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name='课程名称')

    create_date = models.DateTimeField(default=now)

    group_members_min = models.IntegerField(default=1, verbose_name='团队成员下限')
    group_members_max = models.IntegerField(default=20, verbose_name='团队成员上限')

    detail = models.OneToOneField('Article', null=True, blank=True, verbose_name='课程详情')
    author = models.ForeignKey(User, verbose_name='发布者(教师)')
```

使用 `a_course.detail` 获取课程的“详情文章”对象  
使用 `a_course.article_set.all()`  获取课程的“学习资料文章”对象列表

### 学生自由组建学生团队
让学生团队属于某个课程，这样的话就不需要考虑一个小组对应多个课程的引发的各种麻烦事，比如不同课程允许的团队成员人数上限不同。  

学生团队有啥属性？团队名、所属课程、队长、队员。

用户(队长)与团队是一对多关系，一个用户可以成为多个团队的队长。在团队里添加队长外键；  
所属课程也是一对多；  
队员与团队之间的关系是多对多，一个用户可以参加多个团队，一个团队也可以有多个队员用户。使用ManyToManyField

学生团队应该允许成员主动退出队伍吗？
课程正式开始前应该允许自由进入退出，但课程进行中就不应该允许了。
于是设一个locked标记，默认为False，课程开始后想个办法把它设为True，当它为True时禁止退出队伍。
```python
class CourseGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name='小组名称')

    belong = models.ForeignKey(Course, verbose_name='本组所属课程')

    creator = models.ForeignKey(User, related_name='my_groups', verbose_name='组长')
    members = models.ManyToManyField(User, related_name='added_groups', verbose_name='组员')

    locked = models.BooleanField(default=False, verbose_name='锁定')
```

到现在，课程、文章、团队model都建好了

![ER图](https://github.com/bllli/ReverseCourse/blob/new/Docs/ER.png?raw=true)

## 功能实现
### 课程展示
增删改查，咱们先做查。"增删改"先交给Django Admin。

展示的话分两部分，课程列表和课程详情。
#### 课程列表
[课程列表及分页的实现](https://github.com/bllli/ReverseCourse/commit/66595b8fb65918ab08b1dd2bfcc98f3e9d8511f1)
#### 课程详情
[课程详情的实现](https://github.com/bllli/ReverseCourse/commit/de84ef12bf868e4799f55ba6ad7da0582a291cc0)

### 自由组队
想了想，组建流程大概是这样滴  
![学生团队组建流程图](https://github.com/bllli/ReverseCourse/blob/new/Docs/%E5%AD%A6%E7%94%9F%E5%9B%A2%E9%98%9F%E7%BB%84%E5%BB%BA%E6%B5%81%E7%A8%8B.png?raw=true)

# 今天先唠到这儿
[项目托管地址 https://github.com/bllli/ReverseCourse](https://github.com/bllli/ReverseCourse)

欢迎前来指导!

# 第二篇
大家好我是bllli，这是“揣着Django做项目”的第二篇文章。

第一篇在这儿 [揣着Django做项目](https://zhuanlan.zhihu.com/p/31346209)

上次说到了组队流程，其实上一篇文章发表时我已经实现了一部分，发现自己果然图样，在没规划好需求的情况下胡写一通。
这就暴露没计划就写代码的缺点了：维护性太差，而且根本就没考虑到以后的功能要怎么实现。

所以我就不写我有缺陷的实现了，直接说现在更优雅一些的想法与实现。

## 从组队功能说起
上次已经放过组队的时序图了，再放一遍

![学生团队组建流程](https://raw.githubusercontent.com/bllli/ReverseCourse/new/Docs/%E5%AD%A6%E7%94%9F%E5%9B%A2%E9%98%9F%E7%BB%84%E5%BB%BA%E6%97%B6%E5%BA%8F.png)
上述组队时序图包括了创建队伍、队长邀请，其他用户向队长发送加入团队的申请  
划重点 邀请和申请。

来看看怎么实现。具体分这几步：创建队伍、队伍详情展示、请求(邀请/申请)记录的生成、站内信发送、请求记录的处理。

#### 创建团队
在课程详情页面创建队伍，申请创建部分可以使用表单提交。

```python
def course_detail(request, course_id):
    c = get_object_or_404(Course, pk=course_id)
    return render(request, 'course_detail.html', {
        'course': c,
        'course_article': c.article_set.exclude(status=Status.CREATING).all(),
        'in_group': request.user.added_groups.filter(belong=c).first() if request.user.is_authenticated() else None,
        'groups': c.coursegroup_set.all(),
    })
```
这是课程详情的view，要展示课程详情(course)、展示属于课程的文章(course_article)、确认当前用户加入的本课程的团队(in_group)、还要展示属于课程的所有团队(groups)

模板里面该取属性的取属性，该遍历的遍历
```
{% if in_group %}
    你已加入<a href="{% url 'group_detail' in_group.id %}"><div class="ui green button">{{ in_group.name }}</div></a>
{% else %}
    <div class="ui buttons">
    <a href="{% url 'create_group' course.id %}"><button class="ui positive button">创建团队</button></a>
    <div class="or" data-text="或"></div>
    <a href="{% url 'groups' %}?course={{ course.id }}"><button class="ui primary button">加入团队</button></a>
    </div>
{% endif %}
```
用户已经加入本课程其他团队的情况下，直接展示已加入的团队；否则展示创建团队和加入团队两个按钮。

![此处应有两个按钮的课程详情](https://raw.githubusercontent.com/bllli/ReverseCourse/new/Docs/blog_img/%E8%AF%BE%E7%A8%8B%E8%AF%A6%E6%83%85.png)

点击"加入团队"跳转到本课程的团队列表，用户可以在该列表里发起申请。这个我先挖个坑，稍后再说。  
点击"创建团队"跳转到团队创建页面。
```python
from django import forms
class CreateGroupForm(forms.Form):
    name = forms.CharField(label='团队名', max_length=20)
```
这是很寒酸的表单
```python
@login_required
def create_group(request, course_id):
    form = CreateGroupForm(request.POST or None)
    c = get_object_or_404(Course, pk=course_id)
    if request.user.added_groups.filter(belong=c).first():
        raise Http404('别瞎试了, 你已经加入一个团队了')
    if request.POST and form.is_valid():
        name = form.cleaned_data.get('name', None)
        if not CourseGroup.objects.filter(name=name).all():
            new_group = request.user.my_groups.create(name=name, belong=c)
            new_group.members.add(request.user)
            new_group.save()
            return redirect('group_detail', new_group.pk)
        messages.warning(request, '这个名字已经有人捷足先登了，换一个试试吧')
    return render(request, 'group_create.html', {'course': c})
```
这是创建团队的view，先把没登录的、课程id填错的(点“创建团队”按钮不会报错，用户瞎改url才会报错)、
已经加了别的小队还想来凑热闹的统统过滤掉。

点了“创建团队”，浏览器跟着创建团队的url，按GET方法访问，给用户个页面还有表单，先看看。  

![此处应有创建团队图](https://raw.githubusercontent.com/bllli/ReverseCourse/new/Docs/blog_img/%E5%88%9B%E5%BB%BA%E5%9B%A2%E9%98%9F%E9%A1%B5%E9%9D%A2.png)

用户填好了表单，点了提交，浏览器按POST发到该url
```
{% extends 'base.html' %}
{% block title %}创建团队 - 翻转课堂{% endblock %}
{% block container %}
    <div class="ui text container">
        <div class="ui large header">创建团队 - 课题: {{ course.title }}</div>
        <form class="ui large form" method="post">
            {% csrf_token %}
            <div class="ui stacked segment">
                <div class="field">
                    <p>为你的团队起一个霸气的名字吧</p>
                    <div class="ui input"><input name="name" placeholder="" type="text"></div>
                </div>
                <div class="ui fluid large teal submit button">提交</div>
            </div>
        </form>
    </div>
{% endblock %}
```
这是创建团队的模板group_create.html 注意form标签里要加method="post"，不然点击提交会按照get提交，跟view对不上； form内要加{% csrf_token %}，不然过不了csrf保护。

这样就完成了团队的创建。

#### 团队详情页的设计
队长小强邀请小明加入队伍，需要告诉后台那些数据？

- 谁发出的？当前登录用户小强 request.uesr
- 邀请的谁？小明呗
- 邀请到那儿？...小强的团队？可是小强可以是好几个团队的队长。

团队详情页面要展示团队的信息、队长是谁、队员都有谁、队长的还能看到能邀请谁并发出邀请操作。

![展示一个巨大的流程图](https://raw.githubusercontent.com/bllli/ReverseCourse/new/Docs/%E6%B5%81%E7%A8%8B%E5%9B%BE/%E7%94%A8%E6%88%B7%E8%AE%BF%E9%97%AE%E5%9B%A2%E9%98%9F%E9%A1%B5%E9%9D%A2%E6%B5%81%E7%A8%8B%E5%9B%BE.png)

图片很大，会被知乎压缩到看不清，[点击看原图](https://raw.githubusercontent.com/bllli/ReverseCourse/new/Docs/%E6%B5%81%E7%A8%8B%E5%9B%BE/%E7%94%A8%E6%88%B7%E8%AE%BF%E9%97%AE%E5%9B%A2%E9%98%9F%E9%A1%B5%E9%9D%A2%E6%B5%81%E7%A8%8B%E5%9B%BE.png)

```python
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
```

这是团队详情的Model，提供了几个确认团队状态的函数。

```python
def group_detail(request, group_id):
    group = get_object_or_404(CourseGroup, pk=group_id)
    params = {}
    if request.user.is_authenticated():
        if request.user == group.creator and group.can_invite_user():
            params['can_invite'] = True
            params['users'] = User.objects.exclude(added_groups__belong_id=group.belong_id).all()
        if group.can_join_group(request.user):
            params['can_join'] = True
        elif group.can_leave_group(request.user):
            params['can_quit'] = True
    params['group'] = group
    return render(request, 'group_detail.html', params)
```

团队详情view，未登录用户只能看到团队的一些信息，已登录的用户可以根据Model提供的函数判断该展示什么。

```html
{% if can_invite %}{# 如果能够发起邀请 #}
    <h3 class="ui header">邀请加入队伍</h3>
    <div class="ui divider"></div>
    {% if not users %}<h4 class="ui header">暂无可加入成员</h4>{% endif %}
    <div class="ui middle aligned divided list">
    {% for member in users %}
        <div class="item">
            <div class="right floated content">
                {% if not group|add_arg:member|call:"already_invite" %}{# 未被邀请 #}
                    <a href="{% url 'invite_into_group' group.pk member.pk %}"><div class="ui green button">邀请</div></a>
                {% else %}
                    <div class="ui disabled button">已邀请</div>
                {% endif %}
            </div>
            <img class="ui avatar image" src="/static/images/logo.png"/>
            <div class="content">{{ member.username }}</div>
        </div>
    {% endfor %}
    </div>
{% endif %}
```

团队详情模板。限于篇幅，只展示上面一段。

`{% if not group|add_arg:member|call:"already_invite" %}{# 未被邀请 #}`这是在模板中调用带参数的函数，详见[这篇文章](https://zhuanlan.zhihu.com/p/31450795)

其中`<a href="{% url 'invite_into_group' group.pk member.pk %}"><div class="ui green button">邀请</div></a>`

这就是邀请按钮了 group团队对象就是当前打开详情页的团队对象，“可邀请的用户列表”中遍历每个member。加上当前登录用户的隐含条件，就能够告诉后端：从request.user发出的、邀请member用户进入group团队

![展示团队详情,注意特别要展示已邀请/邀请按钮](https://raw.githubusercontent.com/bllli/ReverseCourse/new/Docs/blog_img/%E5%9B%A2%E9%98%9F%E8%AF%A6%E6%83%85%E9%A1%B5%E9%9D%A2.png)

#### 邀请操作
```python
@login_required
def invite_into_group(request, group_id, invitees_id):
    invitees = get_object_or_404(User, pk=invitees_id)
    group = get_object_or_404(CourseGroup, pk=group_id)
    if group.creator != request.user and group.can_join_group(invitees):  # 只有队长才能邀请其他人
        messages.error(request, '邀请失败， 可能你邀请的人已经在同课程中别的群里了。')
    else:
        if group.already_invite(invitees):
            messages.success(request, '已经邀请过{invitees}，请不要发送多条邀请。'.format(invitees=invitees))
        else:
            invite_code = Invite.generate(creator=request.user, invitee=invitees,
                                          group=group, choice=Invite.INVITE_USER_JOIN_GROUP)
            notify.send(request.user, recipient=invitees,
                        verb='邀请你加入<a href="/groups/{g_id}/" target="_blank">{group}</a>'
                        .format(group=group.name, g_id=group.pk),
                        target=group,
                        description=invite_code)
            messages.success(request, '邀请{invitees}成功!'.format(invitees=invitees))
    return redirect('group_detail', group.pk)
```

邀请操作的view，接受团队id、受邀人id。先过滤，把传入团队id、受邀人id有错误的干掉；
把假装自己是队长的、受邀人不能接受邀请的干掉；把已经发送过邀请的干掉。

(鬼知道用户会传入什么参数，用户传进来的一律不信任，过滤的干干净净才能让请求影响数据库)

然后就新建请求(邀请)记录对象、并发送请求记录给受邀人。

啥请求记录？咋发送？接着看。

#### 请求(邀请/申请)记录Model
邀请/申请的本质就是**发起人**让**审核人**干啥事，**审核人**查看信息选择同意或者不同意。  

统计一下需要执行邀请/申请的的操作

|发起人(actor)|审核人(target)|干啥(verb)|去哪儿(action_onject)|
|---|---|---|---|
|用户(团队队长)|其他用户|邀请(其他用户)进入|XX小队|
|用户(团队成员)|向用户(团队队长)|申请加入|XX小队|
|用户(团队成员)|向用户(团队队长)|申请退出|XX小队|
|用户(课程负责教师)|其他用户(教师)|邀请(教师)进入|XX课程教师团队|

```python
from django.db import models
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
    choice = models.IntegerField(choices=TYPE, default=INVITE_USER_JOIN_GROUP)
    # 确认邀请对象类型 if a_invite.choice is Invite.APPLY_QUIT_GROUP:    
    # 确认邀请对象是申请的一种 if a_invite.choice in Invite.APPLY:    
    code = models.CharField(max_length=10, verbose_name='邀请码')
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
        """判断使用该邀请码的用户是否有权限"""
        return True if (self.choice is Invite.INVITE_USER_JOIN_GROUP and user == self.invitee) or \
                       (self.choice in Invite.APPLY and user == self.group.creator) or \
                       (self.choice is Invite.INVITE_TEACHER_JOIN_COURSE and user == self.course.author) else False
```

请求Model，专门保存邀请/申请信息。  
Model里添加一个“类型”IntegerField字段(避免占用type，我就很民科的起名为了chioce，大家不要学我)，用choice参数描述请求的类型。  
因为邀请可能会邀请加入团队，也有可能加入课程，所以为课程和团队都添加了一条外键，用于存储“如果是邀请的话，邀请到哪里”。  
code字段用户存储随机生成的邀请码  
creator为发起人(发送邀请/申请)，invitee为受邀人(收到邀请)/审核人(收到申请)

check_code方法用来验证访问这条请求记录的用户到底有没有权限。
根据设计，邀请只能由受邀请人点击确认，申请只能由队长/教师点击确认。  
这样我们就加了一个验证，干掉没通过验证的访问就行了。

静态方法generate负责生成一个请求对象，并随机出一个字符串。(其实用自增的主键更好，不会出现重复)


#### 站内信
站内信，就是一个用户可以向其他用户发送消息，请求(邀请/申请)信息都以站内信的形式发送。

没啥思路，我先搜搜。搜到一篇 [django-notifications](https://github.com/django-notifications/django-notifications)  

人家README里有一句

> For example: justquick (actor) closed (verb) issue 2 (action_object) on activity-stream (target) 12 hours ago

发起人 干了啥动作 操作了哪个东西 针对啥 什么时候干的  
队长 邀请了 (操作团队对象) 受邀请的用户 

哎呀这就是我想要的！赶紧pip install

（安装和配置django-notifications可以在README找到，在此不赘述。）

收件箱的已读/未读
```python
@login_required
def inbox(request):
    queryset = request.user.notifications
    return render(request, 'inbox.html', {'notifications': queryset})
```

组队邀请的发送(前面邀请操作有详细的)
```python
@login_required
def invite_into_group(request, group_id, invitees_id):
    ...  # 一系列的判定 确认用户可以邀请受邀人
    notify.send(request.user, recipient=invitees,
                        verb='邀请你加入<a href="/groups/{g_id}/" target="_blank">{group}</a>'
                        .format(group=group.name, g_id=group.pk),
                        target=group, 
                        description=invite_code)
    ...  # 告诉用户你邀请成功了
```

模板foreach一下，展示收到的站内信
```html
{% for un in notifications.unread %}
    {% if un.target %}
        <div class="item">
            <div class="right floated content">
                <div class="ui buttons">
                    <a href="{% url 'notifications:mark_as_read' un.slug %}?next={% url 'inbox' %}">
                        <button class="ui button">已读</button>
                    </a>
                    <div class="or" data-text="或"></div>
                    <a href="{% url 'accept_invite' un.description %}">
                        <button class="ui positive button">接受</button>
                    </a>
                    <div class="or" data-text="或"></div>
                    <a href="{% url 'refuse_invite' un.description %}">
                        <button class="ui primary button">拒绝</button>
                    </a>
                </div>
            </div>
            <div class="content"><i class="mail icon"></i>
                <a href="{% url 'user_detail' un.actor %}" target="_blank">{{ un.actor }}</a>
                {{ un.verb | safe }}({{ un.timesince }} 前)
            </div>
        </div>
{% for un in notifications.read %}
...
```

可以用 {{ un.verb | safe }} 渲染，展示html<a>标签链接

我用站内信的target参数是否有值来确定是不是请求信息，没有的话就是普通的站内信，不展示接受/拒绝按钮。

(有些功能如申请/邀请的区分用django-notifition的话实现到是能实现，但是看的不爽，就让django-notification专心做站内信吧。)

![展示收件箱，接受/拒绝按钮](https://raw.githubusercontent.com/bllli/ReverseCourse/new/Docs/blog_img/%E6%94%B6%E4%BB%B6%E7%AE%B1.png)

#### 接受/拒绝

```python
@login_required
def accept_invite(request, str_code: str):
    code = get_object_or_404(Invite, code=str_code)
    notification = get_object_or_404(Notification, recipient=request.user, description=str_code)
    if code.check_code(request.user):
        notification.mark_as_read()
        if code.choice is Invite.INVITE_USER_JOIN_GROUP:
            if not code.group.can_join_group(request.user):  # 能加进去
                messages.success(request, '加入失败，团队成员已满或你已经加入了本课题下的另一个团队')
            else:
                code.group.join(request.user)
                messages.success(request, '已加入{group_name}, 祝学习愉快!'.format(group_name=code.group.name))
                return redirect('group_detail', code.group.pk)
        elif code.choice in Invite.APPLY:  # 申请类型code
            if code.choice is Invite.APPLY_QUIT_GROUP:
                code.group.leave(code.creator)
                messages.success(request, '你已同意{user}退出{group}'.format(user=code.creator, group=code.group))
            elif code.choice is Invite.APPLY_JOIN_GROUP:
                code.group.join(code.creator)
                messages.success(request, '你已同意{user}加入{group}'.format(user=code.creator, group=code.group))
        return redirect('inbox')
    raise Http404('别捣乱')
```

点了接受按钮，带着随机生成的邀请码访问这个accept view。仍然是一系列判断验证操作真实，通过验证才能执行进一步操作。

这个view处理所有点了接受的情况，所以可以看到根据请求(邀请/申请)对象类型的不同，来执行不同的操作。

至于“加入团队”申请操作，留个坑下次接着讲。

#### PS
大家在知乎上的点赞给了我莫大的鼓励。第二篇写了很久，我尽量用我能最好的文字把学习成果展示给大家。
如果朋友们觉得什么地方说的模糊难以理解，或是有什么bug，请在文章下留言/发个issue/私信指点我一下，谢谢∩_∩

GitHub: [https://github.com/bllli/ReverseCourse](https://github.com/bllli/ReverseCourse)

# 第三篇(未完成)
出现这种情况我也很无奈啊

而且现有的文章Model也无法实现“教师发布一篇更新文章, 团队提交阶段成果并由教师评分”
也就是下面三个要求

- 教师能够提交“课题”（课题页面中，教师能够发布多篇文章、资料）
- 教师能够设定“课题”的某个阶段的截止日期 
- 学生结组后，能够提交各个阶段的成果文章。
