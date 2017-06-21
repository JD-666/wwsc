"""forum_project URL Configuration

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
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
import django.contrib.auth.views
from django.http import HttpResponseRedirect
from django.conf.urls.static import static
from django.core.urlresolvers import reverse

from forum_app import views

urlpatterns = [
    url(r'^$', lambda r: HttpResponseRedirect('forum/')),
    url(r'^admin/', admin.site.urls),
    url(r'^forum/', include('forum_app.urls')), # Maps URLs to forum_app
    url(r'^accounts/login/$', django.contrib.auth.views.login, name='login'),
    url(r'^accounts/logout/$', django.contrib.auth.views.logout, name='logout',
        kwargs={'next_page': '/'}),
    url(r'^accounts/change-password/$', 
        django.contrib.auth.views.password_change, 
        {'template_name':'forum/change_password.html'}, name='password_change'),
    url(r'^accounts/change-password-done/$', 
        django.contrib.auth.views.password_change_done, 
        {'template_name':'registration/change_password_done.html'}, 
        name='password_change_done'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
