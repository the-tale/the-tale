# Generated by Django 2.0.13 on 2019-12-04 15:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0008_bill_depends_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
