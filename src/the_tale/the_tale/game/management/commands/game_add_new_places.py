import smart_imports

smart_imports.all()


def create_place_and_person(logger, x,
                            y,
                            place_name,
                            person_name,
                            race,
                            profession=None,
                            personality_cosmetic=None,
                            personality_practical=None,
                            size=1,
                            is_frontier=True):

    if places_storage.places.get_by_coordinates(x, y) is not None:
        logger.info(f'place at {x, y} already created')
        return

    if profession is None:
        profession = persons_relations.PERSON_TYPE.random()

    if personality_cosmetic is None:
        personality_cosmetic = persons_relations.PERSONALITY_COSMETIC.random()

    if personality_practical is None:
        personality_practical = persons_relations.PERSONALITY_PRACTICAL.random()

    place = places_logic.create_place(x=x,
                                      y=y,
                                      size=size,
                                      utg_name=place_name,
                                      race=race,
                                      is_frontier=is_frontier)

    persons_logic.create_person(place=place,
                                race=race,
                                type=profession,
                                utg_name=person_name,
                                gender=game_relations.GENDER.index_utg_id[person_name.properties.get(utg_relations.GENDER)],
                                personality_cosmetic=personality_cosmetic,
                                personality_practical=personality_practical)

    politic_power_storage.places.reset()
    politic_power_storage.persons.reset()

    place.refresh_attributes()
    places_logic.save_place(place)

    logger.info(f'place at {x, y} created')


class Command(utilities_base.Command):

    help = 'add new places, described in CODE'

    LOCKS = ['game_commands']

    GAME_MUST_BE_STOPPED = True

    @django_transaction.atomic
    def _handle(self, *args, **options):

        # https://the-tale.org/folklore/posts/1113
        create_place_and_person(self.logger, x=49, y=7,
                                place_name=lexicon_dictionary.noun(['Теалор', 'Теалора', 'Теалору', 'Теалор', 'Теалором', 'Теалоре',
                                                                    'Теалоры', 'Теалоров', 'Теалорам', 'Теалоров', 'Теалорами', 'Теалорах'],
                                                                    'но,мр').word,
                                person_name=lexicon_dictionary.noun(['Любомудр', 'Любомудра', 'Любомудру', 'Любомудра', 'Любомудром', 'Любомудре',
                                                                     'Любомудры', 'Любомудров', 'Любомудрам', 'Любомудров', 'Любомудрами', 'Любомудрах'],
                                                                     'од,мр').word,
                                race=game_relations.RACE.HUMAN,
                                profession=persons_relations.PERSON_TYPE.PHYSICIAN,
                                personality_practical=persons_relations.PERSONALITY_PRACTICAL.ACTIVE)

        # https://the-tale.org/folklore/posts/1097
        create_place_and_person(self.logger, x=39, y=1,
                                place_name=lexicon_dictionary.noun(['Миориель', 'Миориеля', 'Миориелю', 'Миориель', 'Миориелем', 'Миориеле',
                                                                    'Миориели', 'Миориелей', 'Миориелям', 'Миориели', 'Миориелями', 'Миориелях'],
                                                                   'но,мр').word,
                                person_name=lexicon_dictionary.noun(['Ронборг', 'Ронборга', 'Ронборгу', 'Ронборг', 'Ронборгом', 'Ронборге',
                                                                     'Ронборги', 'Ронборгов', 'Ронборгам', 'Ронборгов', 'Ронборгами', 'Ронборгах'],
                                                                    'од,мр').word,
                                race=game_relations.RACE.HUMAN,
                                profession=persons_relations.PERSON_TYPE.MAGOMECHANIC,
                                personality_practical=persons_relations.PERSONALITY_PRACTICAL.INFLUENTIAL)

        # сдвигаем фронтир
        # places_storage.places[?].is_frontier = False

        places_storage.places.update_version()
        persons_storage.persons.update_version()

        places_storage.places.save_all()
        persons_storage.persons.save_all()

        game_logic.highlevel_step(logger=self.logger)

        map_generator.update_map(index=map_storage.map_info.item.id + 1)
