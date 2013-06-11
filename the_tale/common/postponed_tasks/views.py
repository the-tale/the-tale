# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument

from common.utils.resources import Resource

from common.postponed_tasks.prototypes import PostponedTaskPrototype


class PostponedTaskResource(Resource):

    @validate_argument('task', PostponedTaskPrototype.get_by_id, 'postponed_task', u'Задача не найдена')
    def initialize(self, task, *args, **kwargs):
        super(PostponedTaskResource, self).initialize(*args, **kwargs)
        self.task = task

    @handler('#task', 'status', method='get')
    def status(self): # pylint: disable=R0911
        if self.task.state.is_waiting:
            return self.json_processing(reverse('postponed-tasks:status', args=[self.task.id]))

        if self.task.state.is_processed:
            self.task.internal_logic.processed_view(self)
            return self.json_ok(data=self.task.internal_logic.processed_data)

        if self.task.state.is_reseted:
            return self.json_error('postponed_task.task_reseted', u'Обработка задачи отменена')

        if self.task.state.is_timeout:
            return self.json_error('postponed_task.timeout', u'Превышено время обработки задачи, попробуйте ещё раз')

        if self.task.state.is_error:
            return self.json_error('postponed_task.error', self.task.internal_logic.error_message)

        if self.task.state.is_exception:
            return self.json_error('postponed_task.exception', u'Неизвестная ошибка, повторите попытку позже')

        return self.json_error('postponed_task.unknown_error', u'Неизвестная ошибка, повторите попытку позже')

    @handler('#task', 'wait', method='get')
    def wait(self):
        return self.template('postponed_tasks/wait.html',
                             {'task': self.task})
