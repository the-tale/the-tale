import smart_imports

smart_imports.all()


class Command(django_management.BaseCommand):

    help = 'add new places, described in CODE'

    @django_transaction.atomic
    def handle(self, *args, **options):

        place = places_logic.create_place(x=29,
                                          y=6,
                                          size=1,
                                          utg_name=lexicon_dictionary.noun(['Родрог', 'Родрога', 'Родрогу', 'Родрог', 'Родрогом', 'Родроге',
                                                                            'Родроги', 'Родрогов', 'Родрогам', 'Родрогов', 'Родрогами', 'Родрогах'],
                                                                           'но,мр').word,
                                          race=game_relations.RACE.HUMAN,
                                          is_frontier=True)

        persons_logic.create_person(place=place,
                                    race=game_relations.RACE.HUMAN,
                                    type=persons_relations.PERSON_TYPE.WARDEN,
                                    utg_name=lexicon_dictionary.noun(['Эргонд', 'Эргонда', 'Эргонду', 'Эргонда', 'Эргондом', 'Эргонде',
                                                                      'Эргонды', 'Эргондов', 'Эргондам', 'Эргондов', 'Эргондами', 'Эргондах'],
                                                                      'од,мр').word,
                                    gender=game_relations.GENDER.MALE,
                                    personality_cosmetic=persons_relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                                    personality_practical=persons_relations.PERSONALITY_PRACTICAL.ACTIVE)

        place.refresh_attributes()
        places_logic.save_place(place)

        map_generator.update_map(index=map_storage.map_info.item.id + 1)
