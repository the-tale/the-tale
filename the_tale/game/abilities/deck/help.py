# coding: utf-8
import random

from the_tale.game.heroes.relations import MONEY_SOURCE, HABIT_CHANGE_SOURCE

from the_tale.game.abilities.prototypes import AbilityPrototype
from the_tale.game.abilities.relations import ABILITY_TYPE, ABILITY_RESULT

from the_tale.game.balance import constants as c, formulas as f

from the_tale.game.pvp.prototypes import Battle1x1Prototype


class Help(AbilityPrototype):
    TYPE = ABILITY_TYPE.HELP

    def use_heal(self, action, hero, critical):
        if critical:
            heal_amount = int(hero.heal(hero.max_health * random.uniform(*c.ANGEL_HELP_CRIT_HEAL_FRACTION)))
            hero.add_message('angel_ability_healhero_crit', hero=hero, health=heal_amount)
        else:
            heal_amount = int(hero.heal(hero.max_health * random.uniform(*c.ANGEL_HELP_HEAL_FRACTION)))
            hero.add_message('angel_ability_healhero', hero=hero, health=heal_amount)
        action.on_heal()
        return (ABILITY_RESULT.SUCCESSED, None, ())

    def use_start_quest(self, action, hero, critical): # pylint: disable=W0613
        action.init_quest()
        hero.add_message('angel_ability_stimulate', hero=hero)
        return (ABILITY_RESULT.SUCCESSED, None, ())

    def use_money(self, action, hero, critical): # pylint: disable=W0613
        multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)
        coins = int(f.normal_loot_cost_at_lvl(hero.level) * multiplier)

        if critical:
            coins *= c.ANGEL_HELP_CRIT_MONEY_MULTIPLIER
            hero.change_money(MONEY_SOURCE.EARNED_FROM_HELP, coins)
            hero.add_message('angel_ability_money_crit', hero=hero, coins=coins)
        else:
            hero.change_money(MONEY_SOURCE.EARNED_FROM_HELP, coins)
            hero.add_message('angel_ability_money', hero=hero, coins=coins)
        return (ABILITY_RESULT.SUCCESSED, None, ())

    def use_teleport(self, action, hero, critical):
        if critical:
            action.short_teleport(c.ANGEL_HELP_CRIT_TELEPORT_DISTANCE)
            hero.add_message('angel_ability_shortteleport_crit', hero=hero)
        else:
            action.short_teleport(c.ANGEL_HELP_TELEPORT_DISTANCE)
            hero.add_message('angel_ability_shortteleport', hero=hero)
        return (ABILITY_RESULT.SUCCESSED, None, ())

    def use_lightning(self, action, hero, critical):
        if critical:
            action.bit_mob(random.uniform(*c.ANGEL_HELP_CRIT_LIGHTING_FRACTION))
            hero.add_message('angel_ability_lightning_crit', hero=hero, mob=action.mob)
        else:
            action.bit_mob(random.uniform(*c.ANGEL_HELP_LIGHTING_FRACTION))
            hero.add_message('angel_ability_lightning', hero=hero, mob=action.mob)
        return (ABILITY_RESULT.SUCCESSED, None, ())

    def use_resurrect(self, action, hero, critical): # pylint: disable=W0613
        if hero.is_alive:
            return (ABILITY_RESULT.IGNORE, None, ())
        action.fast_resurrect()
        hero.add_message('angel_ability_resurrect', hero=hero)
        return (ABILITY_RESULT.SUCCESSED, None, ())

    def use_experience(self, action, hero, critical): # pylint: disable=W0613

        if critical:
            experience = int(c.ANGEL_HELP_CRIT_EXPERIENCE * (1 + random.uniform(-c.ANGEL_HELP_EXPERIENCE_DELTA, c.ANGEL_HELP_EXPERIENCE_DELTA))+ 1)
            real_experience = hero.add_experience(experience)
            hero.add_message('angel_ability_experience_crit', hero=hero, experience=real_experience)
        else:
            experience = int(c.ANGEL_HELP_EXPERIENCE * (1 + random.uniform(-c.ANGEL_HELP_EXPERIENCE_DELTA, c.ANGEL_HELP_EXPERIENCE_DELTA))+ 1)
            real_experience = hero.add_experience(experience)
            hero.add_message('angel_ability_experience', hero=hero, experience=real_experience)

        return (ABILITY_RESULT.SUCCESSED, None, ())

    def use_stock_up_energy(self, action, hero, critical): # pylint: disable=W0613

        if critical:
            energy = c.ANGEL_FREE_ENERGY_CHARGE_CRIT
            hero.add_message('angel_ability_stock_up_energy_crit', hero=hero, energy=energy)
        else:
            energy = c.ANGEL_FREE_ENERGY_CHARGE
            hero.add_message('angel_ability_stock_up_energy', hero=hero, energy=energy)

        hero.add_energy_bonus(energy)

        return (ABILITY_RESULT.SUCCESSED, None, ())

    def use(self, data, storage, **kwargs): # pylint: disable=R0911

        hero = storage.heroes[data['hero_id']]

        battle = Battle1x1Prototype.get_by_account_id(hero.account_id)

        if battle and not battle.state.is_WAITING:
            return (ABILITY_RESULT.FAILED, None, ())

        action = hero.actions.current_action

        choice = action.get_help_choice()

        if choice is None:
            return (ABILITY_RESULT.FAILED, None, ())

        if action.AGGRESSIVE:
            hero.update_habits(HABIT_CHANGE_SOURCE.HELP_AGGRESSIVE)
        else:
            hero.update_habits(HABIT_CHANGE_SOURCE.HELP_UNAGGRESSIVE)

        critical = random.uniform(0, 1) < hero.might_crit_chance

        if choice.is_HEAL:
            return self.use_heal(action, hero, critical)

        elif choice.is_START_QUEST:
            return self.use_start_quest(action, hero, critical)

        elif choice.is_MONEY:
            return self.use_money(action, hero, critical)

        elif choice.is_TELEPORT:
            return self.use_teleport(action, hero, critical)

        elif choice.is_LIGHTING:
            return self.use_lightning(action, hero, critical)

        elif choice.is_RESURRECT:
            return self.use_resurrect(action, hero, critical)

        elif choice.is_EXPERIENCE:
            return self.use_experience(action, hero, critical)

        elif choice.is_STOCK_UP_ENERGY:
            return self.use_stock_up_energy(action, hero, critical)
