# coding: utf-8

from django.core.management.base import BaseCommand
from django.db import transaction

from the_tale.linguistics.lexicon.dictionary import noun

from the_tale.game import relations as game_relations

from the_tale.game.places import storage as places_storage

from the_tale.game.persons import logic
from the_tale.game.persons import relations
from the_tale.game.persons import storage


class Command(BaseCommand):

    help = 'create new masters'

    def handle(self, *args, **options):
        self.create_masters()


    @transaction.atomic
    def create_masters(self):
        logic.create_person(place=places_storage.places[19],
                            race=game_relations.RACE.ELF,
                            gender=game_relations.GENDER.FEMININE,
                            type=relations.PERSON_TYPE.INNKEEPER,
                            utg_name=noun([u'Мирелла', u'Миреллы', u'Мирелле', u'Миреллу', u'Миреллой', u'Мирелле',
                                           u'Миреллы', u'Мирелл', u'Миреллам', u'Мирелл', u'Миреллами', u'Миреллах'], u'од,жр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.FIDGET,
                            personality_practical=relations.PERSONALITY_PRACTICAL.CHARISMATIC)

        logic.create_person(place=places_storage.places[5],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.EXECUTIONER,
                            utg_name=noun([u'Тархан-Сухэ', u'Тархан-Сухэ', u'Тархан-Сухэ', u'Тархан-Сухэ', u'Тархан-Сухэ', u'Тархан-Сухэ',
                                           u'Тархан-Сухэ', u'Тархан-Сухэ', u'Тархан-Сухэ', u'Тархан-Сухэ', u'Тархан-Сухэ', u'Тархан-Сухэ'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.LEADER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.RESPONSIBLE)

        logic.create_person(place=places_storage.places[13],
                            race=game_relations.RACE.GOBLIN,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.ALCHEMIST,
                            utg_name=noun([u'Тиен-Ханьюл', u'Тиен-Ханьюл', u'Тиен-Ханьюл', u'Тиен-Ханьюл', u'Тиен-Ханьюл', u'Тиен-Ханьюл',
                                           u'Тиен-Ханьюл', u'Тиен-Ханьюл', u'Тиен-Ханьюл', u'Тиен-Ханьюл', u'Тиен-Ханьюл', u'Тиен-Ханьюл'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.ORGANIZER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.INSIDIOUS)

        logic.create_person(place=places_storage.places[23],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.FARMER,
                            utg_name=noun([u'Всемил', u'Всемила', u'Всемилу', u'Всемила', u'Всемилом', u'Всемиле',
                                           u'Всемилы', u'Всемилов', u'Всемилам', u'Всемилов', u'Всемилами', u'Всемилах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.HARDWORKING)

        logic.create_person(place=places_storage.places[16],
                            race=game_relations.RACE.DWARF,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.MINER,
                            utg_name=noun([u'Барди', u'Барди', u'Барди', u'Барди', u'Барди', u'Барди',
                                           u'Барди', u'Барди', u'Барди', u'Барди', u'Барди', u'Барди'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.GOOD_SOUL,
                            personality_practical=relations.PERSONALITY_PRACTICAL.DEVOUT)

        logic.create_person(place=places_storage.places[7],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.WARDEN,
                            utg_name=noun([u'Октай', u'Октая', u'Октаю', u'Октая', u'Октаем', u'Октае',
                                           u'Октаи', u'Октаев', u'Октаям', u'Октаев', u'Октаями', u'Октаях'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.LEADER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.INFLUENTIAL)

        logic.create_person(place=places_storage.places[18],
                            race=game_relations.RACE.ELF,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.ROGUE,
                            utg_name=noun([u'Филлуной', u'Филлуноя', u'Филлуною', u'Филлуноя', u'Филлуноем', u'Филлуное',
                                           u'Филлунои', u'Филлуноев', u'Филлуноям', u'Филлуноев', u'Филлунями', u'Филлуноях'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.KNAVE,
                            personality_practical=relations.PERSONALITY_PRACTICAL.REVENGEFUL)

        logic.create_person(place=places_storage.places[5],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.BARD,
                            utg_name=noun([u'Гардасан', u'Гардасана', u'Гардасану', u'Гардасана', u'Гардасаном', u'Гардасане',
                                           u'Гардасаны', u'Гардасанов', u'Гардасанам', u'Гардасанов', u'Гардасанами', u'Гардасанах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.REVENGEFUL)

        logic.create_person(place=places_storage.places[1],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.PRIEST,
                            utg_name=noun([u'Владимир', u'Владимира', u'Владимиру', u'Владимира', u'Владимиром', u'Владимире',
                                           u'Владимиры', u'Владимиров', u'Владимирам', u'Владимиров', u'Владимирами', u'Владимирах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.GOOD_SOUL,
                            personality_practical=relations.PERSONALITY_PRACTICAL.INFLUENTIAL)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.BARD,
                            utg_name=noun([u'Володимир', u'Володимира', u'Володимиру', u'Володимира', u'Володимиром', u'Володимире',
                                           u'Володимиры', u'Володимиров', u'Володимирам', u'Володимиров', u'Володимирами', u'Володимирах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.NIHILIST,
                            personality_practical=relations.PERSONALITY_PRACTICAL.CHARISMATIC)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.DWARF,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.BLACKSMITH,
                            utg_name=noun([u'Хэнлезлок', u'Хэнлезлока', u'Хэнлезлоку', u'Хэнлезлока', u'Хэнлезлоком', u'Хэнлезлоке',
                                           u'Хэнлезлоки', u'Хэнлезлоков', u'Хэнлезлокам', u'Хэнлезлоков', u'Хэнлезлоками', u'Хэнлезлоках'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.HARDWORKING)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.GOBLIN,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.MERCHANT,
                            utg_name=noun([u'Джай-Лу', u'Джай-Лу', u'Джай-Лу', u'Джай-Лу', u'Джай-Лу', u'Джай-Лу',
                                           u'Джай-Лу', u'Джай-Лу', u'Джай-Лу', u'Джай-Лу', u'Джай-Лу', u'Джай-Лу'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.ORGANIZER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ENTERPRISING)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.FEMININE,
                            type=relations.PERSON_TYPE.HERDSMAN,
                            utg_name=noun([u'Дарла', u'Дарлы', u'Дарле', u'Дарлу', u'Дарлой', u'Дарле',
                                           u'Дарлы', u'Дарл', u'Дарлам', u'Дарл', u'Дарлами', u'Дарлах'], u'од,жр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.LEADER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.HARDWORKING)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.ELF,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.ROGUE,
                            utg_name=noun([u'Альсекор', u'Альсекора', u'Альсекору', u'Альсекора', u'Альсекором', u'Альсекоре',
                                           u'Альсекоры', u'Альсекоров', u'Альсекорам', u'Альсекоров', u'Альсекорами', u'Альсекорах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.ORGANIZER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.INFLUENTIAL)

        logic.create_person(place=places_storage.places[27],
                            race=game_relations.RACE.DWARF,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.PRIEST,
                            utg_name=noun([u'Толнир', u'Толнира', u'Толниру', u'Толнира', u'Толниром', u'Толнире',
                                           u'Толниры', u'Толниров', u'Толнирам', u'Толниров', u'Толнирами', u'Толнирах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.GOOD_SOUL,
                            personality_practical=relations.PERSONALITY_PRACTICAL.MULTIWISE)

        logic.create_person(place=places_storage.places[47],
                            race=game_relations.RACE.DWARF,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.WARDEN,
                            utg_name=noun([u'Гульбер', u'Гульбера', u'Гульберу', u'Гульбера', u'Гульбером', u'Гульбере',
                                           u'Гульберы', u'Гульберов', u'Гульберам', u'Гульберов', u'Гульберами', u'Гульберах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.RELIABLE)

        logic.create_person(place=places_storage.places[1],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.PRIEST,
                            utg_name=noun([u'Святослав', u'Святослава', u'Святославу', u'Святослава', u'Святославом', u'Святославе',
                                           u'Святославы', u'Святославов', u'Святославам', u'Святославов', u'Святославами', u'Святославах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.FIDGET,
                            personality_practical=relations.PERSONALITY_PRACTICAL.CHARISMATIC)

        logic.create_person(place=places_storage.places[13],
                            race=game_relations.RACE.GOBLIN,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.MAGOMECHANIC,
                            utg_name=noun([u'Юн-Дус', u'Юн-Дуса', u'Юн-Дусу', u'Юн-Дуса', u'Юн-Дусом', u'Юн-Дусе',
                                           u'Юн-Дусы', u'Юн-Дусов', u'Юн-Дусам', u'Юн-Дусов', u'Юн-Дусами', u'Юн-Дусах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.RECLUSE,
                            personality_practical=relations.PERSONALITY_PRACTICAL.MULTIWISE)

        logic.create_person(place=places_storage.places[9],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.FEMININE,
                            type=relations.PERSON_TYPE.MAGICIAN,
                            utg_name=noun([u'Гро-Здельдлик', u'Гро-Здельдлик', u'Гро-Здельдлик', u'Гро-Здельдлик', u'Гро-Здельдлик', u'Гро-Здельдлик',
                                           u'Гро-Здельдлик', u'Гро-Здельдлик', u'Гро-Здельдлик', u'Гро-Здельдлик', u'Гро-Здельдлик', u'Гро-Здельдлик'], u'од,жр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ORDERLY)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.FEMININE,
                            type=relations.PERSON_TYPE.INNKEEPER,
                            utg_name=noun([u'Любава', u'Любавы', u'Любаве', u'Любаву', u'Любавой', u'Любаве',
                                           u'Любавы', u'Любав', u'Любавам', u'Любав', u'Любавами', u'Любавах'], u'од,жр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.GUARANTOR,
                            personality_practical=relations.PERSONALITY_PRACTICAL.RESPONSIBLE)

        logic.create_person(place=places_storage.places[26],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.HERDSMAN,
                            utg_name=noun([u'Вейгхаз', u'Вейгхаза', u'Вейгхазу', u'Вейгхаза', u'Вейгхазом', u'Вейгхазе',
                                           u'Вейгхазы', u'Вейгхазов', u'Вейгхазам', u'Вейгхазов', u'Вейгхазами', u'Вейгхазах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.RECLUSE,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ACTIVE)

        logic.create_person(place=places_storage.places[22],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.ALCHEMIST,
                            utg_name=noun([u'Берислав', u'Берислава', u'Бериславу', u'Берислава', u'Бериславом', u'Бериславе',
                                           u'Бериславы', u'Бериславов', u'Бериславам', u'Бериславов', u'Бериславами', u'Бериславах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.FIDGET,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ORDERLY)

        logic.create_person(place=places_storage.places[46],
                            race=game_relations.RACE.GOBLIN,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.WARDEN,
                            utg_name=noun([u'Фай-Лах', u'Фай-Лах', u'Фай-Лах', u'Фай-Лах', u'Фай-Лах', u'Фай-Лах',
                                           u'Фай-Лах', u'Фай-Лах', u'Фай-Лах', u'Фай-Лах', u'Фай-Лах', u'Фай-Лах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.FIDGET,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ACTIVE)

        logic.create_person(place=places_storage.places[13],
                            race=game_relations.RACE.ELF,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.PHYSICIAN,
                            utg_name=noun([u'Веларион', u'Велариона', u'Велариону', u'Велариона', u'Веларионом', u'Веларионе',
                                           u'Веларионы', u'Веларионов', u'Веларионам', u'Веларионов', u'Веларионами', u'Веларионах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.GOOD_SOUL,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ORDERLY)


        logic.create_person(place=places_storage.places[16],
                            race=game_relations.RACE.DWARF,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.MAGOMECHANIC,
                            utg_name=noun([u'Фродрун', u'Фродруна', u'Фродруну', u'Фродруна', u'Фродруном', u'Фродруне',
                                           u'Фродруны', u'Фродрунов', u'Фродрунам', u'Фродрунов', u'Фродрунами', u'Фродрунах'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.BULLY,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ROMANTIC)

        logic.create_person(place=places_storage.places[40],
                            race=game_relations.RACE.ELF,
                            gender=game_relations.GENDER.MASCULINE,
                            type=relations.PERSON_TYPE.TAILOR,
                            utg_name=noun([u'Таирвайн', u'Таирвайн', u'Таирвайн', u'Таирвайн', u'Таирвайн', u'Таирвайн',
                                           u'Таирвайн', u'Таирвайн', u'Таирвайн', u'Таирвайн', u'Таирвайн', u'Таирвайн'], u'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.RECLUSE,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ORDERLY)

        def change_personality(id, practical, cosmetic):
            if id in storage.persons:
                storage.persons[id].personality_practical = practical
                storage.persons[id].personality_cosmetic = cosmetic

        change_personality(2966, relations.PERSONALITY_PRACTICAL.ACTIVE, relations.PERSONALITY_COSMETIC.GUARANTOR)
        change_personality(2085, relations.PERSONALITY_PRACTICAL.INFLUENTIAL, relations.PERSONALITY_COSMETIC.LEADER)
        change_personality(2856, relations.PERSONALITY_PRACTICAL.DEVOUT, relations.PERSONALITY_COSMETIC.GOOD_SOUL)

        storage.persons.save_all()
