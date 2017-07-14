# forum_app specific URLs
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from forum_app import views

#app_name = 'forum' # used for namespacing like {% url 'forum:categories' %}
urlpatterns =[
    url(r'^search/$', views.search_bar, name='search'),
    url(r'^ajax_login/$', views.ajax_login, name='ajax_login'),
    url(r'^register/$', views.register_user, name='register'),
    url(r'^profile/(?P<username>[\w]+)/$', views.profile, name='profile'),
    url(r'^profile/(?P<username>[\w]+)/conversations/$', views.conversations,
        name='conversations'),
    url(r'^profile/(?P<username>[\w]+)/conversations/(?P<is_with>[\w]+)/delete/$',
        views.delete_conversation, name='delete_conversation'),
    url(r'^profile/(?P<username>[\w]+)/conversations/(?P<is_with>[\w]+)/$',
        views.conversation, name='conversation'),
    url(r'^users/$', views.profile_list, name='profile_list'),
    url(r'^$', views.category_list, name='categories'),
    url(r'^add-category/$', views.category_add,
        name='category_add'),
    url(r'^(?P<category_slug>[\w\-]+)/$', views.thread_list, 
        name='threads'),
    url(r'^(?P<category_slug>[\w\-]+)/edit/$', views.category_edit,
        name='category_edit'),
    url(r'^(?P<category_slug>[\w\-]+)/add-thread/$', views.thread_add,
            name='thread_add'),
    url(r'^(?P<category_slug>[\w\-]+)/(?P<thread_slug>[\w\-]+)/$',
        views.thread, name='thread'),
    url(r'^(?P<category_slug>[\w\-]+)/(?P<thread_slug>[\w\-]+)/edit/$', views.thread_edit,
            name='thread_edit'),
]