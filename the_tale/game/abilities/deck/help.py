# coding: utf-8
import random

from game.heroes.statistics import MONEY_SOURCE

from game.abilities.prototypes import AbilityPrototype

from game.balance import constants as c, formulas as f

from game.pvp.prototypes import Battle1x1Prototype

class Help(AbilityPrototype):

    COST = 4

    COMMAND_PREFIX = 'help'

    NAME = u'Помочь'
    DESCRIPTION = u'Попытаться помочь герою, чем бы тот не занимался'

    def use(self, data, step, main_task_id, storage, **kwargs):

        hero = storage.heroes[data['hero_id']]

        battle = Battle1x1Prototype.get_by_account_id(hero.account_id)

        if battle and not battle.state._is_WAITING:
            return False, None, ()

        action = storage.current_hero_action(hero.id)

        choice = action.get_help_choice()

        critical = random.uniform(0, 1) < hero.might_crit_chance

        if choice == c.HELP_CHOICES.HEAL:
            if critical:
                heal_amount = int(hero.heal(hero.max_health * random.uniform(*c.ANGEL_HELP_CRIT_HEAL_FRACTION)))
                hero.add_message('angel_ability_healhero_crit', hero=hero, health=heal_amount)
            else:
                heal_amount = int(hero.heal(hero.max_health * random.uniform(*c.ANGEL_HELP_HEAL_FRACTION)))
                hero.add_message('angel_ability_healhero', hero=hero, health=heal_amount)
            action.on_heal()
            return True, None, ()

        if choice == c.HELP_CHOICES.START_QUEST:
            action.init_quest()
            hero.add_message('angel_ability_stimulate', hero=hero)
            return True, None, ()

        if choice == c.HELP_CHOICES.MONEY:
            multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)
            coins = int(f.normal_loot_cost_at_lvl(hero.level) * multiplier)

            if critical:
                coins *= c.ANGEL_HELP_CRIT_MONEY_MULTIPLIER
                hero.change_money(MONEY_SOURCE.EARNED_FROM_HELP, coins)
                hero.add_message('angel_ability_money_crit', hero=hero, coins=coins)
            else:
                hero.change_money(MONEY_SOURCE.EARNED_FROM_HELP, coins)
                hero.add_message('angel_ability_money', hero=hero, coins=coins)
            return True, None, ()

        if choice == c.HELP_CHOICES.TELEPORT:
            if critical:
                action.short_teleport(c.ANGEL_HELP_CRIT_TELEPORT_DISTANCE)
                hero.add_message('angel_ability_shortteleport_crit', hero=hero)
            else:
                action.short_teleport(c.ANGEL_HELP_TELEPORT_DISTANCE)
                hero.add_message('angel_ability_shortteleport', hero=hero)
            return True, None, ()

        if choice == c.HELP_CHOICES.LIGHTING:
            if critical:
                action.bit_mob(random.uniform(*c.ANGEL_HELP_CRIT_LIGHTING_FRACTION))
                hero.add_message('angel_ability_lightning_crit', hero=hero, mob=action.mob)
            else:
                action.bit_mob(random.uniform(*c.ANGEL_HELP_LIGHTING_FRACTION))
                hero.add_message('angel_ability_lightning', hero=hero, mob=action.mob)
            return True, None, ()

        if choice == c.HELP_CHOICES.RESURRECT:
            action.fast_resurrect()
            hero.add_message('angel_ability_resurrect', hero=hero)
            return True, None, ()

        return False, None, ()
