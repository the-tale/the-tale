
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'clean database'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):
        PostponedTaskPrototype.remove_old_tasks()

        forum_prototypes.ThreadReadInfoPrototype.remove_old_infos()
        forum_prototypes.SubCategoryReadInfoPrototype.remove_old_infos()

        post_service_prototypes.MessagePrototype.remove_old_messages()
