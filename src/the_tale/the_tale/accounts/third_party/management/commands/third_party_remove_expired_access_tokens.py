
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'remove expired acces tokens'

    def handle(self, *args, **options):
        logic.remove_expired_access_tokens()
