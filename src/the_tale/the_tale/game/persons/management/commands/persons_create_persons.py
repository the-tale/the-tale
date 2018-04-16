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
                            gender=game_relations.GENDER.FEMALE,
                            type=relations.PERSON_TYPE.INNKEEPER,
                            utg_name=noun(['Мирелла', 'Миреллы', 'Мирелле', 'Миреллу', 'Миреллой', 'Мирелле',
                                           'Миреллы', 'Мирелл', 'Миреллам', 'Мирелл', 'Миреллами', 'Миреллах'], 'од,жр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.FIDGET,
                            personality_practical=relations.PERSONALITY_PRACTICAL.CHARISMATIC)

        logic.create_person(place=places_storage.places[5],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.EXECUTIONER,
                            utg_name=noun(['Тархан-Сухэ', 'Тархан-Сухэ', 'Тархан-Сухэ', 'Тархан-Сухэ', 'Тархан-Сухэ', 'Тархан-Сухэ',
                                           'Тархан-Сухэ', 'Тархан-Сухэ', 'Тархан-Сухэ', 'Тархан-Сухэ', 'Тархан-Сухэ', 'Тархан-Сухэ'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.LEADER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.RESPONSIBLE)

        logic.create_person(place=places_storage.places[13],
                            race=game_relations.RACE.GOBLIN,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.ALCHEMIST,
                            utg_name=noun(['Тиен-Ханьюл', 'Тиен-Ханьюл', 'Тиен-Ханьюл', 'Тиен-Ханьюл', 'Тиен-Ханьюл', 'Тиен-Ханьюл',
                                           'Тиен-Ханьюл', 'Тиен-Ханьюл', 'Тиен-Ханьюл', 'Тиен-Ханьюл', 'Тиен-Ханьюл', 'Тиен-Ханьюл'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.ORGANIZER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.INSIDIOUS)

        logic.create_person(place=places_storage.places[23],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.FARMER,
                            utg_name=noun(['Всемил', 'Всемила', 'Всемилу', 'Всемила', 'Всемилом', 'Всемиле',
                                           'Всемилы', 'Всемилов', 'Всемилам', 'Всемилов', 'Всемилами', 'Всемилах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.HARDWORKING)

        logic.create_person(place=places_storage.places[16],
                            race=game_relations.RACE.DWARF,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.MINER,
                            utg_name=noun(['Барди', 'Барди', 'Барди', 'Барди', 'Барди', 'Барди',
                                           'Барди', 'Барди', 'Барди', 'Барди', 'Барди', 'Барди'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.GOOD_SOUL,
                            personality_practical=relations.PERSONALITY_PRACTICAL.DEVOUT)

        logic.create_person(place=places_storage.places[7],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.WARDEN,
                            utg_name=noun(['Октай', 'Октая', 'Октаю', 'Октая', 'Октаем', 'Октае',
                                           'Октаи', 'Октаев', 'Октаям', 'Октаев', 'Октаями', 'Октаях'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.LEADER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.INFLUENTIAL)

        logic.create_person(place=places_storage.places[18],
                            race=game_relations.RACE.ELF,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.ROGUE,
                            utg_name=noun(['Филлуной', 'Филлуноя', 'Филлуною', 'Филлуноя', 'Филлуноем', 'Филлуное',
                                           'Филлунои', 'Филлуноев', 'Филлуноям', 'Филлуноев', 'Филлунями', 'Филлуноях'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.KNAVE,
                            personality_practical=relations.PERSONALITY_PRACTICAL.REVENGEFUL)

        logic.create_person(place=places_storage.places[5],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.BARD,
                            utg_name=noun(['Гардасан', 'Гардасана', 'Гардасану', 'Гардасана', 'Гардасаном', 'Гардасане',
                                           'Гардасаны', 'Гардасанов', 'Гардасанам', 'Гардасанов', 'Гардасанами', 'Гардасанах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.REVENGEFUL)

        logic.create_person(place=places_storage.places[1],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.PRIEST,
                            utg_name=noun(['Владимир', 'Владимира', 'Владимиру', 'Владимира', 'Владимиром', 'Владимире',
                                           'Владимиры', 'Владимиров', 'Владимирам', 'Владимиров', 'Владимирами', 'Владимирах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.GOOD_SOUL,
                            personality_practical=relations.PERSONALITY_PRACTICAL.INFLUENTIAL)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.BARD,
                            utg_name=noun(['Володимир', 'Володимира', 'Володимиру', 'Володимира', 'Володимиром', 'Володимире',
                                           'Володимиры', 'Володимиров', 'Володимирам', 'Володимиров', 'Володимирами', 'Володимирах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.NIHILIST,
                            personality_practical=relations.PERSONALITY_PRACTICAL.CHARISMATIC)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.DWARF,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.BLACKSMITH,
                            utg_name=noun(['Хэнлезлок', 'Хэнлезлока', 'Хэнлезлоку', 'Хэнлезлока', 'Хэнлезлоком', 'Хэнлезлоке',
                                           'Хэнлезлоки', 'Хэнлезлоков', 'Хэнлезлокам', 'Хэнлезлоков', 'Хэнлезлоками', 'Хэнлезлоках'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.HARDWORKING)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.GOBLIN,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.MERCHANT,
                            utg_name=noun(['Джай-Лу', 'Джай-Лу', 'Джай-Лу', 'Джай-Лу', 'Джай-Лу', 'Джай-Лу',
                                           'Джай-Лу', 'Джай-Лу', 'Джай-Лу', 'Джай-Лу', 'Джай-Лу', 'Джай-Лу'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.ORGANIZER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ENTERPRISING)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.FEMALE,
                            type=relations.PERSON_TYPE.HERDSMAN,
                            utg_name=noun(['Дарла', 'Дарлы', 'Дарле', 'Дарлу', 'Дарлой', 'Дарле',
                                           'Дарлы', 'Дарл', 'Дарлам', 'Дарл', 'Дарлами', 'Дарлах'], 'од,жр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.LEADER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.HARDWORKING)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.ELF,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.ROGUE,
                            utg_name=noun(['Альсекор', 'Альсекора', 'Альсекору', 'Альсекора', 'Альсекором', 'Альсекоре',
                                           'Альсекоры', 'Альсекоров', 'Альсекорам', 'Альсекоров', 'Альсекорами', 'Альсекорах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.ORGANIZER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.INFLUENTIAL)

        logic.create_person(place=places_storage.places[27],
                            race=game_relations.RACE.DWARF,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.PRIEST,
                            utg_name=noun(['Толнир', 'Толнира', 'Толниру', 'Толнира', 'Толниром', 'Толнире',
                                           'Толниры', 'Толниров', 'Толнирам', 'Толниров', 'Толнирами', 'Толнирах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.GOOD_SOUL,
                            personality_practical=relations.PERSONALITY_PRACTICAL.MULTIWISE)

        logic.create_person(place=places_storage.places[47],
                            race=game_relations.RACE.DWARF,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.WARDEN,
                            utg_name=noun(['Гульбер', 'Гульбера', 'Гульберу', 'Гульбера', 'Гульбером', 'Гульбере',
                                           'Гульберы', 'Гульберов', 'Гульберам', 'Гульберов', 'Гульберами', 'Гульберах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.RELIABLE)

        logic.create_person(place=places_storage.places[1],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.PRIEST,
                            utg_name=noun(['Святослав', 'Святослава', 'Святославу', 'Святослава', 'Святославом', 'Святославе',
                                           'Святославы', 'Святославов', 'Святославам', 'Святославов', 'Святославами', 'Святославах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.FIDGET,
                            personality_practical=relations.PERSONALITY_PRACTICAL.CHARISMATIC)

        logic.create_person(place=places_storage.places[13],
                            race=game_relations.RACE.GOBLIN,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.MAGOMECHANIC,
                            utg_name=noun(['Юн-Дус', 'Юн-Дуса', 'Юн-Дусу', 'Юн-Дуса', 'Юн-Дусом', 'Юн-Дусе',
                                           'Юн-Дусы', 'Юн-Дусов', 'Юн-Дусам', 'Юн-Дусов', 'Юн-Дусами', 'Юн-Дусах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.RECLUSE,
                            personality_practical=relations.PERSONALITY_PRACTICAL.MULTIWISE)

        logic.create_person(place=places_storage.places[9],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.FEMALE,
                            type=relations.PERSON_TYPE.MAGICIAN,
                            utg_name=noun(['Гро-Здельдлик', 'Гро-Здельдлик', 'Гро-Здельдлик', 'Гро-Здельдлик', 'Гро-Здельдлик', 'Гро-Здельдлик',
                                           'Гро-Здельдлик', 'Гро-Здельдлик', 'Гро-Здельдлик', 'Гро-Здельдлик', 'Гро-Здельдлик', 'Гро-Здельдлик'], 'од,жр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ORDERLY)

        logic.create_person(place=places_storage.places[45],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.FEMALE,
                            type=relations.PERSON_TYPE.INNKEEPER,
                            utg_name=noun(['Любава', 'Любавы', 'Любаве', 'Любаву', 'Любавой', 'Любаве',
                                           'Любавы', 'Любав', 'Любавам', 'Любав', 'Любавами', 'Любавах'], 'од,жр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.GUARANTOR,
                            personality_practical=relations.PERSONALITY_PRACTICAL.RESPONSIBLE)

        logic.create_person(place=places_storage.places[26],
                            race=game_relations.RACE.ORC,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.HERDSMAN,
                            utg_name=noun(['Вейгхаз', 'Вейгхаза', 'Вейгхазу', 'Вейгхаза', 'Вейгхазом', 'Вейгхазе',
                                           'Вейгхазы', 'Вейгхазов', 'Вейгхазам', 'Вейгхазов', 'Вейгхазами', 'Вейгхазах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.RECLUSE,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ACTIVE)

        logic.create_person(place=places_storage.places[22],
                            race=game_relations.RACE.HUMAN,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.ALCHEMIST,
                            utg_name=noun(['Берислав', 'Берислава', 'Бериславу', 'Берислава', 'Бериславом', 'Бериславе',
                                           'Бериславы', 'Бериславов', 'Бериславам', 'Бериславов', 'Бериславами', 'Бериславах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.FIDGET,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ORDERLY)

        logic.create_person(place=places_storage.places[46],
                            race=game_relations.RACE.GOBLIN,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.WARDEN,
                            utg_name=noun(['Фай-Лах', 'Фай-Лах', 'Фай-Лах', 'Фай-Лах', 'Фай-Лах', 'Фай-Лах',
                                           'Фай-Лах', 'Фай-Лах', 'Фай-Лах', 'Фай-Лах', 'Фай-Лах', 'Фай-Лах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.FIDGET,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ACTIVE)

        logic.create_person(place=places_storage.places[13],
                            race=game_relations.RACE.ELF,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.PHYSICIAN,
                            utg_name=noun(['Веларион', 'Велариона', 'Велариону', 'Велариона', 'Веларионом', 'Веларионе',
                                           'Веларионы', 'Веларионов', 'Веларионам', 'Веларионов', 'Веларионами', 'Веларионах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.GOOD_SOUL,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ORDERLY)


        logic.create_person(place=places_storage.places[16],
                            race=game_relations.RACE.DWARF,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.MAGOMECHANIC,
                            utg_name=noun(['Фродрун', 'Фродруна', 'Фродруну', 'Фродруна', 'Фродруном', 'Фродруне',
                                           'Фродруны', 'Фродрунов', 'Фродрунам', 'Фродрунов', 'Фродрунами', 'Фродрунах'], 'од,мр').word,
                            personality_cosmetic=relations.PERSONALITY_COSMETIC.BULLY,
                            personality_practical=relations.PERSONALITY_PRACTICAL.ROMANTIC)

        logic.create_person(place=places_storage.places[40],
                            race=game_relations.RACE.ELF,
                            gender=game_relations.GENDER.MALE,
                            type=relations.PERSON_TYPE.TAILOR,
                            utg_name=noun(['Таирвайн', 'Таирвайн', 'Таирвайн', 'Таирвайн', 'Таирвайн', 'Таирвайн',
                                           'Таирвайн', 'Таирвайн', 'Таирвайн', 'Таирвайн', 'Таирвайн', 'Таирвайн'], 'од,мр').word,
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
