from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404, render_to_response
from django.conf import settings

from legislators.models import Legislator, Term

try:
    PREVIEW_WIDTH = settings.PREVIEW_WIDTH
    PREVIEW_HEIGHT = settings.PREVIEW_HEIGHT
except:
    raise Exception("Couldn't import preview settings. Are PREVIEW_WIDTH and PREVIEW_HEIGHT defined in a settings file?")

def preview(request, bioguide_id):
    legislator = get_object_or_404(Legislator, bioguide=bioguide_id)
    terms = Term.objects.filter(legislator=legislator).order_by('-start')
    
    return render_to_response('preview.html', 
       {
       'legislator':legislator,
       'terms':terms,
       'preview_height':PREVIEW_HEIGHT - 30,
       'preview_width':PREVIEW_WIDTH - 20
       })
"""
http://localhost:8000/refine/reconcile/legislators/
"""