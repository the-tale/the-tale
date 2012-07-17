# coding: utf-8
import random

from game.heroes.statistics import MONEY_SOURCE

from game.abilities.prototypes import AbilityPrototype

from game.actions.prototypes import HELP_CHOICES

from game.balance import constants as c, formulas as f

class Help(AbilityPrototype):

    COST = 4

    NAME = u'Помочь'
    DESCRIPTION = u'Попытаться помочь герою, чем бы тот не занимался'
    ARTISTIC = u'Помощь, конечно, хорошо, но главное - не переусердствовать'

    def use(self, bundle, angel, hero, form):
        action = bundle.current_hero_action(hero.id)

        choice = action.get_help_choice()

        if choice == HELP_CHOICES.HEAL:
            heal_amount = hero.heal(hero.max_health * random.uniform(*c.ANGEL_HELP_HEAL_FRACTION))
            hero.add_message('angel_ability_healhero', hero=hero, health=heal_amount)
            return True

        if choice == HELP_CHOICES.START_QUEST:
            action.init_quest()
            hero.add_message('angel_ability_stimulate', hero=hero)
            return True

        if choice == HELP_CHOICES.MONEY:
            multiplier = 1+random.uniform(-c.PRICE_DELTA, c.PRICE_DELTA)
            coins = int(f.normal_loot_cost_at_lvl(hero.level) * multiplier)
            hero.change_money(MONEY_SOURCE.EARNED_FROM_HELP, coins)
            hero.add_message('angel_ability_money', hero=hero, coins=coins)
            return True

        if choice == HELP_CHOICES.TELEPORT:
            action.short_teleport(c.ANGEL_HELP_TELEPORT_DISTANCE)
            hero.add_message('angel_ability_shortteleport', hero=hero)
            return True

        if choice == HELP_CHOICES.LIGHTING:
            action.bit_mob(random.uniform(*c.ANGEL_HELP_LIGHTING_FRACTION))
            hero.add_message('angel_ability_lightning', hero=hero, mob=action.mob)
            return True

        if choice == HELP_CHOICES.RESURRECT:
            action.fast_resurrect()
            hero.add_message('angel_ability_resurrect', hero=hero)
            return True

        return False
