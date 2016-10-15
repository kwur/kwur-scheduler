from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^submit-show/?$', views.submit_show),
    url(r'^additional-times/(?P<dj_id>[0-9]+)/?$', views.additional_times),
    url(r'^submit-additional-times/(?P<dj_id>[0-9]+)/?$', views.submit_additional_times),
    url(r'^tentative-schedule/?$', views.tentative_schedule),
    url(r'^login/?$', views.login_page, name='login_page'),
    url(r'^crediting/?$', views.crediting),
    url(r'^show-names-schedule/?$', views.schedule_with_names),
    url(r'^submit-credits/?$', views.submit_credits),
    url(r'^view-credits/?$', views.view_credits),
    url(r'^finalize-creditings/?$', views.finalize_creditings),
]