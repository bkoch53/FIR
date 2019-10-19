from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from django.http import HttpResponse
from json import dumps

from findings.authorization.decorator import authorization_required
from findings.models import Finding
from fir_nuggets.models import Nugget, NuggetForm


@login_required
@authorization_required('findings.view_findings', Finding, view_arg='observation_id')
def list(request, observation_id, authorization_target=None):
    if authorization_target is None:
        e = get_object_or_404(
            Finding.authorization.for_user(request.user, 'findings.handle_findings'),
            pk=observation_id)
    else:
        e = authorization_target
    nuggets = e.nugget_set.all().order_by('start_timestamp')
    return render(request, 'fir_nuggets/list.html', {'nuggets': nuggets})


@login_required
@authorization_required('findings.handle_findings', Finding, view_arg='observation_id')
def new(request, observation_id, authorization_target=None):
    if authorization_target is None:
        e = get_object_or_404(
            Finding.authorization.for_user(request.user, 'findings.handle_findings'),
            pk=observation_id)
    else:
        e = authorization_target

    if request.method == "GET":
        nugget_form = NuggetForm()

    if request.method == 'POST':
        nugget_form = NuggetForm(request.POST)

        if nugget_form.is_valid():
            nugget = nugget_form.save(commit=False)
            nugget.finding = e
            nugget.found_by = request.user
            nugget.save()

            ret = {
                'status': 'success',
                'row': render_to_string("fir_nuggets/nugget_row.html", {'n': nugget, 'mode': 'row', "user": request.user}),
                'raw': render_to_string("fir_nuggets/nugget_row.html", {'n': nugget, 'mode': 'raw', "user": request.user}),
                'nugget_id': nugget.id,
                'mode': 'new',
            }

            e.refresh_artifacts(nugget.raw_data)

            return HttpResponse(dumps(ret), content_type='application/json')
        else:
            errors = render_to_string("fir_nuggets/nugget_form.html", {'mode': 'new', 'nugget_form': nugget_form, 'observation_id': e.id})
            ret = {'status': 'error', 'data': errors}
            return HttpResponse(dumps(ret), content_type="application/json")

    return render(request, "fir_nuggets/nugget_form.html", {'nugget_form': nugget_form, 'mode': 'new', 'observation_id': observation_id})


@login_required
def edit(request, nugget_id):
    n = get_object_or_404(Nugget, pk=nugget_id)
    e = n.finding
    if not request.user.has_perm('findings.handle_findings', obj=e):
        ret = {'status': 'error', 'data': ['Permission denied', ]}
        return HttpResponse(dumps(ret), content_type="application/json")
    if request.method == "GET":
        nugget_form = NuggetForm(instance=n)
        return render(request, "fir_nuggets/nugget_form.html", {'mode': 'edit', 'nugget_form': nugget_form, 'nugget_id': n.id})

    if request.method == "POST":
        nugget_form = NuggetForm(request.POST, instance=n)

        if nugget_form.is_valid():
            nugget = nugget_form.save()
            ret = {
                'status': 'success',
                'mode': 'edit',
                'nugget_id': nugget.id,
                'row': render_to_string("fir_nuggets/nugget_row.html", {'n': nugget, 'mode': 'row', "user": request.user}),
                'raw': render_to_string("fir_nuggets/nugget_row.html", {'n': nugget, 'mode': 'raw', "user": request.user}),
            }
            return HttpResponse(dumps(ret), content_type='application/json')

        else:
            errors = render_to_string("fir_nuggets/nugget_form.html", {'mode': 'edit', 'nugget_form': nugget_form, 'nugget_id': n.id})
            ret = {'status': 'error', 'data': errors}
            return HttpResponse(dumps(ret), content_type="application/json")


@login_required
def delete(request, nugget_id):
    n = get_object_or_404(Nugget, pk=nugget_id)
    e = n.finding
    if not request.user.has_perm('findings.handle_findings', obj=e):
        ret = {'status': 'error', 'data': ['Permission denied', ]}
        return HttpResponse(dumps(ret), content_type="application/json")
    n.delete()
    return HttpResponse(nugget_id)
