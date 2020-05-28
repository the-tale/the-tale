
import smart_imports

smart_imports.all()


def collect_data(account_id):
    data = []

    for third_party in models.AccessToken.objects.filter(account=account_id):
        data.append(('third_party_token', {'created_at': third_party.created_at,
                                           'updated_at': third_party.updated_at,
                                           'uid': third_party.uid,
                                           'application_name': third_party.application_name,
                                           'application_info': third_party.application_info,
                                           'application_description': third_party.application_description,
                                           'state': third_party.state}))

    return data


def remove_data(account_id):
    models.AccessToken.objects.filter(account=account_id).delete()
