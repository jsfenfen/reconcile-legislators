from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('',
        url(r'^reconcile/(?P<reconciliation_type>[\w\-]+)/$', 'reconcilers.views.refine'),
        url(r'^reconcile-json/(?P<reconciliation_type>[\w\-]+)/$', 'reconcilers.views.refine_json'),
        
)