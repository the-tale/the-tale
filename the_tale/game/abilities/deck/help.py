# coding: utf-8
import math
import random

from the_tale.game.heroes.relations import MONEY_SOURCE, HABIT_CHANGE_SOURCE

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE

from the_tale.game.balance import constants as c, formulas as f

from the_tale.game.pvp.prototypes import Battle1x1Prototype

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.postponed_tasks import ComplexChangeTask

from the_tale.game.abilities import exceptions


class Help(AbilityPrototype):
    TYPE = ABILITY_TYPE.HELP

    def use_heal(self, task, action, hero, critical):
        if critical:
            heal_amount = int(hero.heal(hero.max_health * random.uniform(*c.ANGEL_HELP_CRIT_HEAL_FRACTION)))
            hero.add_message('angel_ability_healhero_crit', hero=hero, health=heal_amount)
        else:
            heal_amount = int(hero.heal(hero.max_health * random.uniform(*c.ANGEL_HELP_HEAL_FRACTION)))
            hero.add_message('angel_ability_healhero', hero=hero, health=heal_amount)
        action.on_heal()
        return task.logic_result(next_step=ComplexChangeTask.STEP.SUCCESS)

    def use_start_quest(self, task, action, hero, critical): # pylint: disable=W0613
        action.init_quest()
        hero.add_message('angel_ability_stimulate', hero=hero)
        return task.logic_result(next_step=ComplexChangeTask.STEP.SUCCESS)

    def use_money(self, task, action, hero, critical): # pylint: disable=W0613
        multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)
        coins = int(math.ceil(f.normal_loot_cost_at_lvl(hero.level) * multiplier))


        if critical:
            coins *= c.ANGEL_HELP_CRIT_MONEY_MULTIPLIER
            hero.change_money(MONEY_SOURCE.EARNED_FROM_HELP, coins)
            hero.add_message('angel_ability_money_crit', hero=hero, coins=coins)
        else:
            hero.change_money(MONEY_SOURCE.EARNED_FROM_HELP, coins)
            hero.add_message('angel_ability_money', hero=hero, coins=coins)
        return task.logic_result(next_step=ComplexChangeTask.STEP.SUCCESS)

    def use_teleport(self, task, action, hero, critical):
        if critical:
            action.teleport(c.ANGEL_HELP_CRIT_TELEPORT_DISTANCE, create_inplace_action=True)
            hero.add_message('angel_ability_shortteleport_crit', hero=hero)
        else:
            action.teleport(c.ANGEL_HELP_TELEPORT_DISTANCE, create_inplace_action=True)
            hero.add_message('angel_ability_shortteleport', hero=hero)
        return task.logic_result(next_step=ComplexChangeTask.STEP.SUCCESS)

    def use_lightning(self, task, action, hero, critical):
        if critical:
            action.bit_mob(random.uniform(*c.ANGEL_HELP_CRIT_LIGHTING_FRACTION))
            hero.add_message('angel_ability_lightning_crit', hero=hero, mob=action.mob)
        else:
            action.bit_mob(random.uniform(*c.ANGEL_HELP_LIGHTING_FRACTION))
            hero.add_message('angel_ability_lightning', hero=hero, mob=action.mob)
        return task.logic_result(next_step=ComplexChangeTask.STEP.SUCCESS)

    def use_resurrect(self, task, action, hero, critical): # pylint: disable=W0613
        if hero.is_alive:
            return (ComplexChangeTask.RESULT.IGNORE, ComplexChangeTask.STEP.SUCCESS, ())
        action.fast_resurrect()
        hero.add_message('angel_ability_resurrect', hero=hero)
        return task.logic_result(next_step=ComplexChangeTask.STEP.SUCCESS)

    def use_experience(self, task, action, hero, critical): # pylint: disable=W0613

        if critical:
            experience = int(c.ANGEL_HELP_CRIT_EXPERIENCE * (1 + random.uniform(-c.ANGEL_HELP_EXPERIENCE_DELTA, c.ANGEL_HELP_EXPERIENCE_DELTA))+ 1)
            real_experience = hero.add_experience(experience)
            hero.add_message('angel_ability_experience_crit', hero=hero, experience=real_experience)
        else:
            experience = int(c.ANGEL_HELP_EXPERIENCE * (1 + random.uniform(-c.ANGEL_HELP_EXPERIENCE_DELTA, c.ANGEL_HELP_EXPERIENCE_DELTA))+ 1)
            real_experience = hero.add_experience(experience)
            hero.add_message('angel_ability_experience', hero=hero, experience=real_experience)

        return task.logic_result(next_step=ComplexChangeTask.STEP.SUCCESS)

    def use_heal_companion(self, task, action, hero, critical): # pylint: disable=W0613

        if hero.companion is None:
            return task.logic_result(next_step=ComplexChangeTask.STEP.ERROR)

        if hero.companion.health == hero.companion.max_health:
            return task.logic_result(next_step=ComplexChangeTask.STEP.ERROR)

        if critical:
            health = hero.companion.heal(c.COMPANIONS_HEAL_CRIT_AMOUNT)
            hero.add_message('angel_ability_heal_companion_crit', hero=hero, companion=hero.companion, health=health)
        else:
            health = hero.companion.heal(c.COMPANIONS_HEAL_AMOUNT)
            hero.add_message('angel_ability_heal_companion', hero=hero, companion=hero.companion, health=health)

        action.on_heal_companion()

        return task.logic_result(next_step=ComplexChangeTask.STEP.SUCCESS)

    def use_stock_up_energy(self, task, action, hero, critical): # pylint: disable=W0613

        if critical:
            energy = c.ANGEL_FREE_ENERGY_CHARGE_CRIT
            hero.add_message('angel_ability_stock_up_energy_crit', hero=hero, energy=energy)
        else:
            energy = c.ANGEL_FREE_ENERGY_CHARGE
            hero.add_message('angel_ability_stock_up_energy', hero=hero, energy=energy)

        hero.add_energy_bonus(energy)

        return task.logic_result(next_step=ComplexChangeTask.STEP.SUCCESS)

    def _use(self, task, choice, action, hero, critical):
        if choice.is_HEAL:
            return self.use_heal(task, action, hero, critical)

        elif choice.is_START_QUEST:
            return self.use_start_quest(task, action, hero, critical)

        elif choice.is_MONEY:
            return self.use_money(task, action, hero, critical)

        elif choice.is_TELEPORT:
            return self.use_teleport(task, action, hero, critical)

        elif choice.is_LIGHTING:
            return self.use_lightning(task, action, hero, critical)

        elif choice.is_RESURRECT:
            return self.use_resurrect(task, action, hero, critical)

        elif choice.is_EXPERIENCE:
            return self.use_experience(task, action, hero, critical)

        elif choice.is_STOCK_UP_ENERGY:
            return self.use_stock_up_energy(task, action, hero, critical)

        elif choice.is_HEAL_COMPANION:
            return self.use_heal_companion(task, action, hero, critical)


    def process_removed_artifacts(self, hero):
        for artifact in hero.bag.values():
            if artifact.must_be_removed_on_help():
                hero.bag.pop_artifact(artifact)

                if artifact.is_child_gift():
                    hero.statistics.change_gifts_returned(1)
                    hero.add_message('hero_common_journal_return_child_gift', hero=hero, artifact=artifact)

    def use(self, task, storage, **kwargs): # pylint: disable=R0911

        battle = Battle1x1Prototype.get_by_account_id(task.hero.account_id)

        if battle and not battle.state.is_WAITING:
            return task.logic_result(next_step=ComplexChangeTask.STEP.ERROR)

        action = task.hero.actions.current_action

        choice = action.get_help_choice()

        if choice is None:
            return task.logic_result(next_step=ComplexChangeTask.STEP.ERROR)

        if action.HABIT_MODE.is_AGGRESSIVE:
            task.hero.update_habits(HABIT_CHANGE_SOURCE.HELP_AGGRESSIVE)
        elif action.HABIT_MODE.is_PEACEFUL:
            task.hero.update_habits(HABIT_CHANGE_SOURCE.HELP_UNAGGRESSIVE)
        elif action.HABIT_MODE.is_COMPANION:
            if task.hero.companion:
                for habit_source in task.hero.companion.modify_attribute(heroes_relations.MODIFIERS.HABITS_SOURCES, set()):
                    task.hero.update_habits(habit_source)
        else:
            raise exceptions.UnknownHabitModeError(mode=action.HABIT_MODE)

        critical = random.uniform(0, 1) < task.hero.might_crit_chance

        result = self._use(task, choice, action, task.hero, critical)

        if result[0].is_SUCCESSED:
            task.hero.statistics.change_help_count(1)

            if task.hero.actions.current_action.state == task.hero.actions.current_action.STATE.PROCESSED:
                storage.process_turn__single_hero(hero=task.hero,
                                                  logger=None,
                                                  continue_steps_if_needed=True)

        task.hero.cards.change_help_count(1)

        self.process_removed_artifacts(task.hero)

        return result
