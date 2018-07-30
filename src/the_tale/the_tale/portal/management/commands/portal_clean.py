
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'clean database'

    def handle(self, *args, **options):
        PostponedTaskPrototype.remove_old_tasks()

        forum_prototypes.ThreadReadInfoPrototype.remove_old_infos()
        forum_prototypes.SubCategoryReadInfoPrototype.remove_old_infos()

        post_service_prototypes.MessagePrototype.remove_old_messages()
