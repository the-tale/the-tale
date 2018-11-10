
import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'fill heroes stories'

    def handle(self, *args, **options):
        total_heroes = models.Hero.objects.count()

        print('total heroes: {}'.format(total_heroes))

        for i, hero_id in enumerate(models.Hero.objects.all().order_by('id').values_list('id', flat=True), start=1):
            print('process hero {}/{}'.format(i, total_heroes))

            hero = logic.load_hero(hero_id)

            honor = game_relations.HABIT_HONOR_INTERVAL.LEFT_1

            if hero.habit_honor.raw_value > 0:
                honor = game_relations.HABIT_HONOR_INTERVAL.RIGHT_1

            peacefulness = game_relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_1

            if hero.habit_peacefulness.raw_value > 0:
                peacefulness = game_relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_1

            texts = game_logic.generate_history(name_forms=hero.utg_name.forms[:6],
                                                gender=hero.gender,
                                                race=hero.race,
                                                honor=honor,
                                                peacefulness=peacefulness,
                                                archetype=hero.preferences.archetype,
                                                upbringing=hero.upbringing,
                                                first_death=hero.first_death,
                                                age=hero.death_age)

            logic.set_hero_description(hero.id, '\n\n'.join('[rl]' + text for text in texts if text).strip())
