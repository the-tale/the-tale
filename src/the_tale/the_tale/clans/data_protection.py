
import smart_imports

smart_imports.all()


def collect_account_data(account_id):
    data = []

    membership = logic.get_membership(account_id)

    if membership is None:
        data.append(('clan_id', None))
    else:
        data.append(('clan_id', membership.clan_id))

    return data


def remove_account_data(account_id):
    membership = logic.get_membership(account_id)

    if membership is None:
        return

    clan = logic.load_clan(membership.clan_id)

    member = accounts_prototypes.AccountPrototype.get_by_id(account_id)

    logic.remove_member(initiator=accounts_logic.get_system_user(),
                        clan=clan,
                        member=member,
                        force=True)

    if logic.members_number(membership.clan_id) == 0:
        logic.remove_clan(clan)
