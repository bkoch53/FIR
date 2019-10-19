from json import dumps

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from fir_relations.models import Relation
from findings.views import is_finding_handler, is_finding_viewer


@login_required
@user_passes_test(is_finding_viewer)
def relations(request, content_type, object_id):
    references = Relation.objects.filter(src_content_type=content_type,
                                         src_object_id=object_id,
                                         active=True).as_template_objects(request, relation_type='target')
    referenced_by = Relation.objects.filter(tgt_content_type=content_type,
                                            tgt_object_id=object_id,
                                            active=True).as_template_objects(request, relation_type='source')
    return render(request, "fir_relations/relations_sidebar.html",
                  {'references': references, 'referenced_by': referenced_by})


@login_required
@user_passes_test(is_finding_handler)
def remove_relation(request, relation_id):
    if request.method == "POST":
        relation = get_object_or_404(Relation, pk=relation_id)
        if hasattr(relation.source, 'has_perm') and \
                relation.source.has_perm(request.user, 'findings.handle_findings'):
            relation.active = False
            relation.save()
            return HttpResponse(dumps({'status': 'success'}), content_type="application/json")
    raise PermissionDenied
