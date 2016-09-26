# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xsolla', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='bank_invoice',
            field=models.OneToOneField(related_name='+', null=True, on_delete=django.db.models.deletion.SET_NULL, to='bank.Invoice'),
        ),
    ]
