# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-29 22:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('most_recent_post', models.DateTimeField(blank=True, null=True)),
                ('image', models.FileField(null=True, upload_to='category_images')),
                ('num_threads', models.IntegerField(default=0)),
                ('num_posts', models.IntegerField(default=0)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(null=True, upload_to='profile_pics')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum_app.MyUser')),
            ],
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('most_recent_post', models.DateTimeField(blank=True, null=True)),
                ('num_posts', models.IntegerField(default=0)),
                ('slug', models.SlugField(unique=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum_app.MyUser')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum_app.Category')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum_app.Thread'),
        ),
    ]
