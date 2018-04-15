# -*- coding:utf-8 -*-

"""描述状态

此中的状态描述词均为抽象，如FINISHED 既可以为整件事情的结束（课程结束）亦可为某个状态的结束（团队组建完成）
"""
# 课程
COURSE_CREATING = 0x01  # 课程创建中。还是草稿，尚未发布。仅创建者可以查看到。
COURSE_HOLDING = 0x02   # 已创建完成，公布给指定班级。允许学生在本课程中自由结组。
COURSE_STARTED = 0x04   # 已开始。此时分组不可变更，未组队的学生将自动结组。
COURSE_FINISHED = 0x08  # 已结束。此时应拒绝非管理员的修改操作。

INVITE_SUBMITTED = 0x01  #
INVITE_REJECTED = 0x40   # 被驳回，需要修改后重新发起请求
INVITE_ACCEPTED = 0x80   # 被接收

COURSE_STATUS_CHOICES = (
    (COURSE_CREATING, '未提交'),  # 课程尚未提交。除提交教师本人外不可查看
    (COURSE_HOLDING, '待开始'),  # 课程已提交，但尚未开始。学生此时组队
    (COURSE_STARTED, '进行中'),  # 课程已经开启。
    (COURSE_FINISHED, '已结束'),  # 课程已经结束。统计，出结果、出成绩
)
