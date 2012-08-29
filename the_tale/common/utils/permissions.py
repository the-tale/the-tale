# coding: utf-8

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def add_permissions(group, permissions):
    for permission_string in permissions:
        app_label, permission =  permission_string.split('.')
        model_label = permission.split('_')[-1]

        content_type = ContentType.objects.get(app_label=app_label, model=model_label)

        perm = Permission.objects.get(codename=permission, content_type=content_type)
        group.permissions.add(perm)

def sync_group(group_name, permissions):
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        group = Group.objects.create(name=group_name)

    group.permissions.clear()
    add_permissions(group, permissions)

    return group
