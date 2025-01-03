
import smart_imports

smart_imports.all()


class QuestsResource(utils_resources.Resource):

    @utils_decorators.login_required
    def initialize(self, *argv, **kwargs):
        super(QuestsResource, self).initialize(*argv, **kwargs)

    @accounts_views.validate_operation_disabled_game_stopped()
    @utils_api.handler(versions=('1.0',))
    @old_views.handler('api', 'choose', name='api-choose', method='post')
    def api_choose(self, option_uid, api_version):
        choose_task = postponed_tasks.MakeChoiceTask(account_id=self.account.id, option_uid=option_uid)

        task = PostponedTaskPrototype.create(choose_task)

        amqp_environment.environment.workers.supervisor.cmd_logic_task(self.account.id, task.id)

        return self.processing(status_url=task.status_url)
