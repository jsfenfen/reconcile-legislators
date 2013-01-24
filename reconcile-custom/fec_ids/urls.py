from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('',
        url(r'^preview/(?P<fec_id>[\w\d]+)/$', 'fec_ids.views.preview'),
)