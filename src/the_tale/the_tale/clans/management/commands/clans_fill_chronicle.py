
import smart_imports

smart_imports.all()


def date_to_turn(date):
    turn = game_turn.number()
    now = datetime.datetime.now()

    return int(turn - (now - date).total_seconds() / 10)


class Command(django_management.BaseCommand):

    help = 'fill clans chronicle'

    def handle(self, *args, **options):
        total_clans = models.Clan.objects.all().count()

        all_events = []

        for i, clan in enumerate(models.Clan.objects.all().order_by('id')):
            print('process clan {} / {}'.format(i, total_clans))

            events = [{'message': 'Основана гильдия',
                       'clan': clan,
                       'event': relations.EVENT.CREATED,
                       'tags': (),
                       'attributes': {'clan_id': clan.id},
                       'turn': date_to_turn(clan.created_at),
                       'timestamp': time.mktime(clan.created_at.timetuple())}]

            for member in models.Membership.objects.filter(clan_id=clan.id):
                account = accounts_prototypes.AccountPrototype(member.account)

                events.append({'message': 'В гильдию вступил(а) {}'.format(account.nick_verbose),
                               'clan': clan,
                               'event': relations.EVENT.TECHNICAL,
                               'tags': (account.meta_object().tag,),
                               'attributes': {'clan_id': clan.id,
                                              'account_id': account.id},
                               'turn': date_to_turn(member.created_at),
                               'timestamp': time.mktime(member.created_at.timetuple())})

            for request in models.MembershipRequest.objects.filter(clan_id=clan.id):
                account = accounts_prototypes.AccountPrototype(request.account)
                initiator = accounts_prototypes.AccountPrototype(request.initiator)

                if request.type.is_FROM_CLAN:
                    events.append({'message': '{} пригласил(а) игрока {} в гильдию'.format(initiator.nick_verbose,
                                                                                           account.nick_verbose),
                                   'clan': clan,
                                   'event': relations.EVENT.NEW_MEMBERSHIP_INVITE,
                                   'tags': (account.meta_object().tag, initiator.meta_object().tag),
                                   'attributes': {'clan_id': clan.id,
                                                  'account_id': account.id,
                                                  'initiator_id': initiator.id},
                                   'turn': date_to_turn(request.created_at),
                                   'timestamp': time.mktime(request.created_at.timetuple())})
                else:
                    events.append({'message': 'Игрок {} хочет вступить в гильдию'.format(account.nick_verbose),
                                   'clan': clan,
                                   'event': relations.EVENT.NEW_MEMBERSHIP_REQUEST,
                                   'tags': (account.meta_object().tag, initiator.meta_object().tag),
                                   'attributes': {'clan_id': clan.id,
                                                  'account_id': account.id,
                                                  'initiator_id': initiator.id},
                                   'turn': date_to_turn(request.created_at),
                                   'timestamp': time.mktime(request.created_at.timetuple())})

            events.append({'message': 'Конец «восстановленных» событий, начало полной истории гильдии',
                           'clan': clan,
                           'event': relations.EVENT.TECHNICAL,
                           'tags': (),
                           'attributes': {'clan_id': clan.id},
                           'turn': game_turn.number(),
                           'timestamp': time.time()})

            all_events.extend(events)

        all_events.sort(key=lambda event: event['timestamp'])

        tt_services.chronicle.cmd_debug_clear_service()

        for i, event in enumerate(all_events):
            print('process event {} / {}'.format(i, len(all_events)))
            tt_services.chronicle.cmd_add_event(clan=logic.load_clan(clan_model=event['clan']),
                                                event=event['event'],
                                                tags=event['tags'],
                                                message=event['message'],
                                                attributes=event['attributes'],
                                                turn=event['turn'],
                                                timestamp=event['timestamp'])
