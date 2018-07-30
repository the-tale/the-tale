
import smart_imports

smart_imports.all()


def add_permissions(group, permissions):
    for permission_string in permissions:

        app_label, permission = permission_string.split('.')
        model_label = permission.split('_')[-1]

        content_type = django_contenttypes_models.ContentType.objects.get(app_label=app_label, model=model_label)

        perm = django_auth_models.Permission.objects.get(codename=permission, content_type=content_type)

        group.permissions.add(perm)


def sync_group(group_name, permissions):
    try:
        group = django_auth_models.Group.objects.get(name=group_name)
    except django_auth_models.Group.DoesNotExist:
        group = django_auth_models.Group.objects.create(name=group_name)

    group.permissions.clear()
    add_permissions(group, permissions)

    return group
