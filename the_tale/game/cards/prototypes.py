# coding: utf-8
import random

from dext.utils import discovering

from rels import Column
from rels.django import DjangoEnum

from the_tale.common.postponed_tasks import PostponedTaskPrototype
from the_tale.common.utils.logic import random_value_by_priority

from the_tale.game.workers.environment import workers_environment

from the_tale.game.cards import relations

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.map.places.storage import places_storage, buildings_storage
from the_tale.game.persons.storage import persons_storage

from the_tale.game.balance import constants as c
from the_tale.game.prototypes import TimePrototype

from the_tale.game.relations import HABIT_TYPE
from the_tale.game.heroes.relations import PREFERENCE_TYPE, ITEMS_OF_EXPENDITURE

from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.artifacts.relations import RARITY as ARTIFACT_RARITY


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
        return u'Увеличивает опыт за текущее задание на %(experience)d очков опыта.' % {'experience': self.EXPERIENCE}

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            if not hero.quests.has_quests:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()

            hero.quests.current_quest.current_info.experience += self.EXPERIENCE
            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()

class AddExperienceCommon(AddExperienceBase):
    TYPE = relations.CARD_TYPE.ADD_EXPERIENCE_COMMON
    EXPERIENCE = 25

class AddExperienceUncommon(AddExperienceBase):
    TYPE = relations.CARD_TYPE.ADD_EXPERIENCE_UNCOMMON
    EXPERIENCE = AddExperienceCommon.EXPERIENCE * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class AddExperienceRare(AddExperienceBase):
    TYPE = relations.CARD_TYPE.ADD_EXPERIENCE_RARE
    EXPERIENCE = AddExperienceUncommon.EXPERIENCE * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class AddExperienceEpic(AddExperienceBase):
    TYPE = relations.CARD_TYPE.ADD_EXPERIENCE_EPIC
    EXPERIENCE = AddExperienceRare.EXPERIENCE * (c.CARDS_COMBINE_TO_UP_RARITY + 1)


class AddPowerBase(CardBase):
    TYPE = None
    POWER = None

    @property
    def DESCRIPTION(self):
        return u'Увеличивает влияние за текущее задание на %(power)d очков опыта.' % {'power': self.POWER}

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            if not hero.quests.has_quests:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()

            hero.quests.current_quest.current_info.power += self.POWER
            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()

class AddPowerCommon(AddPowerBase):
    TYPE = relations.CARD_TYPE.ADD_POWER_COMMON
    POWER = 500

class AddPowerUncommon(AddPowerBase):
    TYPE = relations.CARD_TYPE.ADD_POWER_UNCOMMON
    POWER = AddPowerCommon.POWER * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class AddPowerRare(AddPowerBase):
    TYPE = relations.CARD_TYPE.ADD_POWER_RARE
    POWER = AddPowerUncommon.POWER * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class AddPowerEpic(AddPowerBase):
    TYPE = relations.CARD_TYPE.ADD_POWER_EPIC
    POWER = AddPowerRare.POWER * (c.CARDS_COMBINE_TO_UP_RARITY + 1)


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
            return u'Увеличивает %(habit)s героя на %(points)d единиц.' % {'habit': self.HABIT.text,
                                                                          'points': self.POINTS}
        return u'Уменьшает %(habit)s героя на %(points)d единиц.' % {'habit': self.HABIT.text,
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


class PreferencesCooldownsResetBase(CardBase):
    TYPE = None
    PREFERENCE = None

    @property
    def DESCRIPTION(self):
        return u'Сбрасывает задержку на изменение предпочтения «%(preference)s».' % {'preference': self.PREFERENCE.text}

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]
            hero.preferences.reset_change_time(self.PREFERENCE)
            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()

class PreferencesCooldownsResetMob(PreferencesCooldownsResetBase):
    TYPE = relations.CARD_TYPE.PREFERENCES_COOLDOWNS_RESET_MOB
    PREFERENCE = PREFERENCE_TYPE.MOB

class PreferencesCooldownsResetPlace(PreferencesCooldownsResetBase):
    TYPE = relations.CARD_TYPE.PREFERENCES_COOLDOWNS_RESET_PLACE
    PREFERENCE = PREFERENCE_TYPE.PLACE

class PreferencesCooldownsResetFriend(PreferencesCooldownsResetBase):
    TYPE = relations.CARD_TYPE.PREFERENCES_COOLDOWNS_RESET_FRIEND
    PREFERENCE = PREFERENCE_TYPE.FRIEND

class PreferencesCooldownsResetEnemy(PreferencesCooldownsResetBase):
    TYPE = relations.CARD_TYPE.PREFERENCES_COOLDOWNS_RESET_ENEMY
    PREFERENCE = PREFERENCE_TYPE.ENEMY

class PreferencesCooldownsResetEnergyRegeneration(PreferencesCooldownsResetBase):
    TYPE = relations.CARD_TYPE.PREFERENCES_COOLDOWNS_RESET_ENERGY_REGENERATION
    PREFERENCE = PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE

class PreferencesCooldownsResetEquipmentSlot(PreferencesCooldownsResetBase):
    TYPE = relations.CARD_TYPE.PREFERENCES_COOLDOWNS_RESET_EQUIPMEN_SLOT
    PREFERENCE = PREFERENCE_TYPE.EQUIPMENT_SLOT

class PreferencesCooldownsResetRiskLevel(PreferencesCooldownsResetBase):
    TYPE = relations.CARD_TYPE.PREFERENCES_COOLDOWNS_RESET_RISK_LEVEL
    PREFERENCE = PREFERENCE_TYPE.RISK_LEVEL

class PreferencesCooldownsResetFavoriteItem(PreferencesCooldownsResetBase):
    TYPE = relations.CARD_TYPE.PREFERENCES_COOLDOWNS_RESET_FAVORITE_ITEM
    PREFERENCE = PREFERENCE_TYPE.FAVORITE_ITEM

class PreferencesCooldownsResetArchetype(PreferencesCooldownsResetBase):
    TYPE = relations.CARD_TYPE.PREFERENCES_COOLDOWNS_RESET_ARCHETYPE
    PREFERENCE = PREFERENCE_TYPE.ARCHETYPE


class PreferencesCooldownsResetAll(CardBase):
    TYPE = relations.CARD_TYPE.PREFERENCES_COOLDOWNS_RESET_ALL

    DESCRIPTION = u'Сбрасывает задержку на изменение всех предпочтений.'

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]
            for preference in PREFERENCE_TYPE.records:
                hero.preferences.reset_change_time(preference)
            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class ChangeAbilitiesChoices(CardBase):
    TYPE = relations.CARD_TYPE.CHANGE_ABILITIES_CHOICES
    DESCRIPTION = u'Изменяет список новых способностей.'

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            if hero.abilities.rechooce_choices():
                return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()

            return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, () #TODO: return correct message


class ChangeItemOfExpenditureBase(CardBase):
    TYPE = None
    ITEM = None

    @property
    def DESCRIPTION(self):
        return u'Текущей целью трат героев становится %(item)s.' % {'item': self.ITEM.text}

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]
            hero.next_spending = self.ITEM
            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()

class ChangeHeroSpendingsToInstantHeal(ChangeItemOfExpenditureBase):
    TYPE = relations.CARD_TYPE.CHANGE_HERO_SPENDINGS_TO_INSTANT_HEAL
    ITEM = ITEMS_OF_EXPENDITURE.INSTANT_HEAL

class ChangeHeroSpendingsToBuyingArtifact(ChangeItemOfExpenditureBase):
    TYPE = relations.CARD_TYPE.CHANGE_HERO_SPENDINGS_TO_BUYING_ARTIFACT
    ITEM = ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT

class ChangeHeroSpendingsToSharpeingArtifact(ChangeItemOfExpenditureBase):
    TYPE = relations.CARD_TYPE.CHANGE_HERO_SPENDINGS_TO_SHARPENING_ARTIFACT
    ITEM = ITEMS_OF_EXPENDITURE.SHARPENING_ARTIFACT

class ChangeHeroSpendingsToExperience(ChangeItemOfExpenditureBase):
    TYPE = relations.CARD_TYPE.CHANGE_HERO_SPENDINGS_TO_EXPERIENCE
    ITEM = ITEMS_OF_EXPENDITURE.EXPERIENCE

class ChangeHeroSpendingsToRepairingArtifact(ChangeItemOfExpenditureBase):
    TYPE = relations.CARD_TYPE.CHANGE_HERO_SPENDINGS_TO_REPAIRING_ARTIFACT
    ITEM = ITEMS_OF_EXPENDITURE.REPAIRING_ARTIFACT


class RepairRandomArtifact(CardBase):
    TYPE = relations.CARD_TYPE.REPAIR_RANDOM_ARTIFACT
    DESCRIPTION = u'Чинит случайный артефакт из экиприровки героя.'

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            choices = [item for item in hero.equipment.values() if item.integrity < item.max_integrity]

            if not choices:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, () #TODO: return correct message

            artifact = random.choice(choices)

            artifact.repair_it()

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class RepairAllArtifacts(CardBase):
    TYPE = relations.CARD_TYPE.REPAIR_ALL_ARTIFACTS
    DESCRIPTION = u'Чинит все артефакты из экиприровки героя.'

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            if not [item for item in hero.equipment.values() if item.integrity < item.max_integrity]:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, () #TODO: return correct message

            for item in hero.equipment.values():
                item.repair_it()

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class CancelQuest(CardBase):
    TYPE = relations.CARD_TYPE.CANCEL_QUEST
    DESCRIPTION = u'Отменяет текущее задание героя.'

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            if not hero.quests.has_quests:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, () #TODO: return correct message

            hero.quests.pop_quest()

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class GetArtifactBase(CardBase):
    TYPE = None
    DESCRIPTION = None

    class ARTIFACT_TYPE_CHOICES(DjangoEnum):
        priority = Column()
        rarity = Column(unique=False, single_type=False)

        records = ( ('LOOT', 0, u'лут', 1000, ARTIFACT_RARITY.NORMAL),
                    ('COMMON', 1, u'обычные', 100, ARTIFACT_RARITY.NORMAL),
                    ('RARE', 2, u'редкие', 10, ARTIFACT_RARITY.RARE),
                    ('EPIC', 3, u'эпические', 1, ARTIFACT_RARITY.EPIC), )

    INTERVAL = None

    def get_new_artifact_data(self):
        artifact_type = random_value_by_priority([(record, record.priority) for record in self.ARTIFACT_TYPE_CHOICES.records][-self.INTERVAL:])

        if artifact_type.is_LOOT:
            return artifacts_storage.loot, artifact_type.rarity

        return artifacts_storage.artifacts, artifact_type.rarity

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            artifacts_list, rarity = self.get_new_artifact_data()

            artifact = artifacts_storage.generate_artifact_from_list(artifacts_list, hero.level, rarity=rarity)

            hero.put_loot(artifact)

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class GetArtifactCommon(GetArtifactBase):
    TYPE = relations.CARD_TYPE.GET_ARTIFACT_COMMON
    DESCRIPTION = u'Герой получает случайный бесполезный предмет или артефакт'
    INTERVAL = 4

class GetArtifactUncommon(GetArtifactBase):
    TYPE = relations.CARD_TYPE.GET_ARTIFACT_UNCOMMON
    DESCRIPTION = u'Герой получает случайный артефакт.'
    INTERVAL = 3

class GetArtifactRare(GetArtifactBase):
    TYPE = relations.CARD_TYPE.GET_ARTIFACT_RARE
    DESCRIPTION = u'Герой получает случайный редкий или эпический артефакт.'
    INTERVAL = 2

class GetArtifactEpic(GetArtifactBase):
    TYPE = relations.CARD_TYPE.GET_ARTIFACT_EPIC
    DESCRIPTION = u'Герой получает случайный эпический артефакт.'
    INTERVAL = 1


class InstantMonsterKill(CardBase):
    TYPE = relations.CARD_TYPE.INSTANT_MONSTER_KILL
    DESCRIPTION = u'Мгновенно убивает монстра, с которым сражается герой.'

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            if not hero.actions.current_action.TYPE.is_BATTLE_PVE_1X1:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, () #TODO: return correct message

            hero.actions.current_action.bit_mob(1.01)

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()



class KeepersGoodsBase(CardBase):
    TYPE = None
    GOODS = None

    @property
    def DESCRIPTION(self):
        return u'Создаёт в указанном городе %(goods)d «даров Хранителей». Город будет постепенно переводить их в продукцию, пока дары не кончатся.' % {'goods': self.GOODS}

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


class KeepersGoodsCommon(KeepersGoodsBase):
    TYPE = relations.CARD_TYPE.KEEPERS_GOODS_COMMON
    GOODS = 20

class KeepersGoodsUncommon(KeepersGoodsBase):
    TYPE = relations.CARD_TYPE.KEEPERS_GOODS_UNCOMMON
    GOODS = KeepersGoodsCommon.GOODS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class KeepersGoodsRare(KeepersGoodsBase):
    TYPE = relations.CARD_TYPE.KEEPERS_GOODS_RARE
    GOODS = KeepersGoodsUncommon.GOODS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class KeepersGoodsEpic(KeepersGoodsBase):
    TYPE = relations.CARD_TYPE.KEEPERS_GOODS_EPIC
    GOODS = KeepersGoodsRare.GOODS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class KeepersGoodsLegendary(KeepersGoodsBase):
    TYPE = relations.CARD_TYPE.KEEPERS_GOODS_LEGENDARY
    GOODS = KeepersGoodsEpic.GOODS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)



class RepairBuilding(CardBase):
    TYPE = relations.CARD_TYPE.REPAIR_BUILDING

    DESCRIPTION = u'Полностью ремонтирует указанное строение.'

    def use(self, data, step, main_task_id, storage, highlevel=None, **kwargs): # pylint: disable=R0911,W0613

        building_id = data.get('building_id')

        if building_id not in buildings_storage:
            return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()

        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            return ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL, ((lambda: workers_environment.highlevel.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step.is_HIGHLEVEL:
            building = buildings_storage[building_id]

            while building.need_repair:
                building.repair()

            building.save()

            buildings_storage.update_version()

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()



class PersonPowerBonusBase(CardBase):
    TYPE = None
    BONUS = None

    @property
    def DESCRIPTION(self):
        return u'Увеличивает бонус к начисляемому положительному влиянию соратника героя на %(bonus).1f%%.' % {'bonus': round(self.BONUS*100, 1)}

    def use(self, data, step, main_task_id, storage, highlevel=None, **kwargs): # pylint: disable=R0911,W0613

        person_id = data.get('person_id')

        if person_id not in persons_storage:
            return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()

        person = persons_storage[person_id]

        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            return ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL, ((lambda: workers_environment.highlevel.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step.is_HIGHLEVEL:
            person_id = data.get('person_id')

            person = persons_storage[person_id]

            person.push_power_positive(TimePrototype.get_current_turn_number(), self.BONUS)

            person.save()

            persons_storage.update_version()

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class PersonPowerBonusUncommon(PersonPowerBonusBase):
    TYPE = relations.CARD_TYPE.PERSON_POWER_BONUS_POSITIVE_UNCOMMON
    BONUS = c.HERO_POWER_BONUS / 4

class PersonPowerBonusRare(PersonPowerBonusBase):
    TYPE = relations.CARD_TYPE.PERSON_POWER_BONUS_POSITIVE_RARE
    BONUS = PersonPowerBonusUncommon.BONUS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class PersonPowerBonusEpic(PersonPowerBonusBase):
    TYPE = relations.CARD_TYPE.PERSON_POWER_BONUS_POSITIVE_EPIC
    BONUS = PersonPowerBonusRare.BONUS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class PersonPowerBonusLegendary(PersonPowerBonusBase):
    TYPE = relations.CARD_TYPE.PERSON_POWER_BONUS_POSITIVE_LEGENDARY
    BONUS = PersonPowerBonusEpic.BONUS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)



class PlacePowerBonusBase(CardBase):
    TYPE = None
    BONUS = None

    @property
    def DESCRIPTION(self):
        if self.BONUS > 0:
            return u'Увеличивает бонус к начисляемому положительному влиянию города на %(bonus).1f%%.' % {'bonus': round(self.BONUS*100, 1)}

        return u'Увеличивает бонус к начисляемому негативному влиянию города на %(bonus).1f%%.' % {'bonus': round(self.BONUS*100, 1)}

    def use(self, data, step, main_task_id, storage, highlevel=None, **kwargs): # pylint: disable=R0911,W0613

        place_id = data.get('place_id')

        if place_id not in places_storage:
            return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()

        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            return ComplexChangeTask.RESULT.CONTINUE, ComplexChangeTask.STEP.HIGHLEVEL, ((lambda: workers_environment.highlevel.cmd_logic_task(hero.account_id, main_task_id)), )

        elif step.is_HIGHLEVEL:
            place = places_storage[place_id]

            if self.BONUS > 0:
                place.push_power_positive(TimePrototype.get_current_turn_number(), self.BONUS)
            else:
                place.push_power_negative(TimePrototype.get_current_turn_number(), self.BONUS)

            place.save()

            places_storage.update_version()

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()



class PlacePowerBonusPositiveUncommon(PlacePowerBonusBase):
    TYPE = relations.CARD_TYPE.PLACE_POWER_BONUS_POSITIVE_UNCOMMON
    BONUS = c.HERO_POWER_BONUS / 4

class PlacePowerBonusPositiveRare(PlacePowerBonusBase):
    TYPE = relations.CARD_TYPE.PLACE_POWER_BONUS_POSITIVE_RARE
    BONUS = PlacePowerBonusPositiveUncommon.BONUS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class PlacePowerBonusPositiveEpic(PlacePowerBonusBase):
    TYPE = relations.CARD_TYPE.PLACE_POWER_BONUS_POSITIVE_EPIC
    BONUS = PlacePowerBonusPositiveRare.BONUS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class PlacePowerBonusPositiveLegendary(PlacePowerBonusBase):
    TYPE = relations.CARD_TYPE.PLACE_POWER_BONUS_POSITIVE_LEGENDARY
    BONUS = PlacePowerBonusPositiveEpic.BONUS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)


class PlacePowerBonusNegativeUncommon(PlacePowerBonusBase):
    TYPE = relations.CARD_TYPE.PLACE_POWER_BONUS_NEGATIVE_UNCOMMON
    BONUS = c.HERO_POWER_BONUS / 4

class PlacePowerBonusNegativeRare(PlacePowerBonusBase):
    TYPE = relations.CARD_TYPE.PLACE_POWER_BONUS_NEGATIVE_RARE
    BONUS = PlacePowerBonusNegativeUncommon.BONUS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class PlacePowerBonusNegativeEpic(PlacePowerBonusBase):
    TYPE = relations.CARD_TYPE.PLACE_POWER_BONUS_NEGATIVE_EPIC
    BONUS = PlacePowerBonusNegativeRare.BONUS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class PlacePowerBonusNegativeLegendary(PlacePowerBonusBase):
    TYPE = relations.CARD_TYPE.PLACE_POWER_BONUS_NEGATIVE_LEGENDARY
    BONUS = PlacePowerBonusNegativeEpic.BONUS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)


class HelpPlaceBase(CardBase):
    TYPE = None
    HELPS = None

    @property
    def DESCRIPTION(self):
        if self.HELPS > 0:
            return u'В документах города появляются %(helps)d дополнительные записи о помощи, полученной от героя.' % {'helps': self.HELPS}
        return u'В документах города появляется дополнительная запись о помощи, полученной от героя.'

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            place_id = data.get('place_id')

            if place_id not in places_storage:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()

            for i in xrange(self.HELPS):
                hero.places_history.add_place(place_id)

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class HelpPlaceUncommon(HelpPlaceBase):
    TYPE = relations.CARD_TYPE.MOST_COMMON_PLACES_UNCOMMON
    HELPS = 1

class HelpPlaceRare(HelpPlaceBase):
    TYPE = relations.CARD_TYPE.MOST_COMMON_PLACES_RARE
    HELPS =  HelpPlaceUncommon.HELPS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class HelpPlaceEpic(HelpPlaceBase):
    TYPE = relations.CARD_TYPE.MOST_COMMON_PLACES_EPIC
    HELPS =  HelpPlaceRare.HELPS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)

class HelpPlaceLegendary(HelpPlaceBase):
    TYPE = relations.CARD_TYPE.MOST_COMMON_PLACES_LEGENDARY
    HELPS =  HelpPlaceEpic.HELPS * (c.CARDS_COMBINE_TO_UP_RARITY + 1)


class ShortTeleport(CardBase):
    TYPE = relations.CARD_TYPE.SHORT_TELEPORT

    DESCRIPTION = u'Телепортируе героя до ближайшего города либо до ближайшей ключевой точки задания. Работает только во время движения по дорогам.'

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            if not hero.actions.current_action.TYPE.is_MOVE_TO:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, () #TODO: return correct message

            if not hero.actions.current_action.teleport_to_place():
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, () #TODO: return correct message

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class LongTeleport(CardBase):
    TYPE = relations.CARD_TYPE.LONG_TELEPORT

    DESCRIPTION = u'Телепортируе героя в конечную точку назначения либо до ближайшей ключевой точки задания. Работает только во время движения по дорогам.'

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            if not hero.actions.current_action.TYPE.is_MOVE_TO:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, () #TODO: return correct message

            if not hero.actions.current_action.teleport_to_end():
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, () #TODO: return correct message

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class ExperienceToEnergyBase(CardBase):
    TYPE = None
    EXPERIENCE = None

    @property
    def DESCRIPTION(self):
        return u'Преобразует опыт героя на текущем уровне в дополнительную энергию по курсу %(experience)s единиц опыта за единицу энергии.' % {'experience': self.EXPERIENCE}

    def use(self, data, step, main_task_id, storage, **kwargs): # pylint: disable=R0911,W0613
        if step.is_LOGIC:
            hero = storage.heroes[data['hero_id']]

            if hero.experience == 0:
                return ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()

            hero.convert_experience_to_energy(self.EXPERIENCE)

            return ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()


class ExperienceToEnergyUncommon(ExperienceToEnergyBase):
    TYPE = relations.CARD_TYPE.EXPERIENCE_TO_ENERGY_UNCOMMON
    EXPERIENCE = 50

class ExperienceToEnergyRare(ExperienceToEnergyBase):
    TYPE = relations.CARD_TYPE.EXPERIENCE_TO_ENERGY_RARE
    EXPERIENCE = 40

class ExperienceToEnergyEpic(ExperienceToEnergyBase):
    TYPE = relations.CARD_TYPE.EXPERIENCE_TO_ENERGY_EPIC
    EXPERIENCE = 30

class ExperienceToEnergyLegendary(ExperienceToEnergyBase):
    TYPE = relations.CARD_TYPE.EXPERIENCE_TO_ENERGY_LEGENDARY
    EXPERIENCE = 20


CARDS = {card_class.TYPE: card_class()
         for card_class in discovering.discover_classes(globals().values(), CardBase)
         if card_class.TYPE is not None}
