from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from backend.forms import TaskForm
from backend.models import Course, Status, CourseArticle, User, GroupArticle, CourseGroup


def courses(request):
    queryset = Course.objects.exclude(status=Status.CREATING)
    query = request.GET.get('query') or None
    if query:
        queryset = queryset.filter(title__contains=query)
    p = Paginator(queryset, 5)
    page = request.GET.get('page') or 1
    try:
        course_list = p.page(page)
    except PageNotAnInteger:
        course_list = p.page(1)
    except EmptyPage:
        course_list = p.page(p.num_pages)
    return render(request, 'courses.html', {
        'p': course_list,
        'query': query,
    })


def course_detail(request, course_id):
    c = get_object_or_404(Course, pk=course_id)
    from collections import namedtuple
    CATuple = namedtuple('CATuple', ['id', 'title', 'content', 'is_task_article', 'uploaded_this_task'])
    group_for_current_user = request.user.added_groups.filter(belong=c).first() if request.user.is_authenticated() else None
    # group_for_current_user: CourseGroup or None
    return render(request, 'course_detail.html', {
        'course': c,
        'course_article': [CATuple(
            ca.id,
            ca.title,
            ca.content,
            ca.is_task_article,
            group_for_current_user.group_article_set.filter(belong=ca).exists() if group_for_current_user else None
        ) for ca in c.article_set.exclude(status=Status.CREATING).all()],
        'in_group': group_for_current_user,
        'groups': c.coursegroup_set.all(),
        'is_author_teacher': c.author == request.user
    })


def task_list(request, task_id):
    task = get_object_or_404(CourseArticle, pk=task_id)
    user_group, user_answer = None, None
    if request.method == 'POST' and request.user.is_authenticated():
        form = TaskForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data['content'])
            return HttpResponseRedirect(reverse('course:task_list', args=[task_id]))
    if request.user.is_authenticated():
        # request.user: User
        user_group = request.user.added_groups.filter(belong=task.belong).first()
        # user_group: CourseGroup
        user_answer = user_group.group_article_set.filter(belong=task).first()
        other_answer = task.group_article_set.exclude(group=user_group).all()
    else:
        other_answer = task.group_article_set.all()

    return render(request, 'group_article_list.html', {
        'course': task.belong,
        'task': task,
        'user_group': user_group,
        'user_answer': user_answer,
        'show_form': True,
        'form': TaskForm(),
        'other_answer': other_answer,
    })


def task_detail(request, task_id):
    task = get_object_or_404(CourseArticle, pk=task_id)

