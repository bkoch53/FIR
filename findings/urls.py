from django.conf.urls import url

from findings import views

urlpatterns = [
    url(r'^$', views.index, {'is_finding': True}, name='index'),
    url(r'^all/$', views.findings_all, name='all'),
    url(r'^(?P<finding_id>\d+)/$', views.details, name='details'),
    url(r'^(?P<finding_id>\d+)/followup/$', views.followup, name='followup'),
    url(r'^(?P<finding_id>\d+)/comment/$', views.comment, name='comment'),
    url(r'^(?P<finding_id>\d+)/comment/(?P<comment_id>\d+)/delete/$', views.delete_comment, name='delete_comment'),
    url(r'^(?P<finding_id>\d+)/edit/$', views.edit_finding, name='edit'),
    url(r'^(?P<finding_id>\d+)/delete/$', views.delete_finding, name='delete'),
    url(r'^(?P<finding_id>\d+)/status/(?P<status>[OBC])$', views.change_status, name='change_status'),
    url(r'^(?P<finding_id>\d+)/attribute$', views.add_attribute, name='add_attribute'),
    url(r'^(?P<finding_id>\d+)/attribute/(?P<attribute_id>\d+)/delete/$', views.delete_attribute, name='delete_attribute'),
]
