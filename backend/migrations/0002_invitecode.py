# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-20 04:29
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InviteCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, verbose_name='邀请码')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='send_code_set', to=settings.AUTH_USER_MODEL, verbose_name='邀请人')),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='code_set', to='backend.CourseGroup')),
                ('invitee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receive_code_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
