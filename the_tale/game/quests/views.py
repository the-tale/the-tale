# coding: utf-8

from dext.views import handler
from dext.utils import cache

from common.utils.resources import Resource
from common.utils.decorators import login_required

from game.heroes.prototypes import HeroPrototype

from .prototypes import get_quest_by_id

class QuestsResource(Resource):

    @login_required
    def initialize(self, quest_id=None, *argv, **kwargs):
        super(QuestsResource, self).initialize(*argv, **kwargs)

        self.quest_id = int(quest_id)

        if self.quest is None:
            return self.json_error('quests.no_quest', u'Вы не можете работать с этим квестом')

        if self.account.id not in self.quest.accounts_ids():
            return self.json_error('quests.wrong_account', u'Вы не можете работать с этим квестом')

    @property
    def quest(self):
        if not hasattr(self, '_quest'):
            self._quest = get_quest_by_id(self.quest_id)
        return self._quest

    @handler('#quest_id', 'choose', method='post')
    def choose(self, choice_point, choice):

        cmd = self.quest.env.get_nearest_quest_choice(self.quest.pointer)

        if cmd is None or choice not in cmd.choices:
            return self.json_error('quests.choose.unknown_choice', u'Не существует такого выбора')

        if cmd is None or cmd.id != choice_point:
            return self.json_error('quests.choose.wrong_point', u'В данный момент вы не можете влиять на эту точку выбора')

        if not self.quest.is_choice_available(cmd.choices[choice]):
            return self.json_error('quests.choose.line_not_availbale', u'Характер не позволяет герою сделать такой выбор')

        if not self.quest.make_choice(choice_point, choice):
            return self.json_error('quests.choose.already_choosed', u'Вы уже сделали выбор')

        #reset here cache cache
        for hero_id in self.quest.heroes_ids():
            cache.delete(HeroPrototype.get_by_id(hero_id).cached_ui_info_key)

        return self.json(status='ok')
