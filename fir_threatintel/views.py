from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import redirect

from findings.views import is_finding_handler

from fir_threatintel.models import YetiProfile


@login_required
@user_passes_test(is_finding_handler)
def update_api(request):
    yp, _ = YetiProfile.objects.get_or_create(user_id=request.user)

    yp.api_key = request.POST.get('yeti_api', '')
    yp.endpoint = request.POST.get('endpoint', '')
    yp.save()

    messages.success(request, "Yeti API successfully updated")
    return redirect("user:profile")
