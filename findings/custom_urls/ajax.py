from django.conf.urls import url
from findings import views


urlpatterns = [
    url(r'^comment/(?P<comment_id>\d+)$', views.update_comment, name='update_comment'),
    url(r'^finding/(?P<finding_id>\d+)/toggle_star/$', views.toggle_star, name='toggle_star'),
]
