from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^', include('answers.urls'))
)
