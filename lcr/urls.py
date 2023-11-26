"""lcr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse

from . import accountviews
from . import settings

urlpatterns = [
    url(r'^', include('lkft.urls')),
    url(r'^robots.txt$', lambda _: HttpResponse("User-agent: *\nDisallow: /\n", content_type='text/plain')),
    url(r'^lkft/', include('lkft.urls')),
    url(r'^admin/', admin.site.urls),

    url(r'^accounts/register/$', accountviews.SignUpView.as_view(), name='signup'),
    url(r'^accounts/login/$', accountviews.LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', accountviews.LogOutView.as_view(), name='logout'),
    url(r'^accounts/change_password/$', accountviews.change_password, name='change_password'),
    url(r'^accounts/no_permission/$', accountviews.NoPermissionView.as_view(), name='no_permmission'),
]

if settings.ENABLE_APP_REPORT:
    urlpatterns = urlpatterns + [
            url(r'^report/', include('report.urls')), ## TO BE UPDATED, to uncomment when enable the lcr report app
        ]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
