
import smart_imports

smart_imports.all()


class Friendship(django_models.Model):
    created_at = django_models.DateTimeField(auto_now_add=True, db_index=True)

    friend_1 = django_models.ForeignKey('accounts.Account', related_name='+', on_delete=django_models.CASCADE)
    friend_2 = django_models.ForeignKey('accounts.Account', related_name='+', on_delete=django_models.CASCADE)

    text = django_models.TextField(default='Давайте дружить')

    is_confirmed = django_models.BooleanField(default=False, db_index=True)
