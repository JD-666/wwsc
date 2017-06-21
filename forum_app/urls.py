# forum_app specific URLs
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from forum_app import views

#app_name = 'forum' # used for namespacing like {% url 'forum:categories' %}
urlpatterns =[
    url(r'^$', views.category_list, name='categories'),
    url(r'^category/(?P<category_slug>[\w\-]+)/$', views.thread_list, 
        name='threads'),
    url(r'^thread/[\w\-]+/(?P<thread_slug>[\w\-]+)/$',
        views.thread, name='thread'),
    url(r'^edit/(?P<category_slug>[\w\-]+)/$', views.category_edit,
        name='category_edit'),
    url(r'^search/$', views.search_bar, name='search'),
    url(r'^ajax_login/$', views.ajax_login, name='ajax_login'),
    url(r'^register/$', views.register_user, name='register'),
    url(r'^profile/(?P<username>[\w]+)/$', views.profile, name='profile'),
    url(r'^users/$', views.profile_list, name='profile_list'),
]