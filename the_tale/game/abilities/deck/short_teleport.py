# coding: utf-8

from ..prototypes import AbilityPrototype
from ...actions.prototypes import ActionMoveToPrototype

attrs = None

class ShortTeleport(AbilityPrototype):

    LIMITED = False
    INITIAL_LIMIT = None

    COST = 10
    COOLDOWN = 10

    NAME = u'Подтолкнуть'
    DESCRIPTION = u'Телепортировать героя на короткое расстояние'
    ARTISTIC = u'Маленький толчёк, и ваш подопечный уже влетает в дереве в нескольких километрах впереди.'

    FORM = None
    TEMPLATE = None
      
    def use(self, bundle, angel, hero, form):
        move_action = bundle.current_hero_action(hero.id)

        if move_action.type != ActionMoveToPrototype.TYPE:
            return False

        if not move_action.short_teleport(10):
            return False

        hero.create_tmp_log_message('You teleport hero for %d km' % 10 )

        return True


