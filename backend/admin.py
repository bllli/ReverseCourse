from django.db import models
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from pagedown.widgets import AdminPagedownWidget


from .models import Course, CourseGroup, GroupArticle, CourseArticle, Evaluation, User


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


class CourseArticleInline(SaveModelMixin, admin.TabularInline):
    model = CourseArticle
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            if request.user.is_superuser:
                readonly = ('create_date', )
            else:
                readonly = ('create_date', 'author')
            return self.readonly_fields + readonly
        return self.readonly_fields
    verbose_name = '课程文章'
    verbose_name_plural = verbose_name


class CourseGroupInline(admin.TabularInline):
    model = CourseGroup
    extra = 0


@admin.register(Course)
class CourseAdmin(SaveModelMixin, PageDownOverrideMixin, admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'status', 'author')}),
        ('群组', {'fields': ('group_members_min', 'group_members_max',)}),
        ('正文', {'fields': ('detail', )}),
        ('时间', {'fields': ('create_date', 'start_date', 'finish_date')}),
    )

    inlines = (CourseArticleInline, CourseGroupInline)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            if request.user.is_superuser:
                readonly = ('create_date', )
            else:
                readonly = ('create_date', 'author')
            return self.readonly_fields + readonly
        return self.readonly_fields

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(author=request.user)


# @admin.register(CourseArticle)
# class CourseArticleAdmin(SaveModelMixin, PageDownOverrideMixin, admin.ModelAdmin):
#     pass


@admin.register(GroupArticle)
class GroupArticleAdmin(PageDownOverrideMixin, admin.ModelAdmin):
    readonly_fields = ('group', 'create_date', 'submit_date', 'score', 'scoring_people')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(group__in=request.user.added_groups.all())

    def save_model(self, request, obj, form, change):
        obj.group = request.user.added_groups.filter(pk=obj.belong.pk).first()
        obj.save()


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
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(creator=request.user)


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            if not request.user.is_superuser:
                readonly = ('last_login', 'date_joined', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'is_active')
            else:
                readonly = ('last_login', 'date_joined')
            return self.readonly_fields + readonly
        return self.readonly_fields

    def get_queryset(self, request):
        query_set = super().get_queryset(request)
        if request.user.is_superuser:
            return query_set
        return query_set.filter(pk=request.user.pk)


admin.site.register(Evaluation)
