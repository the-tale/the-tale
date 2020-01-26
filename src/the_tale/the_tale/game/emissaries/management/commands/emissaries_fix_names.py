
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'Do one emissary calculation step'

    def handle(self, *args, **options):
        for emissary in storage.emissaries.all():
            if emissary.gender.utg_id == emissary.utg_name.properties.get(utg_relations.GENDER):
                continue

            print(f'fix name for emissary {emissary.id}')

            game_names.sync_properties(emissary.utg_name, emissary.gender)

            logic.save_emissary(emissary)
