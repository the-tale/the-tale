# coding: utf-8

from ...actions.prototypes import ActionIdlenessPrototype

from ..prototypes import AbilityPrototype

attrs = None

class GetQuest(AbilityPrototype):

    LIMITED = False
    INITIAL_LIMIT = None

    COST = 3
    COOLDOWN = 50

    NAME = u'Простимулировать'
    DESCRIPTION = u'Заставить героя взяться за работу'
    ARTISTIC = u'Существует много способов принудить героя взять квест: можно уговорить, а можено и молнией приложиться'

    FORM = None
    TEMPLATE = None

    def use(self, bundle, angel, hero, form):

        idleness_action = bundle.current_hero_action(hero.id)

        if idleness_action.type != ActionIdlenessPrototype.TYPE:
            return False

        if not idleness_action.init_quest():
            return False

        hero.add_message('angel_ability_stimulate', hero=hero)

        return True
