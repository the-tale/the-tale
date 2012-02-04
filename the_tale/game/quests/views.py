# coding: utf-8

from dext.views.resources import handler
from dext.utils.exceptions import Error

from common.utils.resources import Resource

from .prototypes import get_quest_by_id

class QuestsResource(Resource):

    def __init__(self, request, quest_id=None, *argv, **kwargs):
        super(QuestsResource, self).__init__(request, *argv, **kwargs)
        
        self.quest_id = int(quest_id)

        from ..heroes.prototypes import get_hero_by_id

        if self.quest is None or self.angel.id != get_hero_by_id(self.quest.hero_id).angel_id:
            raise Error(u'Вы не работать с этим квестом')

    @property
    def quest(self):
        if not hasattr(self, '_quest'):
            self._quest = get_quest_by_id(self.quest_id)
        return self._quest

    @handler('#quest_id', 'choose', method='post')
    def choose(self, subquest, choice_point, choice):

        cmd = self.quest.env.get_nearest_quest_choice(self.quest.pointer)

        if cmd.id != choice_point:
            return self.json(status='error', errors=u'В данный момент вы не можете влиять на эту точку выбора')

        if choice not in cmd.choices:
            return self.json(status='error', errors=u'Не существует такого выбора')

        if not self.quest.make_choice(choice_point, choice):
            return self.json(status='error', errors=u'Вы уже сделали выбор')

        return self.json(status='ok')
