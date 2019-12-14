import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    def handle(self, *args, **options):

        from the_tale.game.places import storage as p_storage
        from the_tale.game.places import relations as p_relations
        from the_tale.game.map import storage as m_storage

        p = p_storage.places[18]

        print(p.attrs.production)

        # pprint.pprint(p.tooltip_effects_for_attribute(p_relations.ATTRIBUTE.PRODUCTION))

        p.refresh_attributes()

        print(p.attrs.production)
