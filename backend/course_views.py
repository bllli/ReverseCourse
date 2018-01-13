from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404

from backend.models import Course, Status


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
    return render(request, 'course_detail.html', {
        'course': c,
        'course_article': c.article_set.exclude(status=Status.CREATING).all(),
        'in_group': request.user.added_groups.filter(belong=c).first() if request.user.is_authenticated() else None,
        'groups': c.coursegroup_set.all(),
    })
