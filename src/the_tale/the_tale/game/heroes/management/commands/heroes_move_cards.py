
import uuid

from django.core.management.base import BaseCommand

from dext.common.utils import s11n

from the_tale.game.cards import objects as cards_objects

from the_tale.game.heroes import models
from the_tale.game.heroes import relations
from the_tale.game.cards import tt_api as cards_tt_api

from the_tale.game import relations as game_relations


OLD_SPENDINGS_CARDS_TO_SPENDINGS = {40: relations.ITEMS_OF_EXPENDITURE.INSTANT_HEAL,
                                    41: relations.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT,
                                    42: relations.ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT,
                                    43: relations.ITEMS_OF_EXPENDITURE.EXPERIENCE,
                                    44: relations.ITEMS_OF_EXPENDITURE.REPAIRING_ARTIFACT,
                                    105: relations.ITEMS_OF_EXPENDITURE.HEAL_COMPANION}


OLD_PREFERENCE_CARDS_TO_PREFERENCES = {29: relations.PREFERENCE_TYPE.MOB,
                                       30: relations.PREFERENCE_TYPE.PLACE,
                                       31: relations.PREFERENCE_TYPE.FRIEND,
                                       32: relations.PREFERENCE_TYPE.ENEMY,
                                       33: relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE,
                                       34: relations.PREFERENCE_TYPE.EQUIPMENT_SLOT,
                                       35: relations.PREFERENCE_TYPE.RISK_LEVEL,
                                       36: relations.PREFERENCE_TYPE.FAVORITE_ITEM,
                                       37: relations.PREFERENCE_TYPE.ARCHETYPE,
                                       95: relations.PREFERENCE_TYPE.COMPANION_DEDICATION,
                                       96: relations.PREFERENCE_TYPE.COMPANION_EMPATHY}


OLD_HABIT_UNCOMMON_TO_HABITS = {13: (game_relations.HABIT_TYPE.HONOR, 1),
                                14: (game_relations.HABIT_TYPE.HONOR, -1),
                                15: (game_relations.HABIT_TYPE.PEACEFULNESS, 1),
                                16: (game_relations.HABIT_TYPE.PEACEFULNESS, -1)}

OLD_HABIT_RARE_TO_HABITS = {17: (game_relations.HABIT_TYPE.HONOR, 1),
                            18: (game_relations.HABIT_TYPE.HONOR, -1),
                            19: (game_relations.HABIT_TYPE.PEACEFULNESS, 1),
                            20: (game_relations.HABIT_TYPE.PEACEFULNESS, -1)}

OLD_HABIT_EPIC_TO_HABITS = {21: (game_relations.HABIT_TYPE.HONOR, 1),
                            22: (game_relations.HABIT_TYPE.HONOR, -1),
                            23: (game_relations.HABIT_TYPE.PEACEFULNESS, 1),
                            24: (game_relations.HABIT_TYPE.PEACEFULNESS, -1)}

OLD_HABIT_LEGENDARY_TO_HABITS = {25: (game_relations.HABIT_TYPE.HONOR, 1),
                                 26: (game_relations.HABIT_TYPE.HONOR, -1),
                                 27: (game_relations.HABIT_TYPE.PEACEFULNESS, 1),
                                 28: (game_relations.HABIT_TYPE.PEACEFULNESS, -1)}

OLD_PERSON_POWER_TO_PERSON_POWER_COMMON = {108: 1, 111: -1}
OLD_PERSON_POWER_TO_PERSON_POWER_UNCOMMON = {58: 1,112: -1}
OLD_PERSON_POWER_TO_PERSON_POWER_RARE = {59: 1, 113: -1}
OLD_PERSON_POWER_TO_PERSON_POWER_EPIC = {60: 1, 114: -1}
OLD_PERSON_POWER_TO_PERSON_POWER_LEGENDARY = {61: 1, 115: -1}

OLD_PLACE_POWER_TO_PLACE_POWER_COMMON = {109: 1, 110: -1}
OLD_PLACE_POWER_TO_PLACE_POWER_UNCOMMON = {62: 1, 66: -1}
OLD_PLACE_POWER_TO_PLACE_POWER_RARE = {63: 1, 67: -1}
OLD_PLACE_POWER_TO_PLACE_POWER_EPIC = {64: 1, 68: -1}
OLD_PLACE_POWER_TO_PLACE_POWER_LEGENDARY = {65: 1, 69: -1}

OLD_EXPERIENCE_TO_ENERGY = {84: 6,
                            85: 7,
                            86: 8,
                            87: 9}

def transform_card(data):
    old_type = data['type']

    if old_type in OLD_SPENDINGS_CARDS_TO_SPENDINGS:
        data['type'] = 116
        data['data'] = {'item_id': OLD_SPENDINGS_CARDS_TO_SPENDINGS[old_type].value}

    if old_type in OLD_PREFERENCE_CARDS_TO_PREFERENCES:
        data['type'] = 117
        data['data'] = {'preference_id': OLD_PREFERENCE_CARDS_TO_PREFERENCES[old_type].value}

    if old_type in OLD_HABIT_UNCOMMON_TO_HABITS:
        habit, direction = OLD_HABIT_UNCOMMON_TO_HABITS[old_type]
        data['type'] = 119
        data['data'] = {'habit_id': habit.value, 'direction': direction}

    if old_type in OLD_HABIT_RARE_TO_HABITS:
        habit, direction = OLD_HABIT_RARE_TO_HABITS[old_type]
        data['type'] = 120
        data['data'] = {'habit_id': habit.value, 'direction': direction}

    if old_type in OLD_HABIT_EPIC_TO_HABITS:
        habit, direction = OLD_HABIT_EPIC_TO_HABITS[old_type]
        data['type'] = 121
        data['data'] = {'habit_id': habit.value, 'direction': direction}

    if old_type in OLD_HABIT_LEGENDARY_TO_HABITS:
        habit, direction = OLD_HABIT_LEGENDARY_TO_HABITS[old_type]
        data['type'] = 122
        data['data'] = {'habit_id': habit.value, 'direction': direction}

    if old_type in OLD_PERSON_POWER_TO_PERSON_POWER_COMMON:
        data['type'] = 123
        data['data'] = {'direction': OLD_PERSON_POWER_TO_PERSON_POWER_COMMON[old_type]}

    if old_type in OLD_PERSON_POWER_TO_PERSON_POWER_UNCOMMON:
        data['type'] = 124
        data['data'] = {'direction': OLD_PERSON_POWER_TO_PERSON_POWER_UNCOMMON[old_type]}

    if old_type in OLD_PERSON_POWER_TO_PERSON_POWER_RARE:
        data['type'] = 125
        data['data'] = {'direction': OLD_PERSON_POWER_TO_PERSON_POWER_RARE[old_type]}

    if old_type in OLD_PERSON_POWER_TO_PERSON_POWER_EPIC:
        data['type'] = 126
        data['data'] = {'direction': OLD_PERSON_POWER_TO_PERSON_POWER_EPIC[old_type]}

    if old_type in OLD_PERSON_POWER_TO_PERSON_POWER_LEGENDARY:
        data['type'] = 127
        data['data'] = {'direction': OLD_PERSON_POWER_TO_PERSON_POWER_LEGENDARY[old_type]}

    if old_type in OLD_PLACE_POWER_TO_PLACE_POWER_COMMON:
        data['type'] = 128
        data['data'] = {'direction': OLD_PLACE_POWER_TO_PLACE_POWER_COMMON[old_type]}

    if old_type in OLD_PLACE_POWER_TO_PLACE_POWER_UNCOMMON:
        data['type'] = 129
        data['data'] = {'direction': OLD_PLACE_POWER_TO_PLACE_POWER_UNCOMMON[old_type]}

    if old_type in OLD_PLACE_POWER_TO_PLACE_POWER_RARE:
        data['type'] = 130
        data['data'] = {'direction': OLD_PLACE_POWER_TO_PLACE_POWER_RARE[old_type]}

    if old_type in OLD_PLACE_POWER_TO_PLACE_POWER_EPIC:
        data['type'] = 131
        data['data'] = {'direction': OLD_PLACE_POWER_TO_PLACE_POWER_EPIC[old_type]}

    if old_type in OLD_PLACE_POWER_TO_PLACE_POWER_LEGENDARY:
        data['type'] = 132
        data['data'] = {'direction': OLD_PLACE_POWER_TO_PLACE_POWER_LEGENDARY[old_type]}

    if old_type in OLD_EXPERIENCE_TO_ENERGY:
        data['type'] = OLD_EXPERIENCE_TO_ENERGY[old_type]

    if old_type == 104:
        data['type'] = 9

    return data


class Command(BaseCommand):

    help = 'move cards from heroes models to tt_storage'

    def handle(self, *args, **options):

        print('start heroes processing')

        for hero in models.Hero.objects.all().order_by('id').iterator():
            print(hero.id)

            cards_data = s11n.from_json(hero.cards)

            data = s11n.from_json(hero.data)
            data['cards'] = {'help_count': cards_data['help_count'],
                             'premium_help_count': cards_data['premium_help_count']}
            hero.data = s11n.to_json(data)
            hero.cards = ''

            cards = []

            for card_data in cards_data['cards']:

                if card_data['type'] == 38:
                    for i in range(0, 11):
                        cards.append(cards_objects.Card.deserialize(uuid.uuid4(), {'type': 117,
                                                                                   'auction': card_data['auction'],
                                                                                   'data': {'preference_id': i}}))
                    continue

                card_data = transform_card(card_data)
                cards.append(cards_objects.Card.deserialize(uuid.uuid4(), card_data))

            cards_tt_api.change_cards(account_id=hero.id, operation_type='initial-import', to_add=cards)

            hero.save()
