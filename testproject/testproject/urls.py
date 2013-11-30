from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^klaus/', include('klaus.urls', namespace='klaus'))
)
