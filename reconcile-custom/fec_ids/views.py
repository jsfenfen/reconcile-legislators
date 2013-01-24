from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404, render_to_response
from django.conf import settings
from django.http import Http404

from fec_ids.models import Candidate

try:
    PREVIEW_WIDTH = settings.PREVIEW_WIDTH
    PREVIEW_HEIGHT = settings.PREVIEW_HEIGHT
except:
    raise Exception("Couldn't import preview settings. Are PREVIEW_WIDTH and PREVIEW_HEIGHT defined in a settings file?")

def preview(request, fec_id):
    candidates = Candidate.objects.filter(fec_id=fec_id).order_by('-cycle')
    try:
        candidate = candidates[0]
    except IndexError:
        raise Http404
    return render_to_response('fec_preview.html', 
       {
       'candidate':candidate,
       'candidates':candidates,
       'preview_height':PREVIEW_HEIGHT - 30,
       'preview_width':PREVIEW_WIDTH - 20
       })
