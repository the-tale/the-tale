
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'block expired accounts. MUST run only if game stopped'

    requires_model_validation = False

    def handle(self, *args, **options):

        for proc in psutil.process_iter():
            try:
                process_cmdline = ' '.join(proc.cmdline())

                if 'django-admin' in process_cmdline and 'supervisor' in process_cmdline and 'the-tale' in process_cmdline:
                    print('game MUST be stopped befor run this command')
                    return
            except psutil.NoSuchProcess:
                pass

        logic.block_expired_accounts(logging.getLogger('the-tale'))
