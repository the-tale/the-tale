
import smart_imports

smart_imports.all()


def collect_data(account_id):
    data = []

    friendships = models.Friendship.objects.filter(django_models.Q(friend_1_id=account_id) |
                                                   django_models.Q(friend_2_id=account_id))

    for friendship in friendships:
        data.append(('friendship', {'friend_1': friendship.friend_1_id,
                                    'friend_2': friendship.friend_2_id,
                                    'is_confirmed': friendship.is_confirmed,
                                    'text': friendship.text,
                                    'created_at': friendship.created_at}))
    return data


def remove_data(account_id):
    models.Friendship.objects.filter(django_models.Q(friend_1_id=account_id) |
                                     django_models.Q(friend_2_id=account_id)).delete()
