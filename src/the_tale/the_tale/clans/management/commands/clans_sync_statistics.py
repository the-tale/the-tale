
import smart_imports

smart_imports.all()


def date_to_turn(date):
    turn = game_turn.number()
    now = datetime.datetime.now()

    return int(turn - (now - date).total_seconds() / 10)


class Command(utilities_base.Command):

    help = 'sync clans statistics'

    LOCKS = ['game_commands']

    def _handle(self, *args, **options):
        for clan_model in models.Clan.objects.all().iterator():
            clan = logic.load_clan(clan_model=clan_model)
            logic.sync_clan_statistics(clan)
