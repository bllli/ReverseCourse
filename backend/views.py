from django.http import Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from notifications.signals import notify
from notifications.models import Notification

from backend.models import Course, User, CourseGroup, Invite, Status
from backend.forms import LoginForm, CreateGroupForm, LetterForm
from backend.utils import get_form_error_msg


def index(request):
    return render(request, 'index.html')


def login(request):
    if request.user.is_authenticated():
        messages.warning(request, '用户 {username}, 你已经登陆'.format(username=request.user.username))
        return redirect('index')
    login_form = LoginForm(request.POST.dict() or None)
    if request.method == 'POST' and login_form.is_valid():
        username = login_form.cleaned_data.get('username')
        password = login_form.cleaned_data.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            messages.success(request, '欢迎回来, {username}'.format(username=request.user.username))
            return redirect('index')
        else:
            messages.error(request, '账号或密码错误')
    return render(request, 'login.html', {'login_form': login_form})


@login_required
def logout(request):
    messages.success(request, '登出成功, Bye~')
    auth.logout(request)
    return redirect('index')


def user_detail(request, username):
    letter_form = LetterForm(request.POST or None)
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated() and letter_form.is_valid():
        notify.send(request.user, recipient=user, verb='给你发了一封私信',
                    description=letter_form.cleaned_data.get('content', None))
        messages.success(request, '发送成功')
        return redirect('user_detail', username)
    added_courses = [group.belong for group in user.added_groups.all()]
    return render(request, 'user_detail.html', {
        'user': user,
        'courses': added_courses,
    })


@login_required
def create_group(request, course_id):
    form = CreateGroupForm(request.POST or None)
    course = get_object_or_404(Course, pk=course_id)
    if request.user.added_groups.filter(belong=course).first():
        raise Http404('别瞎试了, 你已经加入一个团队了')
    if request.POST and form.is_valid():
        new_group = request.user.my_groups.create(name=form.cleaned_data.get('name'), belong=course)
        new_group.members.add(request.user)
        new_group.save()
        return redirect('group_detail', new_group.pk)
    else:
        messages.warning(request, get_form_error_msg(form))
    return render(request, 'group_create.html', {'course': course})


def groups(request):
    queryset = CourseGroup.objects.all()
    query = request.GET.get('query', None)
    course_id = request.GET.get('course', None)
    params = {}
    if query:
        params['query'] = query
        queryset = queryset.filter(name__contains=query)
    elif course_id:
        params['course'] = get_object_or_404(Course, pk=course_id)
        queryset = queryset.filter(belong=params['course'])
    p = Paginator(queryset, 5)
    page = request.GET.get('page') or 1
    try:
        params['p'] = p.page(page)
    except PageNotAnInteger:
        params['p'] = p.page(1)
    except EmptyPage:
        params['p'] = p.page(p.num_pages)
    return render(request, 'groups.html', params)


def group_detail(request, group_id):
    group = get_object_or_404(CourseGroup, pk=group_id)
    params = {}
    if request.user.is_authenticated():
        if request.user == group.creator and group.can_invite_user():
            params['can_invite'] = True
            params['users'] = User.objects.exclude(added_groups__belong_id=group.belong_id).all()
        if group.can_join_group(request.user):
            params['can_join'] = True
        elif group.can_leave_group(request.user):
            params['can_quit'] = True
    params['group'] = group
    return render(request, 'group_detail.html', params)


@login_required
def invite_into_group(request, group_id, invitees_id):
    invitees = get_object_or_404(User, pk=invitees_id)
    group = get_object_or_404(CourseGroup, pk=group_id)
    if group.creator != request.user and group.can_join_group(invitees):  # 只有队长才能邀请其他人
        messages.error(request, '邀请失败， 可能你邀请的人已经在同课程中别的群里了。')
    else:
        if group.already_invite(invitees):
            messages.success(request, '已经邀请过{invitees}，请不要发送多条邀请。'.format(invitees=invitees))
        else:
            invite_code = Invite.generate(creator=request.user, invitee=invitees,
                                          group=group, choice=Invite.INVITE_USER_JOIN_GROUP)
            notify.send(request.user, recipient=invitees,
                        verb='邀请你加入<a href="/groups/{g_id}/" target="_blank">{group}</a>'
                        .format(group=group.name, g_id=group.pk),
                        target=group,
                        description=invite_code)
            messages.success(request, '邀请{invitees}成功!'.format(invitees=invitees))
    return redirect('group_detail', group.pk)


@login_required
def apply_join_group(request, group_id):
    group = get_object_or_404(CourseGroup, pk=group_id)
    current_group = request.user.added_groups.filter(belong=group.belong).first()
    if current_group:
        messages.error(request, '你已经在<a href="/groups/{g_id}/">{g_name}</a>里了。'
                       .format(g_id=group.pk, g_name=group.name))
    else:
        code = Invite.generate(creator=request.user, invitee=group.creator,
                               group=group, choice=Invite.APPLY_JOIN_GROUP)
        notify.send(request.user, recipient=group.creator,
                    verb='申请加入<a href="/groups/{g_id}/" target="_blank">{group}</a>'
                    .format(group=group.name, g_id=group.pk),
                    target=group, description=code)
        messages.success(request, '申请加入{g_name}成功!'.format(g_name=group.name))
    return redirect('group_detail', group.pk)


@login_required
def apply_quit_group(request, group_id):
    group = get_object_or_404(CourseGroup, pk=group_id)
    if group not in request.user.added_groups.all():
        messages.error(request, '你没在本团队内。')
    else:
        code = Invite.generate(creator=request.user, invitee=group.creator,
                               group=group, choice=Invite.APPLY_QUIT_GROUP)
        notify.send(request.user, recipient=group.creator,
                    verb='申请退出<a href="/groups/{g_id}/" target="_blank">{group}</a>'
                    .format(group=group.name, g_id=group.pk),
                    target=group, description=code)
        messages.success(request, '申请退出{g_name}成功!'.format(g_name=group.name))
    return redirect('group_detail', group.pk)


@login_required
def accept_invite(request, str_code: str):
    code = get_object_or_404(Invite, code=str_code)
    notification = get_object_or_404(Notification, recipient=request.user, description=str_code)
    if code.check_code(request.user):
        notification.mark_as_read()
        if code.choice is Invite.INVITE_USER_JOIN_GROUP:
            if not code.group.can_join_group(request.user):  # 能加进去
                messages.success(request, '加入失败，团队成员已满或你已经加入了本课题下的另一个团队')
            else:
                code.group.join(request.user)
                messages.success(request, '已加入{group_name}, 祝学习愉快!'.format(group_name=code.group.name))
                return redirect('group_detail', code.group.pk)
        elif code.choice in Invite.APPLY:  # 申请类型code
            if code.choice is Invite.APPLY_QUIT_GROUP:
                code.group.leave(code.creator)
                messages.success(request, '你已同意{user}退出{group}'.format(user=code.creator, group=code.group))
            elif code.choice is Invite.APPLY_JOIN_GROUP:
                code.group.join(code.creator)
                messages.success(request, '你已同意{user}加入{group}'.format(user=code.creator, group=code.group))
        return redirect('inbox')
    raise Http404('别捣乱')


@login_required
def refuse_invite(request, code):
    invite_code = get_object_or_404(Invite, code=code)
    notification = get_object_or_404(Notification, recipient=request.user, description=code)
    if invite_code.check_code(request.user):
        messages.success(request, '已拒绝')
        notification.mark_as_read()
        return redirect('inbox')
    raise Http404('别捣乱')


@login_required
def inbox(request):
    queryset = request.user.notifications
    return render(request, 'inbox.html', {'notifications': queryset})
