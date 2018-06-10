
from django.core.management.base import BaseCommand

from dext.common.utils.logic import run_django_command

from the_tale.game import relations

from the_tale.game.places import storage as places_storage
from the_tale.game.places import logic as places_logic

from the_tale.game.persons import logic as persons_logic
from the_tale.game.persons import relations as persons_relations

from the_tale.game.roads import prototypes as roads_prototypes

from the_tale.linguistics.lexicon import dictionary


class Command(BaseCommand):

    help = 'create new places'

    def handle(self, *args, **options):

        places_storage.places[52].is_frontier = False
        places_storage.places[48].is_frontier = False

        place = places_logic.create_place(x=49,
                                          y=49,
                                          size=1,
                                          utg_name=dictionary.noun(['Киралода', 'Киралоды', 'Киралоде', 'Киралоду', 'Киралодой', 'Киралоде',
                                                                    'Киралоды', 'Киралод', 'Киралодам', 'Киралоды', 'Киралодами', 'Киралодах'], 'но,жр').word,
                                          race=relations.RACE.ELF,
                                          is_frontier=True)

        persons_logic.create_person(place=place,
                                    race=relations.RACE.ELF,
                                    gender=relations.GENDER.FEMALE,
                                    type=persons_relations.PERSON_TYPE.MAGICIAN,
                                    personality_cosmetic=persons_relations.PERSONALITY_COSMETIC.GUARANTOR,
                                    personality_practical=persons_relations.PERSONALITY_PRACTICAL.RELIABLE,
                                    utg_name=dictionary.noun(['Оуримм', 'Оуримм', 'Оуримм', 'Оуримм', 'Оуримм', 'Оуримм',
                                                              'Оуриммы', 'Оуримм', 'Оуриммам', 'Оуримм', 'Оуриммами', 'Оуриммах'], 'од,жр').word)

        roads_prototypes.RoadPrototype.create(point_1=place, point_2=places_storage.places[52]).update()

        for place in places_storage.places.all():
            place.refresh_attributes()

        places_storage.places.save_all()

        run_django_command(['map_update_map'])
