
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'Recalculate mights of accounts'

    def handle(self, *args, **options):
        might.recalculate_accounts_might()
