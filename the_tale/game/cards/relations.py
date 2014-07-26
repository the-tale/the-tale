# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.cards import forms


class RARITY(DjangoEnum):
    probability = Column()

    records = ( ('COMMON', 0, u'обычная', 3**4),
                ('UNCOMMON', 1, u'необычная', 3**3),
                ('RARE', 3, u'редкая', 3**2),
                ('EPIC', 4, u'эпическая', 3**1),
                ('LEGENDARY', 5, u'легендарная', 3**0) )

class CARD_TYPE(DjangoEnum):
    rarity = Column(unique=False)
    form = Column(unique=False, primary=False, single_type=False)

    records = ( ('LEVEL_UP', 1, u'?увеличить уровень', RARITY.LEGENDARY, forms.EmptyForm,),

                ('ADD_BONUS_ENERGY_COMMON', 5, u'?добавить энергию 1', RARITY.COMMON, forms.EmptyForm,),
                ('ADD_BONUS_ENERGY_UNCOMMON', 6, u'?добавить энергию 2', RARITY.UNCOMMON, forms.EmptyForm,),
                ('ADD_BONUS_ENERGY_RARE', 7, u'?добавить энергию 3', RARITY.RARE, forms.EmptyForm,),
                ('ADD_BONUS_ENERGY_EPIC', 8, u'?добавить энергию 4', RARITY.EPIC, forms.EmptyForm,),
                ('ADD_BONUS_ENERGY_LEGENDARY', 9, u'?добавить энергию 5', RARITY.LEGENDARY, forms.EmptyForm,),

                ('ADD_GOLD_COMMON', 10, u'?добавить золото 1', RARITY.COMMON, forms.EmptyForm,),
                ('ADD_GOLD_UNCOMMON', 11, u'?добавить золото 2', RARITY.UNCOMMON, forms.EmptyForm,),
                ('ADD_GOLD_RARE', 12, u'?добавить золото 3', RARITY.RARE, forms.EmptyForm,),

                ('CHANGE_HABIT_HONOR_PLUS_UNCOMMON', 13, u'?изменить честь плюс 1', RARITY.UNCOMMON, forms.EmptyForm,),
                ('CHANGE_HABIT_HONOR_MINUS_UNCOMMON', 14, u'?изменить честь минус 1', RARITY.UNCOMMON, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_UNCOMMON', 15, u'?изменить миролюбие плюс 1', RARITY.UNCOMMON, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_UNCOMMON', 16, u'?изменить миролюбие минус 1', RARITY.UNCOMMON, forms.EmptyForm,),

                ('CHANGE_HABIT_HONOR_PLUS_RARE', 17, u'?изменить честь плюс 2', RARITY.RARE, forms.EmptyForm,),
                ('CHANGE_HABIT_HONOR_MINUS_RARE', 18, u'?изменить честь минус 2', RARITY.RARE, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_RARE', 19, u'?изменить миролюбие плюс 2', RARITY.RARE, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_RARE', 20, u'?изменить миролюбие минус 2', RARITY.RARE, forms.EmptyForm,),

                ('CHANGE_HABIT_HONOR_PLUS_EPIC', 21, u'?изменить честь плюс 3', RARITY.EPIC, forms.EmptyForm,),
                ('CHANGE_HABIT_HONOR_MINUS_EPIC', 22, u'?изменить честь минус 3', RARITY.EPIC, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_EPIC', 23, u'?изменить миролюбие плюс 3', RARITY.EPIC, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_EPIC', 24, u'?изменить миролюбие минус 3', RARITY.EPIC, forms.EmptyForm,),

                ('CHANGE_HABIT_HONOR_PLUS_LEGENDARY', 25, u'?изменить честь плюс 4', RARITY.LEGENDARY, forms.EmptyForm,),
                ('CHANGE_HABIT_HONOR_MINUS_LEGENDARY', 26, u'?изменить честь минус 4', RARITY.LEGENDARY, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_LEGENDARY', 27, u'?изменить миролюбие плюс 4', RARITY.LEGENDARY, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_LEGENDARY', 28, u'?изменить миролюбие минус 4', RARITY.LEGENDARY, forms.EmptyForm,),

                ('PREFERENCES_COOLDOWNS_RESET_MOB', 29, u'?сбросить кулдаун 1', RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_PLACE', 30, u'?сбросить кулдаун 2', RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_FRIEND', 31, u'?сбросить кулдаун 3', RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_ENEMY', 32, u'?сбросить кулдаун 4', RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_ENERGY_REGENERATION', 33, u'?сбросить кулдаун 5', RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_EQUIPMEN_SLOT', 34, u'?сбросить кулдаун 6', RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_RISK_LEVEL', 35, u'?сбросить кулдаун 7', RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_FAVORITE_ITEM', 36, u'?сбросить кулдаун 8', RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_ARCHETYPE', 37, u'?сбросить кулдаун 9', RARITY.UNCOMMON, forms.EmptyForm,),

                ('PREFERENCES_COOLDOWNS_RESET_ALL', 38, u'?сбросить кулдаун 10', RARITY.RARE, forms.EmptyForm,),

                ('CHANGE_ABILITIES_CHOICES', 39, u'?сбросить абилки', RARITY.UNCOMMON, forms.EmptyForm,),

                ('CHANGE_HERO_SPENDINGS_TO_INSTANT_HEAL', 40, u'?изменить траты 1', RARITY.COMMON, forms.EmptyForm,),
                ('CHANGE_HERO_SPENDINGS_TO_BUYING_ARTIFACT', 41, u'?изменить траты 2', RARITY.COMMON, forms.EmptyForm,),
                ('CHANGE_HERO_SPENDINGS_TO_SHARPENING_ARTIFACT', 42, u'?изменить траты 3', RARITY.COMMON, forms.EmptyForm,),
                ('CHANGE_HERO_SPENDINGS_TO_EXPERIENCE', 43, u'?изменить траты 4', RARITY.COMMON, forms.EmptyForm,),
                ('CHANGE_HERO_SPENDINGS_TO_REPAIRING_ARTIFACT', 44, u'?изменить траты 5', RARITY.COMMON, forms.EmptyForm,),

                ('REPAIR_RANDOM_ARTIFACT', 45, u'?Починка 1', RARITY.UNCOMMON, forms.EmptyForm,),
                ('REPAIR_ALL_ARTIFACTS', 46, u'?Починка 2', RARITY.EPIC, forms.EmptyForm,),

                ('CANCEL_QUEST', 47, u'?отмена задания', RARITY.UNCOMMON, forms.EmptyForm,),

                ('GET_ARTIFACT_COMMON', 48, u'?получить артефакт 1', RARITY.COMMON, forms.EmptyForm,),
                ('GET_ARTIFACT_UNCOMMON', 49, u'?получить артефакт 2', RARITY.UNCOMMON, forms.EmptyForm,),
                ('GET_ARTIFACT_RARE', 50, u'?получить артефакт 3', RARITY.RARE, forms.EmptyForm,),
                ('GET_ARTIFACT_EPIC', 51, u'?получить артефакт 4', RARITY.EPIC, forms.EmptyForm,),

                ('INSTANT_MONSTER_KILL', 52, u'?мгновенно убить монстра', RARITY.COMMON, forms.EmptyForm,),

                ('KEEPERS_GOODS_COMMON', 0, u'?Дары Хранителей 1', RARITY.COMMON, forms.PlaceForm),
                ('KEEPERS_GOODS_UNCOMMON', 53, u'?Дары Хранителей 2', RARITY.UNCOMMON, forms.PlaceForm),
                ('KEEPERS_GOODS_RARE', 54, u'?Дары Хранителей 3', RARITY.RARE, forms.PlaceForm),
                ('KEEPERS_GOODS_EPIC', 55, u'?Дары Хранителей 4', RARITY.EPIC, forms.PlaceForm),
                ('KEEPERS_GOODS_LEGENDARY', 56, u'?Дары Хранителей 5', RARITY.LEGENDARY, forms.PlaceForm),

                ('REPAIR_BUILDING', 57, u'?Починка строения', RARITY.EPIC, forms.BuildingForm),

                ('PERSON_POWER_BONUS_POSITIVE_UNCOMMON', 58, u'?бонус к влиянию соратника позитивный 1', RARITY.UNCOMMON, forms.PersonForm),
                ('PERSON_POWER_BONUS_POSITIVE_RARE', 59, u'?бонус к влиянию соратника позитивный 2', RARITY.RARE, forms.PersonForm),
                ('PERSON_POWER_BONUS_POSITIVE_EPIC', 60, u'?бонус к влиянию соратника позитивный 3', RARITY.EPIC, forms.PersonForm),
                ('PERSON_POWER_BONUS_POSITIVE_LEGENDARY', 61, u'?бонус к влиянию соратника позитивный 4', RARITY.LEGENDARY, forms.PersonForm),

                ('PLACE_POWER_BONUS_POSITIVE_UNCOMMON', 62, u'?бонус к влиянию города позитивный 1', RARITY.UNCOMMON, forms.PlaceForm),
                ('PLACE_POWER_BONUS_POSITIVE_RARE', 63, u'?бонус к влиянию города позитивный 2', RARITY.RARE, forms.PlaceForm),
                ('PLACE_POWER_BONUS_POSITIVE_EPIC', 64, u'?бонус к влиянию города позитивный 3', RARITY.EPIC, forms.PlaceForm),
                ('PLACE_POWER_BONUS_POSITIVE_LEGENDARY', 65, u'?бонус к влиянию города позитивный 4', RARITY.LEGENDARY, forms.PlaceForm),

                ('PLACE_POWER_BONUS_NEGATIVE_UNCOMMON', 66, u'?бонус к влиянию города негативный 1', RARITY.UNCOMMON, forms.PlaceForm),
                ('PLACE_POWER_BONUS_NEGATIVE_RARE', 67, u'?бонус к влиянию города негативный 2', RARITY.RARE, forms.PlaceForm),
                ('PLACE_POWER_BONUS_NEGATIVE_EPIC', 68, u'?бонус к влиянию города негативный 3', RARITY.EPIC, forms.PlaceForm),
                ('PLACE_POWER_BONUS_NEGATIVE_LEGENDARY', 69, u'?бонус к влиянию города негативный 4', RARITY.LEGENDARY, forms.PlaceForm),

                ('MOST_COMMON_PLACES_UNCOMMON', 70, u'?внеочередная момощь городу 1', RARITY.UNCOMMON, forms.PlaceForm),
                ('MOST_COMMON_PLACES_RARE', 71, u'?внеочередная момощь городу 2', RARITY.RARE, forms.PlaceForm),
                ('MOST_COMMON_PLACES_EPIC', 72, u'?внеочередная момощь городу 3', RARITY.EPIC, forms.PlaceForm),
                ('MOST_COMMON_PLACES_LEGENDARY', 73, u'?внеочередная момощь городу 4', RARITY.LEGENDARY, forms.PlaceForm),

                ('ADD_EXPERIENCE_COMMON', 74, u'?добавить опыт 1', RARITY.UNCOMMON, forms.EmptyForm,),
                ('ADD_EXPERIENCE_UNCOMMON', 75, u'?добавить опыт 2', RARITY.UNCOMMON, forms.EmptyForm,),
                ('ADD_EXPERIENCE_RARE', 76, u'?добавить опыт 3', RARITY.RARE, forms.EmptyForm,),
                ('ADD_EXPERIENCE_EPIC', 77, u'?добавить опыт 4', RARITY.EPIC, forms.EmptyForm,),

                ('ADD_POWER_COMMON', 78, u'?добавить влияние 1', RARITY.UNCOMMON, forms.EmptyForm,),
                ('ADD_POWER_UNCOMMON', 79, u'?добавить влияние 2', RARITY.UNCOMMON, forms.EmptyForm,),
                ('ADD_POWER_RARE', 80, u'?добавить влияние 3', RARITY.RARE, forms.EmptyForm,),
                ('ADD_POWER_EPIC', 81, u'?добавить влияние 4', RARITY.EPIC, forms.EmptyForm,),

                ('SHORT_TELEPORT', 82, u'?короткий телепрт', RARITY.UNCOMMON, forms.EmptyForm,),
                ('LONG_TELEPORT', 83, u'?длинный телепорт', RARITY.RARE, forms.EmptyForm,),

                ('EXPERIENCE_TO_ENERGY_UNCOMMON', 84, u'?опыт в энергию 1', RARITY.UNCOMMON, forms.EmptyForm,),
                ('EXPERIENCE_TO_ENERGY_RARE', 85, u'?опыт в энергию 2', RARITY.RARE, forms.EmptyForm,),
                ('EXPERIENCE_TO_ENERGY_EPIC', 86, u'?опыт в энергию 3', RARITY.EPIC, forms.EmptyForm,),
                ('EXPERIENCE_TO_ENERGY_LEGENDARY', 87, u'?опыт в энергию 4', RARITY.LEGENDARY, forms.EmptyForm,),

                )
