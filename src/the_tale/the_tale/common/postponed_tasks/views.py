
import smart_imports

smart_imports.all()


class PostponedTaskResource(utils_resources.Resource):

    @dext_old_views.validate_argument('task', PostponedTaskPrototype.get_by_id, 'postponed_task', 'Задача не найдена')
    def initialize(self, task, *args, **kwargs):
        super(PostponedTaskResource, self).initialize(*args, **kwargs)
        self.task = task

    @dext_old_views.handler('#task', 'status', method='get')
    def status(self):  # pylint: disable=R0911
        if self.task.state.is_waiting:
            return self.json_processing(django_reverse('postponed-tasks:status', args=[self.task.id]))

        if self.task.state.is_processed:
            self.task.internal_logic.processed_view(self)
            return self.json_ok(data=self.task.internal_logic.processed_data)

        if self.task.state.is_reseted:
            return self.json_error('postponed_task.task_reseted', 'Обработка задачи отменена')

        if self.task.state.is_timeout:
            return self.json_error('postponed_task.timeout', 'Превышено время обработки задачи, попробуйте ещё раз')

        if self.task.state.is_error:
            return self.json_error('postponed_task.error', self.task.internal_logic.error_message)

        if self.task.state.is_exception:
            return self.json_error('postponed_task.exception', 'Неизвестная ошибка, повторите попытку позже')

        return self.json_error('postponed_task.unknown_error', 'Неизвестная ошибка, повторите попытку позже')

    @dext_old_views.handler('#task', 'wait', method='get')
    def wait(self):
        return self.template('postponed_tasks/wait.html',
                             {'task': self.task})
