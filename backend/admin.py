from django.db import models
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from pagedown.widgets import AdminPagedownWidget
from django.utils.translation import ugettext, ugettext_lazy as _


from .models import Course, CourseGroup, GroupArticle, CourseArticle, Evaluation, User


class SaveModelMixin:
    def save_model(self, request, obj, form, change):
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

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()


class CourseGroupInline(admin.TabularInline):
    model = CourseGroup
    extra = 0

    verbose_name = '课程小组'
    verbose_name_plural = verbose_name


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
        if request.user.is_superuser:
            readonly = ('create_date', )
        else:
            readonly = ('create_date', 'author')
        return self.readonly_fields + readonly

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(author=request.user)


# @admin.register(CourseArticle)
# class CourseArticleAdmin(SaveModelMixin, PageDownOverrideMixin, admin.ModelAdmin):
#     pass

class EvaluationInline(SaveModelMixin, admin.TabularInline):
    model = Evaluation
    extra = 0

    verbose_name = '课程评价'
    verbose_name_plural = verbose_name

    readonly_fields = ('author', 'create_date')
    exclude = ('delete', 'final')

    def save_model(self, request, obj, form, change):
        print('1231231')
        obj.author = request.user
        obj.save()


@admin.register(GroupArticle)
class GroupArticleAdmin(PageDownOverrideMixin, admin.ModelAdmin):
    # readonly_fields = ('group', 'create_date', 'submit_date', 'score', 'scoring_people')
    inlines = (EvaluationInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # queryset = GroupArticle.objects.all()
        if request.user.is_superuser:
            return queryset
        if request.user.user_type == User.STUDENT:
            return queryset.filter(group__in=request.user.my_groups.all())
        if request.user.user_type == User.TEACHER:
            return queryset.filter(group__belong__author=request.user)

    def save_formset(self, request, form, formset, change):
        # https://stackoverflow.com/questions/3048313/why-save-model-method-doesnt-work-in-admin-stackedinline
        for f in formset.forms:
            obj = f.instance
            obj.author = request.user
            obj.save()
        formset.save()

    def get_readonly_fields(self, request, obj: GroupArticle=None):
        readonly_fields = ('create_date', 'submit_date')
        request.user: User
        if request.user.is_superuser:
            return readonly_fields
        else:
            if obj and obj.belong.deadline < timezone.localtime():
                readonly_fields += ('content', )
            elif request.user.user_type == User.TEACHER:
                readonly_fields += ('content', )
            elif request.user.user_type == User.STUDENT:
                # readonly_fields += ()
                pass
            readonly_fields += ('group', )
        return readonly_fields

    exclude = ('status', 'belong', 'score', 'scoring_people')


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

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'user_type')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'is_staff', 'user_type')

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
