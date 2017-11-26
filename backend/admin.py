from django.db import models
from django.contrib import admin
from django.contrib.auth.models import Group
from pagedown.widgets import AdminPagedownWidget


from .models import Course, CourseGroup, GroupArticle, CourseArticle, Evaluation


class SaveModelMixin:
    def save_model(self, request, obj, form, change):
        try:
            obj.author
        except:
            obj.author = request.user
        obj.save()


class PageDownOverrideMixin:
    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget},
    }


@admin.register(Course)
class CourseAdmin(SaveModelMixin, PageDownOverrideMixin, admin.ModelAdmin):

    def get_queryset(self, request):
        queryset = super(CourseAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(author=request.user)


@admin.register(CourseArticle)
class CourseArticleAdmin(SaveModelMixin, PageDownOverrideMixin, admin.ModelAdmin):
    pass


@admin.register(GroupArticle)
class GroupArticleAdmin(PageDownOverrideMixin, admin.ModelAdmin):
    pass


@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return set()
        if obj and obj.creator == request.user:  # 允许组长修改成员
            if not obj.locked:
                return 'creator', 'locked'
        return 'creator', 'locked', 'members'

    def get_queryset(self, request):
        queryset = super(CourseGroupAdmin, self).get_queryset(request)
        print(queryset)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(creator=request.user)


admin.site.register(Evaluation)
