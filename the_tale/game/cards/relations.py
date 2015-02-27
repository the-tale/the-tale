# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.cards import forms


class RARITY(DjangoEnum):
    priority = Column()

    records = ( ('COMMON', 0, u'обычная карта', 3**4),
                ('UNCOMMON', 1, u'необычная карта', 3**3),
                ('RARE', 2, u'редкая карта', 3**2),
                ('EPIC', 3, u'эпическая карта', 3**1),
                ('LEGENDARY', 4, u'легендарная карта', 3**0) )

class AVAILABILITY(DjangoEnum):
    records = ( ('FOR_ALL', 0, u'для всех'),
                ('FOR_PREMIUMS', 1, u'только для подписчиков') )


class CARDS_COMBINING_STATUS(DjangoEnum):
    records = ( ('ALLOWED', 0, u'Объединение разрешено'),
                ('NOT_ENOUGH_CARDS', 1, u'Не хватает карт'),
                ('TO_MANY_CARDS', 2, u'Слишком много карт'),
                ('EQUAL_RARITY_REQUIRED', 3, u'Карты должны быть одной редкости'),
                ('LEGENDARY_X3_DISALLOWED', 4, u'Нельзя объединять 3 легендарных карты'),
                ('HAS_NO_CARDS', 5, u'У героя нет таких карт') )



class CARD_TYPE(DjangoEnum):
    availability = Column(unique=False)
    rarity = Column(unique=False)
    form = Column(unique=False, primary=False, single_type=False)

    records = ( ('LEVEL_UP', 1, u'озарение', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm,),

                ('ADD_BONUS_ENERGY_COMMON', 5, u'капля энергии', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm,),
                ('ADD_BONUS_ENERGY_UNCOMMON', 6, u'чаша Силы', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('ADD_BONUS_ENERGY_RARE', 7, u'магический вихрь', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm,),
                ('ADD_BONUS_ENERGY_EPIC', 8, u'энергетический шторм', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm,),
                ('ADD_BONUS_ENERGY_LEGENDARY', 9, u'шквал Силы', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm,),

                ('ADD_GOLD_COMMON', 10, u'горсть монет', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm,),
                ('ADD_GOLD_UNCOMMON', 11, u'увесистый кошель', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('ADD_GOLD_RARE', 12, u'сундучок на счастье', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm,),

                ('CHANGE_HABIT_HONOR_PLUS_UNCOMMON', 13, u'умеренность', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('CHANGE_HABIT_HONOR_MINUS_UNCOMMON', 14, u'чревоугодие', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_UNCOMMON', 15, u'спокойствие', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_UNCOMMON', 16, u'вспыльчивость', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),

                ('CHANGE_HABIT_HONOR_PLUS_RARE', 17, u'верность', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm,),
                ('CHANGE_HABIT_HONOR_MINUS_RARE', 18, u'блуд', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_RARE', 19, u'дружелюбие', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_RARE', 20, u'алчность', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm,),

                ('CHANGE_HABIT_HONOR_PLUS_EPIC', 21, u'скромность', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm,),
                ('CHANGE_HABIT_HONOR_MINUS_EPIC', 22, u'тщеславие', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_EPIC', 23, u'сдержанность', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_EPIC', 24, u'гнев', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm,),

                ('CHANGE_HABIT_HONOR_PLUS_LEGENDARY', 25, u'смирение', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm,),
                ('CHANGE_HABIT_HONOR_MINUS_LEGENDARY', 26, u'гордыня', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_LEGENDARY', 27, u'миролюбие', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_LEGENDARY', 28, u'ярость', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm,),

                ('PREFERENCES_COOLDOWNS_RESET_MOB', 29, u'знание врага', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_PLACE', 30, u'новая родина', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_FRIEND', 31, u'новый соратник', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_ENEMY', 32, u'новый противник', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_ENERGY_REGENERATION', 33, u'прозрение', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_EQUIPMEN_SLOT', 34, u'вкусы в экипировке', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_RISK_LEVEL', 35, u'определение лихости', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_FAVORITE_ITEM', 36, u'наскучившая вещь', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_ARCHETYPE', 37, u'пересмотр стиля боя', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),

                ('PREFERENCES_COOLDOWNS_RESET_ALL', 38, u'пересмотр ценностей', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm,),

                ('CHANGE_ABILITIES_CHOICES', 39, u'альтернатива', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),

                ('CHANGE_HERO_SPENDINGS_TO_INSTANT_HEAL', 40, u'странный зуд', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm,),
                ('CHANGE_HERO_SPENDINGS_TO_BUYING_ARTIFACT', 41, u'магазинный импульс', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm,),
                ('CHANGE_HERO_SPENDINGS_TO_SHARPENING_ARTIFACT', 42, u'стремление к совершенству', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm,),
                ('CHANGE_HERO_SPENDINGS_TO_EXPERIENCE', 43, u'тяга к знаниям', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm,),
                ('CHANGE_HERO_SPENDINGS_TO_REPAIRING_ARTIFACT', 44, u'забота об имуществе', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm,),

                ('REPAIR_RANDOM_ARTIFACT', 45, u'фея-мастерица', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('REPAIR_ALL_ARTIFACTS', 46, u'благословение Великого Творца', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm,),

                ('CANCEL_QUEST', 47, u'другие заботы', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),

                ('GET_ARTIFACT_COMMON', 48, u'внезапная находка', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm,),
                ('GET_ARTIFACT_UNCOMMON', 49, u'полезный подарок', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('GET_ARTIFACT_RARE', 50, u'редкое приобретение', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm,),
                ('GET_ARTIFACT_EPIC', 51, u'дар Хранителя', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm,),

                ('INSTANT_MONSTER_KILL', 52, u'длань Смерти', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm,),

                ('KEEPERS_GOODS_COMMON', 53, u'неразменная монета', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.PlaceForm),
                ('KEEPERS_GOODS_UNCOMMON', 54, u'волшебный горшочек', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PlaceForm),
                ('KEEPERS_GOODS_RARE', 55, u'скатерть самобранка', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PlaceForm),
                ('KEEPERS_GOODS_EPIC', 56, u'несметные богатства', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PlaceForm),
                ('KEEPERS_GOODS_LEGENDARY', 0, u'рог изобилия', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PlaceForm),

                ('REPAIR_BUILDING', 57, u'волшебный инструмент', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.BuildingForm),

                ('PERSON_POWER_BONUS_POSITIVE_UNCOMMON', 58, u'удачный день', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PersonForm),
                ('PERSON_POWER_BONUS_POSITIVE_RARE', 59, u'нежданная выгода', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PersonForm),
                ('PERSON_POWER_BONUS_POSITIVE_EPIC', 60, u'удачная афёра', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PersonForm),
                ('PERSON_POWER_BONUS_POSITIVE_LEGENDARY', 61, u'преступление века', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PersonForm),

                ('PLACE_POWER_BONUS_POSITIVE_UNCOMMON', 62, u'погожие деньки', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PlaceForm),
                ('PLACE_POWER_BONUS_POSITIVE_RARE', 63, u'торговый день', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PlaceForm),
                ('PLACE_POWER_BONUS_POSITIVE_EPIC', 64, u'городской праздник', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PlaceForm),
                ('PLACE_POWER_BONUS_POSITIVE_LEGENDARY', 65, u'экономический рост', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PlaceForm),

                ('PLACE_POWER_BONUS_NEGATIVE_UNCOMMON', 66, u'ужасная погода', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PlaceForm),
                ('PLACE_POWER_BONUS_NEGATIVE_RARE', 67, u'запустение', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PlaceForm),
                ('PLACE_POWER_BONUS_NEGATIVE_EPIC', 68, u'нашествие крыс', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PlaceForm),
                ('PLACE_POWER_BONUS_NEGATIVE_LEGENDARY', 69, u'экономический спад', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PlaceForm),

                ('MOST_COMMON_PLACES_UNCOMMON', 70, u'ошибка в архивах', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.PlaceForm),
                ('MOST_COMMON_PLACES_RARE', 71, u'фальшивые рекомендации', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.PlaceForm),
                ('MOST_COMMON_PLACES_EPIC', 72, u'застолье в Совете', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.PlaceForm),
                ('MOST_COMMON_PLACES_LEGENDARY', 73, u'интриги', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.PlaceForm),

                ('ADD_EXPERIENCE_COMMON', 74, u'удачная мысль', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm,),
                ('ADD_EXPERIENCE_UNCOMMON', 75, u'чистый разум', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('ADD_EXPERIENCE_RARE', 76, u'неожиданные осложнения', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm,),
                ('ADD_EXPERIENCE_EPIC', 77, u'слово Гзанзара', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm,),

                ('ADD_POWER_COMMON', 78, u'новые обстоятельства', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.EmptyForm,),
                ('ADD_POWER_UNCOMMON', 79, u'специальная операция', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.EmptyForm,),
                ('ADD_POWER_RARE', 80, u'слово Дабнглана', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.EmptyForm,),
                ('ADD_POWER_EPIC', 81, u'благословление Дабнглана', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.EmptyForm,),

                ('SHORT_TELEPORT', 82, u'телепорт', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('LONG_TELEPORT', 83, u'ТАРДИС', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm,),

                ('EXPERIENCE_TO_ENERGY_UNCOMMON', 84, u'амнезия', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('EXPERIENCE_TO_ENERGY_RARE', 85, u'донор Силы', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm,),
                ('EXPERIENCE_TO_ENERGY_EPIC', 86, u'взыскание долга', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm,),
                ('EXPERIENCE_TO_ENERGY_LEGENDARY', 87, u'ритуал Силы', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm,),

                ('SHARP_RANDOM_ARTIFACT', 88, u'волшебное точило', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('SHARP_ALL_ARTIFACTS', 89, u'суть вещей', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm,),

                ('GET_COMPANION_COMMON', 90, u'обычный спутник', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm),
                ('GET_COMPANION_UNCOMMON', 91, u'необычный спутник', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm),
                ('GET_COMPANION_RARE', 92, u'редкий спутник', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm),
                ('GET_COMPANION_EPIC', 93, u'эпический спутник', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm),
                ('GET_COMPANION_LEGENDARY', 94, u'легендарный спутник', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm),

                ('PREFERENCES_COOLDOWNS_RESET_COMPANION_DEDICATION', 95, u'новый взгляд', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),
                ('PREFERENCES_COOLDOWNS_RESET_COMPANION_EMPATHY', 96, u'чуткость', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),

                ('ADD_EXPERIENCE_LEGENDARY', 97, u'благословление Гзанзара', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm,),

                ('RESET_ABILITIES', 98, u'новый путь', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm,),

                ('RELEASE_COMPANION', 99, u'четыре стороны', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm,),

                )
