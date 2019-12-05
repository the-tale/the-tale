# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('collections', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountitems',
            name='account',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]
