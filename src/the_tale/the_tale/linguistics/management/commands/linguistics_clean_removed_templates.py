
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'clean removed templates'

    LOCKS = ['portal_commands']

    def _handle(self, *args, **options):

        time_border = datetime.datetime.now() - datetime.timedelta(days=conf.settings.REMOVED_TEMPLATE_TIMEOUT)

        for template_model in prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.REMOVED,
                                                                      updated_at__lt=time_border):
            logic.full_remove_template(prototypes.TemplatePrototype(template_model))
