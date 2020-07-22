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

        create_place_and_person(self.logger, x=57, y=50,
                                place_name=lexicon_dictionary.noun(['Оннадуин', 'Оннадуина', 'Оннадуину', 'Оннадуин', 'Оннадуином', 'Оннадуине',
                                                                    'Оннадуины', 'Оннадуинов', 'Оннадуинам', 'Оннадуины', 'Оннадуинами', 'Оннадуинах'],
                                                                   'но,мр').word,
                                person_name=lexicon_dictionary.noun(['Ильфирин', 'Ильфирина', 'Ильфирину', 'Ильфирина', 'Ильфирином', 'Ильфирине',
                                                                     'Ильфирины', 'Ильфиринов', 'Ильфиринам', 'Ильфиринов', 'Ильфиринами', 'Ильфиринах'],
                                                                    'од,мр').word,
                                race=game_relations.RACE.ELF,
                                profession=persons_relations.PERSON_TYPE.MAGICIAN)

        create_place_and_person(self.logger, x=11, y=6,
                                place_name=lexicon_dictionary.noun(['Таур-Анор', 'Таур-Анора', 'Таур-Анору', 'Таур-Анор', 'Таур-Анором', 'Таур-Аноре',
                                                                    'Таур-Аноры', 'Таур-Аноров', 'Таур-Анорам', 'Таур-Аноры', 'Таур-Анорами', 'Таур-Аноров'],
                                                                   'но,мр').word,
                                person_name=lexicon_dictionary.noun(['Кхареян', 'Кхареяна', 'Кхареяну', 'Кхареяна', 'Кхареяном', 'Кхареяне',
                                                                     'Кхареяны', 'Кхареянов', 'Кхареянам', 'Кхареянов', 'Кхареянами', 'Кхареянах'],
                                                                    'од,мр').word,
                                race=game_relations.RACE.ORC,
                                profession=persons_relations.PERSON_TYPE.CARPENTER)

        create_place_and_person(self.logger, x=20, y=2,
                                place_name=lexicon_dictionary.noun(['Силиврэн', 'Силиврэна', 'Силиврэну', 'Силиврэн', 'Силиврэном', 'Силиврэне',
                                                                    'Силиврэны', 'Силиврэнов', 'Силиврэнам', 'Силиврэны', 'Силиврэнами', 'Силиврэнах'],
                                                                   'но,мр').word,
                                person_name=lexicon_dictionary.noun(['Фалгрим', 'Фалгрима', 'Фалгриму', 'Фалгрима', 'Фалгримов', 'Фалгриме',
                                                                     'Фалгримы', 'Фалгримов', 'Фалгримам', 'Фалгримов', 'Фалгримами', 'Фалгримах'],
                                                                    'од,мр').word,
                                race=game_relations.RACE.DWARF,
                                profession=persons_relations.PERSON_TYPE.BLACKSMITH)

        create_place_and_person(self.logger, x=60, y=16,
                                place_name=lexicon_dictionary.noun(['Чулун', 'Чулуна', 'Чулуну', 'Чулун', 'Чулуном', 'Чулуне',
                                                                    'Чулуны', 'Чулунов', 'Чулунам', 'Чулуны', 'Чулунами', 'Чулунах'],
                                                                   'но,мр').word,
                                person_name=lexicon_dictionary.noun(['Озынай', 'Озынай', 'Озынай', 'Озынай', 'Озынай', 'Озынай',
                                                                     'Озынай', 'Озынай', 'Озынай', 'Озынай', 'Озынай', 'Озынай'],
                                                                    'од,жр').word,
                                race=game_relations.RACE.ORC,
                                profession=persons_relations.PERSON_TYPE.MAGICIAN)

        create_place_and_person(self.logger, x=34, y=4,
                                place_name=lexicon_dictionary.noun(['Кострище', 'Кострища', 'Кострищу', 'Кострище', 'Кострищем', 'Кострище',
                                                                    'Кострищи', 'Кострищ', 'Кострищам', 'Кострищи', 'Кострищами', 'Кострищах'],
                                                                   'но,ср').word,
                                person_name=lexicon_dictionary.noun(['Твердивит', 'Твердивита', 'Твердивиту', 'Твердивита', 'Твердивитом', 'Твердивите',
                                                                     'Твердивиты', 'Твердивитов', 'Твердивитам', 'Твердивитов', 'Твердивитами', 'Твердивитах'],
                                                                    'од,мр').word,
                                race=game_relations.RACE.HUMAN,
                                profession=persons_relations.PERSON_TYPE.MAGICIAN)

        create_place_and_person(self.logger, x=14, y=49,
                                place_name=lexicon_dictionary.noun(['Хэйда-Эн', 'Хэйда-Эн', 'Хэйда-Эн', 'Хэйда-Эн', 'Хэйда-Эн', 'Хэйда-Эн',
                                                                    'Хэйда-Эн', 'Хэйда-Эн', 'Хэйда-Эн', 'Хэйда-Эн', 'Хэйда-Эн', 'Хэйда-Эн'],
                                                                   'но,мр').word,
                                person_name=lexicon_dictionary.noun(['Асвальд', 'Асвальда', 'Асвальду', 'Асвальда', 'Асвальдом', 'Асвальде',
                                                                     'Асвальды', 'Асвальдов', 'Асвальдам', 'Асвальдов', 'Асвальдами', 'Асвальдах'],
                                                                    'од,мр').word,
                                race=game_relations.RACE.DWARF,
                                profession=persons_relations.PERSON_TYPE.WARDEN)

        create_place_and_person(self.logger, x=25, y=3,
                                place_name=lexicon_dictionary.noun(['Лирейн', 'Лирейна', 'Лирейну', 'Лирейн', 'Лирейном', 'Лирейне',
                                                                    'Лирейны', 'Лирейнов', 'Лирейнам', 'Лирейны', 'Лирейнами', 'Лирейнах'],
                                                                   'но,мр').word,
                                person_name=lexicon_dictionary.noun(["Сах'Киаран", "Сах'Киарана", "Сах'Киарану", "Сах'Киарана", "Сах'Киараном", "Сах'Киаране",
                                                                     "Сах'Киараны", "Сах'Киаранов", "Сах'Киаранам", "Сах'Киаранов", "Сах'Киаранами", "Сах'Киаранах"],
                                                                    'од,мр').word,
                                race=game_relations.RACE.ELF,
                                profession=persons_relations.PERSON_TYPE.MAGICIAN)

        create_place_and_person(self.logger, x=44, y=56,
                                place_name=lexicon_dictionary.noun(['Кулбобук', 'Кулбобука', 'Кулбобуку', 'Кулбобук', 'Кулбобуком', 'Кулбобуке',
                                                                    'Кулбобуки', 'Кулбобуков', 'Кулбобукам', 'Кулбобуков', 'Кулбобуками', 'Кулбобуках'],
                                                                   'но,мр').word,
                                person_name=lexicon_dictionary.noun(['Рхиир', 'Рхиир', 'Рхиир', 'Рхиир', 'Рхиир', 'Рхиир',
                                                                     'Рхиир', 'Рхиир', 'Рхиир', 'Рхиир', 'Рхиир', 'Рхиир'],
                                                                    'од,жр').word,
                                race=game_relations.RACE.ELF,
                                profession=persons_relations.PERSON_TYPE.ROGUE)

        create_place_and_person(self.logger, x=55, y=12,
                                place_name=lexicon_dictionary.noun(['Мордхейм', 'Мордхейма', 'Мордхейму', 'Мордхейм', 'Мордхеймом', 'Мордхейме',
                                                                    'Мордхеймы', 'Мордхеймов', 'Мордхеймам', 'Мордхеймы', 'Мордхеймами', 'Мордхеймах'],
                                                                   'но,мр').word,
                                person_name=lexicon_dictionary.noun(['Свен', 'Свена', 'Свену', 'Свена', 'Свеном', 'Свене',
                                                                     'Свены', 'Свенов', 'Свенам', 'Свенов', 'Свенами', 'Свенах'],
                                                                    'од,мр').word,
                                race=game_relations.RACE.DWARF,
                                profession=persons_relations.PERSON_TYPE.HUNTER)

        create_place_and_person(self.logger, x=44, y=4,
                                place_name=lexicon_dictionary.noun(['Черноград', 'Чернограда', 'Чернограду', 'Черноград', 'Черноградом', 'Чернограде',
                                                                    'Чернограды', 'Черноградов', 'Черноградам', 'Чернограды', 'Черноградами', 'Черноградах'],
                                                                   'но,мр').word,
                                person_name=lexicon_dictionary.noun(['Всеслав', 'Всеслава', 'Всеславу', 'Всеслава', 'Всеславом', 'Всеславе',
                                                                     'Всеславы', 'Всеславов', 'Всеславам', 'Всеславов', 'Всеславами', 'Всеславах'],
                                                                    'од,мр').word,
                                race=game_relations.RACE.HUMAN,
                                profession=persons_relations.PERSON_TYPE.ROGUE)

        create_place_and_person(self.logger, x=64, y=64,
                                place_name=lexicon_dictionary.noun(['Асиль', 'Асиля', 'Асилю', 'Асиль', 'Асилем', 'Асиле',
                                                                    'Асили', 'Асилей', 'Асилям', 'Асили', 'Асилями', 'Асилях'],
                                                                   'но,мр').word,
                                person_name=lexicon_dictionary.noun(['Ттералл', 'Ттералла', 'Ттераллу', 'Ттералла', 'Ттераллом', 'Ттералле',
                                                                     'Ттераллы', 'Ттераллов', 'Ттераллам', 'Ттераллов', 'Ттераллами', 'Ттераллах'],
                                                                    'од,мр').word,
                                race=game_relations.RACE.ELF,
                                profession=persons_relations.PERSON_TYPE.PRIEST)

        # сдвигаем фронтир
        places_storage.places[47].is_frontier = False
        places_storage.places[37].is_frontier = False
        places_storage.places[49].is_frontier = False
        places_storage.places[46].is_frontier = False

        places_storage.places.save_all()

        game_logic.highlevel_step(logger=self.logger)

        # game_turn.increment() # TODO: remove
        map_generator.update_map(index=map_storage.map_info.item.id + 1)

        # шаблон:
        #
        # create_place_and_person(self.logger, x=, y=,
        #                         place_name=lexicon_dictionary.noun(['', '', '', '', '', '',
        #                                                             '', '', '', '', '', ''],
        #                                                            'но,мр').word,
        #                         person_name=lexicon_dictionary.noun(['', '', '', '', '', '',
        #                                                              '', '', '', '', '', ''],
        #                                                             'од,мр').word,
        #                         race=game_relations.RACE.,
        #                         profession=persons_relations.PERSON_TYPE.)
