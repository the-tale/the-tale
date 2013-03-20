# coding: utf-8

from dext.views import handler

from common.utils.resources import Resource
from common.utils.decorators import login_required
from common.postponed_tasks import PostponedTaskPrototype

from game.workers.environment import workers_environment

from game.quests.postponed_tasks import ChooseQuestLineTask


class QuestsResource(Resource):

    @login_required
    def initialize(self, quest_id=None, *argv, **kwargs):
        super(QuestsResource, self).initialize(*argv, **kwargs)
        self.quest_id = int(quest_id)


    @handler('#quest_id', 'choose', method='post')
    def choose(self, choice_point, choice):

        choose_task = ChooseQuestLineTask(account_id=self.account.id, quest_id=self.quest_id, choice_point=choice_point, choice=choice)

        task = PostponedTaskPrototype.create(choose_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(status_url=task.status_url)
