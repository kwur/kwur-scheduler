from django.urls import include, re_path
from . import views


# urlpatterns = [
#     re_path(r'^$', home, name='home'),
#     re_path(r'^myapp/', include('myapp.urls'),
# ]

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^submit-show/?$', views.submit_show),
    re_path(r'^additional-times/(?P<dj_id>[0-9]+)/?$', views.additional_times),
    re_path(r'^submit-additional-times/(?P<dj_id>[0-9]+)/?$', views.submit_additional_times),
    re_path(r'^tentative-schedule/?$', views.tentative_schedule),
    re_path(r'^login/?$', views.login_page, name='login_page'),
    re_path(r'^crediting/?$', views.crediting),
    re_path(r'^show-names-schedule/?$', views.schedule_with_names),
    re_path(r'^submit-credits/?$', views.submit_credits),
    re_path(r'^view-credits/?$', views.view_credits),
    re_path(r'^finalize-creditings/?$', views.finalize_creditings),
]