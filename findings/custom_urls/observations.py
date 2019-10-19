from django.conf.urls import url

from findings import views

urlpatterns = [
    url(r'^new/$', views.new_observation, name='new'),
    url(r'^$', views.observation_index, name='index'),
    url(r'^all/$', views.observations_all, name='all'),
    url(r'^(?P<finding_id>\d+)/$', views.details, name='details'),
]
