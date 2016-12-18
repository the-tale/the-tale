# -*- coding: utf-8 -*-


import datetime

from django.db import models, migrations


GAME_START_TIME = datetime.datetime(2012, 6, 27, 11, 25, 4, 804708)


def fill_created_at_turn(apps, schema_editor):
    Post = apps.get_model("blogs", "Post")

    for post in Post.objects.all():
        post.created_at_turn = (post.created_at - GAME_START_TIME).total_seconds() / 10
        post.save()


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0002_post_created_at_turn'),
    ]

    operations = [
        migrations.RunPython(
            fill_created_at_turn,
        ),
    ]
