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