# Generated by Django 2.2.10 on 2020-06-05 15:18

from django.db import migrations


def remove(apps, schema_editor):
    apps.get_model("linguistics", "Template").objects.filter(key__in=(240004,
                                                                      240005,
                                                                      240017,
                                                                      240006,
                                                                      240007,
                                                                      80005,
                                                                      80006,
                                                                      80025)).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('linguistics', '0028_remove_place_jobs_templates'),
    ]

    operations = [
        migrations.RunPython(remove)
    ]
