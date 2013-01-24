from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('',
        url(r'^preview/(?P<bioguide_id>[\w\d]+)/$', 'legislators.views.preview'),
)