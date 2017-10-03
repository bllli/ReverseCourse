from django.test import TestCase

from django.contrib.auth.models import User
from backend.models import Course, Article


class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User(username='bllli', is_superuser=True)
        self.user2 = User(username='二狗子')
        self.user3 = User(username='三毛')
        self.user4 = User(username='四攻爹')
        self.teacher = User(username='老师吼')
        self.user.save()
        self.user2.save()
        self.user3.save()
        self.user4.save()
        self.teacher.save()
        self.article = Article(title='走位、消耗及补兵', content_md='# 写在前面\n没啥好说的了', author=self.teacher)
        self.article.save()
        self.course = self.teacher.course_set.create(detail=self.article)
        self.course.save()
        self.cg = self.course.coursegroup_set.create(name='飞龙在天兴趣小组', creator=self.user)
        self.cg.members.add(self.user2, self.user3)
        self.cg.save()
        self.article_g = self.cg.creator.article_set.create(title='飞龙在天组对MOBA类游戏中走位、消耗、补兵的研究成果',
                                                            content_md='# 一 前言\n## 1.1 各大MOBA游戏机理剖析...')
        self.article_g.save()
        self.article_g.add_comment(self.teacher, '3', '一个简短的评论语')
        self.cg.save()

    def test_models(self):
        self.assertEqual(self.course.author, self.teacher)
        self.assertTrue(self.course in self.teacher.course_set.all())
        print(self.teacher.course_set.all())
        self.assertTrue(self.cg.belong is self.course)

        self.assertTrue('补兵' in self.course.detail.title)

        self.assertTrue(self.cg.in_group(self.user))
        self.assertTrue(self.cg.is_creator(self.user))
        self.assertTrue(self.cg.in_group(self.user2))
        self.assertTrue(self.cg.in_group(self.user3))
        self.assertFalse(self.cg.in_group(self.user4))
        self.cg.join(self.user4)
        self.assertTrue(self.cg.in_group(self.user4))
        self.cg.leave(self.user2)
        self.assertFalse(self.cg.in_group(self.user2))

        self.cg.disband()
        print(self.course.coursegroup_set.all())
