from django.contrib import admin

from forum_app.models import Profile, Category, Thread, Post, Conversation, Pm

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(Conversation)
admin.site.register(Pm)
