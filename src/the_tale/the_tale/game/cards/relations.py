# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game.cards import forms


class RARITY(DjangoEnum):
    priority = Column()

    records = ( ('COMMON', 0, 'обычная карта', 3**4),
                ('UNCOMMON', 1, 'необычная карта', 3**3),
                ('RARE', 2, 'редкая карта', 3**2),
                ('EPIC', 3, 'эпическая карта', 3**1),
                ('LEGENDARY', 4, 'легендарная карта', 3**0) )

class AVAILABILITY(DjangoEnum):
    records = ( ('FOR_ALL', 0, 'для всех'),
                ('FOR_PREMIUMS', 1, 'только для подписчиков') )


class CARDS_COMBINING_STATUS(DjangoEnum):
    records = ( ('ALLOWED', 0, 'Объединение разрешено'),
                ('NOT_ENOUGH_CARDS', 1, 'Не хватает карт'),
                ('TO_MANY_CARDS', 2, 'Слишком много карт'),
                ('EQUAL_RARITY_REQUIRED', 3, 'Карты должны быть одной редкости'),
                ('LEGENDARY_X3_DISALLOWED', 4, 'Нельзя объединять 3 легендарных карты'),
                ('HAS_NO_CARDS', 5, 'У героя нет таких карт') )



class CARD_TYPE(DjangoEnum):
    availability = Column(unique=False)
    rarity = Column(unique=False)
    form = Column(unique=False, primary=False, single_type=False)
    in_game = Column(unique=False, primary=False)

    records = ( ('LEVEL_UP', 1, 'озарение', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True),

                ('ADD_BONUS_ENERGY_COMMON', 5, 'капля энергии', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('ADD_BONUS_ENERGY_UNCOMMON', 6, 'чаша Силы', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('ADD_BONUS_ENERGY_RARE', 7, 'магический вихрь', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('ADD_BONUS_ENERGY_EPIC', 8, 'энергетический шторм', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),
                ('ADD_BONUS_ENERGY_LEGENDARY', 9, 'шквал Силы', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),

                ('ADD_GOLD_COMMON', 10, 'горсть монет', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('ADD_GOLD_UNCOMMON', 11, 'увесистый кошель', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('ADD_GOLD_RARE', 12, 'сундучок на счастье', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),

                ('CHANGE_HABIT_HONOR_PLUS_UNCOMMON', 13, 'умеренность', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('CHANGE_HABIT_HONOR_MINUS_UNCOMMON', 14, 'чревоугодие', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_UNCOMMON', 15, 'спокойствие', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_UNCOMMON', 16, 'вспыльчивость', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('CHANGE_HABIT_HONOR_PLUS_RARE', 17, 'верность', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('CHANGE_HABIT_HONOR_MINUS_RARE', 18, 'блуд', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_RARE', 19, 'дружелюбие', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_RARE', 20, 'алчность', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),

                ('CHANGE_HABIT_HONOR_PLUS_EPIC', 21, 'скромность', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),
                ('CHANGE_HABIT_HONOR_MINUS_EPIC', 22, 'тщеславие', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_EPIC', 23, 'сдержанность', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_EPIC', 24, 'гнев', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),

                ('CHANGE_HABIT_HONOR_PLUS_LEGENDARY', 25, 'смирение', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),
                ('CHANGE_HABIT_HONOR_MINUS_LEGENDARY', 26, 'гордыня', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_PLUS_LEGENDARY', 27, 'миролюбие', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),
                ('CHANGE_HABIT_PEACEFULNESS_MINUS_LEGENDARY', 28, 'ярость', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),

                ('PREFERENCES_COOLDOWNS_RESET_MOB', 29, 'знание врага', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_PLACE', 30, 'новая родина', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_FRIEND', 31, 'новый соратник', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_ENEMY', 32, 'новый противник', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_ENERGY_REGENERATION', 33, 'прозрение', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_EQUIPMEN_SLOT', 34, 'вкусы в экипировке', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_RISK_LEVEL', 35, 'определение лихости', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_FAVORITE_ITEM', 36, 'наскучившая вещь', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_ARCHETYPE', 37, 'пересмотр стиля боя', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('PREFERENCES_COOLDOWNS_RESET_ALL', 38, 'пересмотр ценностей', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),

                ('CHANGE_ABILITIES_CHOICES', 39, 'альтернатива', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('CHANGE_HERO_SPENDINGS_TO_INSTANT_HEAL', 40, 'странный зуд', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('CHANGE_HERO_SPENDINGS_TO_BUYING_ARTIFACT', 41, 'магазинный импульс', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('CHANGE_HERO_SPENDINGS_TO_SHARPENING_ARTIFACT', 42, 'стремление к совершенству', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('CHANGE_HERO_SPENDINGS_TO_EXPERIENCE', 43, 'тяга к знаниям', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('CHANGE_HERO_SPENDINGS_TO_REPAIRING_ARTIFACT', 44, 'забота об имуществе', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),

                ('REPAIR_RANDOM_ARTIFACT', 45, 'фея-мастерица', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('REPAIR_ALL_ARTIFACTS', 46, 'благословение Великого Творца', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),

                ('CANCEL_QUEST', 47, 'другие заботы', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('GET_ARTIFACT_COMMON', 48, 'внезапная находка', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('GET_ARTIFACT_UNCOMMON', 49, 'полезный подарок', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('GET_ARTIFACT_RARE', 50, 'редкое приобретение', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('GET_ARTIFACT_EPIC', 51, 'дар Хранителя', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),

                ('INSTANT_MONSTER_KILL', 52, 'длань Смерти', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),

                ('KEEPERS_GOODS_COMMON', 53, 'неразменная монета', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.PlaceForm, True),
                ('KEEPERS_GOODS_UNCOMMON', 54, 'волшебный горшочек', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PlaceForm, True),
                ('KEEPERS_GOODS_RARE', 55, 'скатерть самобранка', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PlaceForm, True),
                ('KEEPERS_GOODS_EPIC', 56, 'несметные богатства', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PlaceForm, True),
                ('KEEPERS_GOODS_LEGENDARY', 0, 'рог изобилия', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PlaceForm, True),

                ('REPAIR_BUILDING', 57, 'волшебный инструмент', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.BuildingForm, True),

                ('ADD_PERSON_POWER_POSITIVE_UNCOMMON', 58, 'удачный день', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PersonForm, True),
                ('ADD_PERSON_POWER_POSITIVE_RARE', 59, 'нежданная выгода', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PersonForm, True),
                ('ADD_PERSON_POWER_POSITIVE_EPIC', 60, 'удачная афера', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PersonForm, True),
                ('ADD_PERSON_POWER_POSITIVE_LEGENDARY', 61, 'преступление века', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PersonForm, True),

                ('ADD_PLACE_POWER_POSITIVE_UNCOMMON', 62, 'погожие деньки', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_POSITIVE_RARE', 63, 'торговый день', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_POSITIVE_EPIC', 64, 'городской праздник', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_POSITIVE_LEGENDARY', 65, 'экономический рост', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PlaceForm, True),

                ('ADD_PLACE_POWER_NEGATIVE_UNCOMMON', 66, 'ужасная погода', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_NEGATIVE_RARE', 67, 'запустение', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_NEGATIVE_EPIC', 68, 'нашествие крыс', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_NEGATIVE_LEGENDARY', 69, 'экономический спад', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PlaceForm, True),

                ('MOST_COMMON_PLACES_UNCOMMON', 70, 'ошибка в архивах', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.PlaceForm, True),
                ('MOST_COMMON_PLACES_RARE', 71, 'фальшивые рекомендации', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.PlaceForm, True),
                ('MOST_COMMON_PLACES_EPIC', 72, 'застолье в Совете', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.PlaceForm, True),
                ('MOST_COMMON_PLACES_LEGENDARY', 73, 'интриги', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.PlaceForm, True),

                ('ADD_EXPERIENCE_COMMON', 74, 'удачная мысль', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('ADD_EXPERIENCE_UNCOMMON', 75, 'чистый разум', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('ADD_EXPERIENCE_RARE', 76, 'неожиданные осложнения', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('ADD_EXPERIENCE_EPIC', 77, 'слово Гзанзара', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),

                ('ADD_POWER_COMMON', 78, 'новые обстоятельства', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.EmptyForm, True,),
                ('ADD_POWER_UNCOMMON', 79, 'специальная операция', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('ADD_POWER_RARE', 80, 'слово Дабнглана', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.EmptyForm, True,),
                ('ADD_POWER_EPIC', 81, 'благословение Дабнглана', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.EmptyForm, True,),

                ('SHORT_TELEPORT', 82, 'телепорт', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('LONG_TELEPORT', 83, 'ТАРДИС', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),

                ('EXPERIENCE_TO_ENERGY_UNCOMMON', 84, 'амнезия', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, False,),
                ('EXPERIENCE_TO_ENERGY_RARE', 85, 'донор Силы', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, False,),
                ('EXPERIENCE_TO_ENERGY_EPIC', 86, 'взыскание долга', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, False,),
                ('EXPERIENCE_TO_ENERGY_LEGENDARY', 87, 'ритуал Силы', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, False,),

                ('SHARP_RANDOM_ARTIFACT', 88, 'волшебное точило', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('SHARP_ALL_ARTIFACTS', 89, 'суть вещей', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),

                ('GET_COMPANION_COMMON', 90, 'обычный спутник', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True),
                ('GET_COMPANION_UNCOMMON', 91, 'необычный спутник', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True),
                ('GET_COMPANION_RARE', 92, 'редкий спутник', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True),
                ('GET_COMPANION_EPIC', 93, 'эпический спутник', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True),
                ('GET_COMPANION_LEGENDARY', 94, 'легендарный спутник', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True),

                ('PREFERENCES_COOLDOWNS_RESET_COMPANION_DEDICATION', 95, 'новый взгляд', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('PREFERENCES_COOLDOWNS_RESET_COMPANION_EMPATHY', 96, 'чуткость', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('ADD_EXPERIENCE_LEGENDARY', 97, 'благословение Гзанзара', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),

                ('RESET_ABILITIES', 98, 'новый путь', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),

                ('RELEASE_COMPANION', 99, 'четыре стороны', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),

                ('HEAL_COMPANION_COMMON', 100, 'передышка', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),
                ('HEAL_COMPANION_UNCOMMON', 101, 'подорожник', AVAILABILITY.FOR_ALL, RARITY.UNCOMMON, forms.EmptyForm, True,),
                ('HEAL_COMPANION_RARE', 102, 'священный мёд', AVAILABILITY.FOR_ALL, RARITY.RARE, forms.EmptyForm, True,),
                ('HEAL_COMPANION_EPIC', 103, 'молодильное яблоко', AVAILABILITY.FOR_ALL, RARITY.EPIC, forms.EmptyForm, True,),
                ('HEAL_COMPANION_LEGENDARY', 104, 'живая вода', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),

                ('CHANGE_HERO_SPENDINGS_TO_HEAL_COMPANION', 105, 'забота о ближнем', AVAILABILITY.FOR_ALL, RARITY.COMMON, forms.EmptyForm, True,),

                ('INCREMENT_ARTIFACT_RARITY', 106, 'скрытый потенциал', AVAILABILITY.FOR_ALL, RARITY.LEGENDARY, forms.EmptyForm, True,),

                ('ADD_POWER_LEGENDARY', 107, 'туз в рукаве', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.EmptyForm, True,),
                ('ADD_PERSON_POWER_POSITIVE_COMMON', 108, 'улыбка фортуны', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.PersonForm, True),

                ('ADD_PLACE_POWER_POSITIVE_COMMON', 109, 'выгодный контракт', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.PlaceForm, True),
                ('ADD_PLACE_POWER_NEGATIVE_COMMON', 110, 'сорванный контракт', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.PlaceForm, True),

                ('ADD_PERSON_POWER_NEGATIVE_COMMON', 111, 'гримаса фортуны', AVAILABILITY.FOR_PREMIUMS, RARITY.COMMON, forms.PersonForm, True),
                ('ADD_PERSON_POWER_NEGATIVE_UNCOMMON', 112, 'гадкий день', AVAILABILITY.FOR_PREMIUMS, RARITY.UNCOMMON, forms.PersonForm, True),
                ('ADD_PERSON_POWER_NEGATIVE_RARE', 113, 'нежданная беда', AVAILABILITY.FOR_PREMIUMS, RARITY.RARE, forms.PersonForm, True),
                ('ADD_PERSON_POWER_NEGATIVE_EPIC', 114, 'провальное мероприятие', AVAILABILITY.FOR_PREMIUMS, RARITY.EPIC, forms.PersonForm, True),
                ('ADD_PERSON_POWER_NEGATIVE_LEGENDARY', 115, 'чёрная полоса', AVAILABILITY.FOR_PREMIUMS, RARITY.LEGENDARY, forms.PersonForm, True),
                )
