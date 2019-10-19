from pkgutil import find_loader
from django.conf.urls import include, url
from django.contrib import admin

from fir.config.base import INSTALLED_APPS, TF_INSTALLED
from findings import views

# urls for core FIR components
urlpatterns = [
    url(r'^logout/', views.user_logout, name='logout'),
    url(r'^findings/', include('findings.urls', namespace='findings')),
    url(r'^search/$', views.search, name='search'),
    url(r'^observations/', include('findings.custom_urls.observations', namespace='observations')),
    url(r'^stats/', include('findings.custom_urls.stats', namespace='stats')),
    url(r'^ajax/', include('findings.custom_urls.ajax', namespace='ajax')),
    url(r'^user/', include('findings.custom_urls.user', namespace='user')),
    url(r'^dashboard/', include('findings.custom_urls.dashboard', namespace='dashboard')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.dashboard_main),
]

if TF_INSTALLED:
    from two_factor.views import LoginView
    from two_factor.urls import urlpatterns as tf_urls
    custom_urls = []
    for tf_url in tf_urls[0]:
        if tf_url.name != "login":
            custom_urls.append(tf_url)
    custom_urls.append(url(regex=r'^account/login/$',
                           view=views.CustomLoginView.as_view(),
                           name='login',))
    urlpatterns.append(url(r'', include((custom_urls, 'two_factor'))))
else:
    urlpatterns.append(url(r'^login/', views.user_login, name='login'))


for app in INSTALLED_APPS:
    if app.startswith('fir_'):
        app_name = app[4:]
        app_urls = '{}.urls'.format(app)
        if find_loader(app_urls):
            urlpatterns.append(url('^{}/'.format(app_name), include(app_urls, namespace=app_name)))
