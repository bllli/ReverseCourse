# ReverseCourse 翻转课堂

翻转课堂, 用项目驱动的方式引导学生进行学习.

孩子咳嗽老不好?多半是不想上补习班装的! ~~打一顿~~ 还不赶紧换个孩子喜欢的上课模式!

## 技术栈
Django

## 功能
- 小组
  - [x] 学生自由结组

- 课题
  - [ ] 教师提交课题
  - [ ] 小组确认开始课题

- 文章(成果)
  - [ ] 小组提交 阶段成果
  - [ ] 小组提交 最终成果及展示图文
  - [ ] 教师评价打分

- 数据展示
  - [ ] 课题中各小组评分汇总

## 安装

### Python3.6

推荐使用[Anaconda](https://conda.io/docs/user-guide/install/index.html)

conda env安装Python3.6

创建 `conda create -n myenv python=3.6`  
激活
> On Windows, in your Anaconda Prompt, run `activate myenv`  
> On macOS and Linux, in your Terminal Window, run `source activate myenv`

退出
> On Windows, in your Anaconda Prompt, run `deactivate`  
> On macOS and Linux, in your Terminal Window, run `source deactivate`

[官方教程在此](https://conda.io/docs/user-guide/tasks/manage-environments.html)

### 包
已激活conda env后(或者是Python3.6)
`pip install -r requirements.txt`

### 部署
`python manage.py migrate`

`python manage.py createsuperuser`

### 运行

`python manage.py runserver`
