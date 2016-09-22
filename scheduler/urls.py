from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^submit-show/?$', views.submit_show),
    url(r'^additional-times/(?P<dj_id>[0-9]+)/?$', views.additional_times),
    url(r'^submit-additional-times/(?P<dj_id>[0-9]+)/?$', views.submit_additional_times),
]