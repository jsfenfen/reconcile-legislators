from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('',
        url(r'^reconcile/(?P<reconciliation_type>[\w\-]+)/$', 'reconcile.views.refine'),
)