
import smart_imports

smart_imports.all()


class Setting(django_models.Model):

    updated_at = django_models.DateTimeField(auto_now=True)

    key = django_models.CharField(max_length=64, unique=True, db_index=True)

    value = django_models.TextField(default='')
