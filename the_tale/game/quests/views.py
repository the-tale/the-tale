# coding: utf-8

from dext.views import handler

from common.utils.resources import Resource
from common.utils.decorators import login_required
from common.postponed_tasks import PostponedTaskPrototype

from game.workers.environment import workers_environment

from game.quests.postponed_tasks import MakeChoiceTask


class QuestsResource(Resource):

    @login_required
    def initialize(self, *argv, **kwargs):
        super(QuestsResource, self).initialize(*argv, **kwargs)

    @handler('choose', method='post')
    def choose(self, choice_uid, option_uid):

        choose_task = MakeChoiceTask(account_id=self.account.id, choice_uid=choice_uid, option_uid=option_uid)

        task = PostponedTaskPrototype.create(choose_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(status_url=task.status_url)
