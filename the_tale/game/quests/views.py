# coding: utf-8

from dext.views import handler

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required
from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.game.workers.environment import workers_environment

from the_tale.game.quests.postponed_tasks import MakeChoiceTask


class QuestsResource(Resource):

    @login_required
    def initialize(self, *argv, **kwargs):
        super(QuestsResource, self).initialize(*argv, **kwargs)

    @handler('choose', method='post')
    def choose(self, option_uid):

        choose_task = MakeChoiceTask(account_id=self.account.id, option_uid=option_uid)

        task = PostponedTaskPrototype.create(choose_task)

        workers_environment.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.json_processing(status_url=task.status_url)
