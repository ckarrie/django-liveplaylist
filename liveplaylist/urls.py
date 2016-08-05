import views
from django.conf.urls import url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url('^$', views.IndexView.as_view(), name='index'),
    url('^pl/(?P<pk>[-\w]+)/m3u/$', views.PlayListM3UView.as_view(), name='pl_m3u'),
    url(r'^db/', include(admin.site.urls)),
]