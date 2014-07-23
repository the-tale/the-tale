# coding: utf-8

from dext.utils import discovering

from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.game.workers.environment import workers_environment

from the_tale.game.cards import relations

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.map.places.storage import places_storage

from the_tale.game.balance import constants as c

from the_tale.game.relations import HABIT_TYPE


class CardBase(object):
    TYPE = None

    def activate(self, hero, data):
        from the_tale.game.cards.postponed_tasks import UseCardTask

        data['hero_id'] = hero.id
        data['account_id'] = hero.account_id

        card_task = UseCardTask(processor_id=self.TYPE.value,
                                hero_id=hero.id,
                                data=data)

        task = PostponedTaskPrototype.create(card_task)

        workers_environment.supervisor.cmd_logic_task(hero.account_id, task.id)

        return task


    def use(self, *argv, **kwargs):
        raise NotImplementedError()

    def check_hero_conditions(self, hero):
        return hero.cards.card_count(self.TYPE)

    def hero_actions(self, hero):
        hero.cards.remove_card(self.TYPE, count=1)



class LevelUp(CardBase):
    TYPE = relations.CARD_TYPE.LEVEL_UP
    DESCRIPTION = u'Ваш герой получает новый уровень. Накопленные очки опыта не сбрасываются.'

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]
            hero.increment_level(send_message=False)
            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class AddExperienceBase(CardBase):
    TYPE = None
    EXPERIENCE = None

    @property
    def DESCRIPTION(self):
        return u'Ваш герой получает %(experience)d очков опыта.' % {'experience': self.EXPERIENCE}

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]
            hero.add_experience(self.EXPERIENCE)
            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()

class AddExperienceUncommon(AddExperienceBase):
    TYPE = relations.CARD_TYPE.ADD_EXPERIENCE_UNCOMMON
    EXPERIENCE = 100

class AddExperienceRare(AddExperienceBase):
    TYPE = relations.CARD_TYPE.ADD_EXPERIENCE_RARE
    EXPERIENCE = AddExperienceUncommon.EXPERIENCE * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class AddExperienceEpic(AddExperienceBase):
    TYPE = relations.CARD_TYPE.ADD_EXPERIENCE_EPIC
    EXPERIENCE = AddExperienceRare.EXPERIENCE * (c.CARDS_COMBINE_TO_UP_RARITY + 1)


class AddBonusEnergyBase(CardBase):
    TYPE = None
    ENERGY = None

    @property
    def DESCRIPTION(self):
        return u'Вы получаете %(energy)d единиц дополнительной энергии.' % {'energy': self.ENERGY}

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]
            hero.add_energy_bonus(self.ENERGY)
            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()

class AddBonusEnergyCommon(AddBonusEnergyBase):
    TYPE = relations.CARD_TYPE.ADD_BONUS_ENERGY_COMMON
    ENERGY = 10

class AddBonusEnergyUncommon(AddBonusEnergyBase):
    TYPE = relations.CARD_TYPE.ADD_BONUS_ENERGY_UNCOMMON
    ENERGY = AddBonusEnergyCommon.ENERGY * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class AddBonusEnergyRare(AddBonusEnergyBase):
    TYPE = relations.CARD_TYPE.ADD_BONUS_ENERGY_RARE
    ENERGY = AddBonusEnergyUncommon.ENERGY * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class AddBonusEnergyEpic(AddBonusEnergyBase):
    TYPE = relations.CARD_TYPE.ADD_BONUS_ENERGY_EPIC
    ENERGY = AddBonusEnergyRare.ENERGY * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class AddBonusEnergyLegendary(AddBonusEnergyBase):
    TYPE = relations.CARD_TYPE.ADD_BONUS_ENERGY_LEGENDARY
    ENERGY = AddBonusEnergyEpic.ENERGY * (c.CARDS_COMBINE_TO_UP_RARITY + 1)


class AddGoldBase(CardBase):
    TYPE = None
    GOLD = None

    @property
    def DESCRIPTION(self):
        return u'Ваш герой получает %(gold)d монет.' % {'gold': self.GOLD}

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        from the_tale.game.heroes.relations import MONEY_SOURCE

        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]
            hero.change_money(MONEY_SOURCE.EARNED_FROM_HELP, self.GOLD)
            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()

class AddGoldCommon(AddGoldBase):
    TYPE = relations.CARD_TYPE.ADD_GOLD_COMMON
    GOLD = 1000

class AddGoldUncommon(AddGoldBase):
    TYPE = relations.CARD_TYPE.ADD_GOLD_UNCOMMON
    GOLD = AddGoldCommon.GOLD * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class AddGoldRare(AddGoldBase):
    TYPE = relations.CARD_TYPE.ADD_GOLD_RARE
    GOLD = AddGoldUncommon.GOLD * (c.CARDS_COMBINE_TO_UP_RARITY + 1)


class ChangeHabitBase(CardBase):
    TYPE = None
    HABIT = None
    POINTS = None

    @property
    def DESCRIPTION(self):
        if self.POINTS > 0:
            return u'Увеличивает %(habit) героя на %(points)d единиц.' % {'habit': self.HABIT.text,
                                                                          'points': self.POINTS}
        return u'Уменьшает %(habit) героя на %(points)d единиц.' % {'habit': self.HABIT.text,
                                                                    'points': -self.POINTS}

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]
            hero.change_habits(self.HABIT, self.POINTS)
            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class ChangeHabitHonorPlusUncommon(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_HONOR_PLUS_UNCOMMON
    HABIT = HABIT_TYPE.HONOR
    POINTS = 25

class ChangeHabitHonorMinusUncommon(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_HONOR_MINUS_UNCOMMON
    HABIT = HABIT_TYPE.HONOR
    POINTS = -25

class ChangeHabitPeacefulnessPlusUncommon(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_PEACEFULNESS_PLUS_UNCOMMON
    HABIT = HABIT_TYPE.PEACEFULNESS
    POINTS = 25

class ChangeHabitPeacefulnessMinusUncommon(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_PEACEFULNESS_MINUS_UNCOMMON
    HABIT = HABIT_TYPE.PEACEFULNESS
    POINTS = -25


class ChangeHabitHonorPlusRare(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_HONOR_PLUS_RARE
    HABIT = HABIT_TYPE.HONOR
    POINTS = ChangeHabitHonorPlusUncommon.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class ChangeHabitHonorMinusRare(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_HONOR_MINUS_RARE
    HABIT = HABIT_TYPE.HONOR
    POINTS = ChangeHabitHonorMinusUncommon.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class ChangeHabitPeacefulnessPlusRare(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_PEACEFULNESS_PLUS_RARE
    HABIT = HABIT_TYPE.PEACEFULNESS
    POINTS = ChangeHabitPeacefulnessPlusUncommon.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class ChangeHabitPeacefulnessMinusRare(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_PEACEFULNESS_MINUS_RARE
    HABIT = HABIT_TYPE.PEACEFULNESS
    POINTS = ChangeHabitPeacefulnessMinusUncommon.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)


class ChangeHabitHonorPlusEpic(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_HONOR_PLUS_EPIC
    HABIT = HABIT_TYPE.HONOR
    POINTS = ChangeHabitHonorPlusRare.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class ChangeHabitHonorMinusEpic(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_HONOR_MINUS_EPIC
    HABIT = HABIT_TYPE.HONOR
    POINTS = ChangeHabitHonorMinusRare.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class ChangeHabitPeacefulnessPlusEpic(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_PEACEFULNESS_PLUS_EPIC
    HABIT = HABIT_TYPE.PEACEFULNESS
    POINTS = ChangeHabitPeacefulnessPlusRare.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class ChangeHabitPeacefulnessMinusEpic(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_PEACEFULNESS_MINUS_EPIC
    HABIT = HABIT_TYPE.PEACEFULNESS
    POINTS = ChangeHabitPeacefulnessMinusRare.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)


class ChangeHabitHonorPlusLegendary(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_HONOR_PLUS_LEGENDARY
    HABIT = HABIT_TYPE.HONOR
    POINTS = ChangeHabitHonorPlusEpic.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class ChangeHabitHonorMinusLegendary(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_HONOR_MINUS_LEGENDARY
    HABIT = HABIT_TYPE.HONOR
    POINTS = ChangeHabitHonorMinusEpic.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class ChangeHabitPeacefulnessPlusLegendary(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_PEACEFULNESS_PLUS_LEGENDARY
    HABIT = HABIT_TYPE.PEACEFULNESS
    POINTS = ChangeHabitPeacefulnessPlusEpic.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class ChangeHabitPeacefulnessMinusLegendary(ChangeHabitBase):
    TYPE = relations.CARD_TYPE.CHANGE_HABIT_PEACEFULNESS_MINUS_LEGENDARY
    HABIT = HABIT_TYPE.PEACEFULNESS
    POINTS = ChangeHabitPeacefulnessMinusEpic.POINTS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)


class KeepersGoods(CardBase):
    TYPE = relations.CARD_TYPE.KEEPERS_GOODS
    GOODS = 5000
    DESCRIPTION = u'Создаёт в указанном городе %(goods)d «даров Хранителей». Город будет постепенно переводить их в продукцию, пока дары не кончатся.' % {'goods': GOODS}

    def use(self, data, step, main_task_id, storage, highlevel=None, **kwargs): # pylint: disable=R0911,W0613

        place_id = data.get('place_id')

        if place_id not in places_storage:
            return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()

        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            return ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL, ((lambda: workers_environment.highlevel.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step.is_HIGHLEVEL:
            place = places_storage[place_id]

            place.keepers_goods += self.GOODS
            place.sync_parameters()

            place.save()

            places_storage.update_version()

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()



CARDS = {card_class.TYPE: card_class
         for card_class in discovering.discover_classes(globals().values(), CardBase)
         if card_class.TYPE is not None}
