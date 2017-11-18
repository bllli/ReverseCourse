from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Course, CourseGroup, Comment, Article


class SaveModelMixin:
    def save_model(self, request, obj, form, change):
        # old = None
        # if change:
        #     old = self.model.objects.get(pk=obj.pk)
        try:
            obj.author
        except:
            obj.author = request.user
        obj.save()


@admin.register(Course)
class CourseAdmin(SaveModelMixin, admin.ModelAdmin):

    fieldsets = (
        (None, {
            'fields': ('title', 'detail')
        }),
        ('高级', {
            'fields': ('group_members_min', 'group_members_max')
        })
    )

    def get_queryset(self, request):
        queryset = super(CourseAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(author=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        print(db_field.name)
        print(db_field)
        if db_field.name is 'detail':
            kwargs['queryset'] = Article.objects.filter(author=request.user)
        return super(CourseAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Article)
class ArticleAdmin(SaveModelMixin, admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'content_md')
        }),
    )

    def get_queryset(self, request):
        queryset = super(ArticleAdmin, self).get_queryset(request)
        print(request.user.groups.all())
        print(dir(request.user.groups))
        print(Group.objects.all())
        if request.user.is_superuser:
            return queryset
        return queryset.filter(author=request.user)


@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):
    # fields = ()

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
        # q = queryset.filter(creator=request.user) | queryset.filter(members=request.user)
        # q = [g for g in queryset.all() if g.in_group(request.user)]
        # print(q)
        return queryset.filter(creator=request.user)


# admin.site.register(CourseGroup)

admin.site.register(Comment)
