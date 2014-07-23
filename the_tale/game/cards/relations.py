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

    records = ( ('KEEPERS_GOODS', 0, u'?Дары Хранителей', RARITY.LEGENDARY, forms.PlaceForm),
                ('LEVEL_UP', 1, u'?увеличить уровень', RARITY.LEGENDARY, forms.EmptyForm,),

                ('ADD_EXPERIENCE_UNCOMMON', 2, u'?добавить опыт 1', RARITY.UNCOMMON, forms.EmptyForm,),
                ('ADD_EXPERIENCE_RARE', 3, u'?добавить опыт 2', RARITY.RARE, forms.EmptyForm,),
                ('ADD_EXPERIENCE_EPIC', 4, u'?добавить опыт 3', RARITY.EPIC, forms.EmptyForm,),

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
                )
