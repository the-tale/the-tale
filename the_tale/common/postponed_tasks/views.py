# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler

from common.utils.resources import Resource

from common.postponed_tasks.prototypes import PostponedTaskPrototype


class PostponedTaskResource(Resource):

    def initialize(self, task_id, *args, **kwargs):
        super(PostponedTaskResource, self).initialize(*args, **kwargs)

        try:
            task_id = int(task_id)
        except:
            return self.auto_error('postponed_task.wrong_task_id', u'Неверный иденификатор задачи', status_code=404)

        self.task = PostponedTaskPrototype.get_by_id(task_id)

        if self.task is None:
            return self.auto_error('postponed_task.task_no_found', u'Задача не найдена', status_code=404)


    @handler('#task_id', 'status', method='get')
    def status(self):

        if self.task.state.is_waiting:
            return self.json_processing(reverse('postponed-tasks:status', args=[self.task.id]))

        if self.task.state.is_processed:
            return self.json_ok(data=self.task.internal_logic.response_data)

        if self.task.state.is_reseted:
            return self.json_error('postponed_task.task_reseted', u'Обработка задачи отменена')

        if self.task.state.is_timeout:
            return self.json_error('postponed_task.timeout', u'Превышено время обработки задачи, попробуйте ещё раз')

        if self.task.state.is_error:
            return self.json_error('postponed_task.error', self.task.internal_logic.error_message)

        if self.task.state.is_exception:
            return self.json_error('postponed_task.exception', u'Неизвестная ошибка, повторите попытку позже')

        return self.json_error('postponed_task.unknown_error', u'Неизвестная ошибка, повторите попытку позже')
