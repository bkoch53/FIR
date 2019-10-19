import datetime

from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from findings.authorization.decorator import authorization_required
from findings.views import is_finding_viewer
from findings.models import Finding, model_created, BusinessLine

from fir_todos.models import TodoItem, TodoItemForm, TodoListTemplate


@require_POST
@login_required
@authorization_required('findings.handle_findings', Finding, view_arg='finding_id')
def create(request, finding_id, authorization_target=None):
    if authorization_target is None:
        finding = get_object_or_404(
            Finding.authorization.for_user(request.user, 'findings.handle_findings'),
            pk=finding_id)
    else:
        finding = authorization_target

    form = TodoItemForm(request.POST, for_user=request.user)
    item = form.save(commit=False)
    item.finding = finding
    item.category = finding.category
    item.done = False
    item.save()

    return render(request, 'fir_todos/single.html', {'item': item})


@login_required
@authorization_required('findings.view_findings', Finding, view_arg='finding_id')
def list(request, finding_id, authorization_target=None):
    if authorization_target is None:
        finding = get_object_or_404(
            Finding.authorization.for_user(request.user, 'findings.handle_findings'),
            pk=finding_id)
    else:
        finding = authorization_target
    todos = finding.todoitem_set.all()
    if request.user.has_perm('findings.handle_findings', obj=finding):
        form = TodoItemForm(for_user=request.user)
    else:
        form = None
    return render(
        request, 'fir_todos/list.html',
        {'todos': todos, 'form': form, 'finding_id': finding_id}
    )


@require_POST
@login_required
def delete(request, todo_id):
    todo = get_object_or_404(TodoItem, pk=todo_id)
    if not request.user.has_perm(todo.finding, 'findings.handle_findings'):
        raise PermissionDenied()
    todo.delete()

    return HttpResponse('')


@require_POST
@login_required
def toggle_status(request, todo_id):
    todo = get_object_or_404(TodoItem, pk=todo_id)
    if (todo.business_line and request.user.has_perm('findings.view_findings', obj=todo.business_line)) or \
            request.user.has_perm('findings.handle_findings', obj=todo.finding):
        todo.done = not todo.done
        if todo.done:
            todo.done_time = datetime.datetime.now()
        todo.save()
    else:
        raise PermissionDenied()

    referer = request.META.get('HTTP_REFERER', None)
    dashboard = False
    if ('/findings/' not in referer) and ('/observations/' not in referer):
        dashboard = True

    return render(request, 'fir_todos/single.html', {'item': todo, 'dashboard': dashboard})


@login_required
@user_passes_test(is_finding_viewer)
def dashboard(request):
    bls = BusinessLine.authorization.for_user(request.user, 'findings.view_findings')
    bl_filter = Q(business_line__in=bls) | Q(business_line__isnull=True)
    todos = TodoItem.objects.filter(finding__isnull=False, done=False).filter(bl_filter)
    todos = todos.select_related('finding', 'category')
    todos = todos.order_by('-finding__date')

    page = request.GET.get('page', 1)
    todos_per_page = request.user.profile.finding_number
    p = Paginator(todos, todos_per_page)

    try:
        todos = p.page(page)
    except (PageNotAnInteger, EmptyPage):
        todos = p.page(1)

    return render(request, 'fir_todos/dashboard.html', {'todos': todos})


def get_todo_templates(category, detection, bl):
    results = []

    q = Q(category=category) | Q(category__isnull=True)
    q &= Q(detection=detection) | Q(detection__isnull=True)
    q &= Q(concerned_business_lines=bl) | Q(concerned_business_lines__isnull=True)

    results += TodoListTemplate.objects.filter(q)

    if not bl.is_root():
        results += [m for m in get_todo_templates(category, detection, bl.get_parent()) if m not in results]

    return results


def create_task(task, instance, bl=None):
    task.pk = None
    task.finding = instance
    task.category = instance.category

    if bl:
        task.business_line = bl

    task.save()


@receiver(model_created, sender=Finding)
def new_observation(sender, instance, **kwargs):
    todos = dict()

    for bl in instance.concerned_business_lines.all():
        for template in get_todo_templates(instance.category, instance.detection, bl):
            for task in template.todolist.all():
                if task.id not in todos:
                    todos[task.id] = {'task': task, 'bls': [bl]}
                else:
                    todos[task.id]['bls'].append(bl)

    for task_id in todos:
        if todos[task_id]['task'].business_line is None:
            for bl in todos[task_id]['bls']:
                create_task(todos[task_id]['task'], instance, bl)
        else:
            create_task(todos[task_id]['task'], instance)
