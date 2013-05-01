# coding: utf-8

import sys
import datetime

from django.core.urlresolvers import reverse

from dext.utils import s11n

from common.postponed_tasks.models import PostponedTask, POSTPONED_TASK_STATE, POSTPONED_TASK_LOGIC_RESULT
from common.postponed_tasks.exceptions import PostponedTaskException
from common.postponed_tasks.conf import postponed_tasks_settings


_INTERNAL_LOGICS = {}


def postponed_task(internal_logic_class):
    internal_logic_class._is_postponed_task = True
    return internal_logic_class


def _register_postponed_tasks(objects):
    global _INTERNAL_LOGICS

    for obj in objects:
        if getattr(obj, '_is_postponed_task', False):
            if obj.TYPE in _INTERNAL_LOGICS:
                raise PostponedTaskException(u'interanl logic "%s" for postponed task has being registered already' % obj.TYPE)
            _INTERNAL_LOGICS[obj.TYPE] = obj


def autodiscover():

    global _INTERNAL_LOGICS

    _INTERNAL_LOGICS = {}

    from django.conf import settings as project_settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in project_settings.INSTALLED_APPS:
        mod = import_module(app)

        try:
            module = import_module('%s.postponed_tasks' % app)

            _register_postponed_tasks([getattr(module, name) for name in dir(module)])
        except:
            if module_has_submodule(mod, 'postponed_tasks'):
                raise


class PostponedTaskPrototype(object):

    def __init__(self, model=None):
        self.model = model
        self._postsave_actions = []

    @property
    def id(self): return self.model.id

    @property
    def type(self): return self.model.internal_type

    @property
    def created_at(self): return self.model.created_at

    @property
    def updated_at(self): return self.model.updated_at

    @property
    def live_time(self): return self.model.live_time

    @property
    def status_url(self): return reverse('postponed-tasks:status', args=[self.id])

    def get_state(self):
        if not hasattr(self, '_state'):
            self._state = POSTPONED_TASK_STATE(self.model.state)
        return self._state
    def set_state(self, value):
        self.state.update(value)
        self.model.state = self.state.value
    state = property(get_state, set_state)

    def get_internal_state(self): return self.model.internal_state
    def set_internal_state(self, value): self.model.internal_state = value
    internal_state = property(get_internal_state, set_internal_state)

    def get_internal_result(self): return self.model.internal_result
    def set_internal_result(self, value): self.model.internal_result = value
    internal_result = property(get_internal_result, set_internal_result)

    def get_comment(self): return self.model.comment
    def set_comment(self, value): self.model.comment = value
    comment = property(get_comment, set_comment)

    @property
    def internal_logic(self):
        if not hasattr(self, '_internal_logic'):
            self._internal_logic = _INTERNAL_LOGICS[self.type].deserialize(s11n.from_json(self.model.internal_data))
        return self._internal_logic

    def save(self):
        self.model.internal_data = s11n.to_json(self.internal_logic.serialize())
        self.model.save()

    def remove(self):
        self.model.delete()

    @classmethod
    def reset_all(cls):
        PostponedTask.objects.filter(state=POSTPONED_TASK_STATE.WAITING).update(state=POSTPONED_TASK_STATE.RESETED)

    @classmethod
    def get_by_id(cls, task_id):
        try:
            return cls(PostponedTask.objects.get(id=task_id))
        except PostponedTask.DoesNotExist:
            return None

    @classmethod
    def check_if_used(cls, internal_type, internal_uuid):
        return PostponedTask.objects.filter(internal_type=internal_type,
                                            internal_uuid=internal_uuid,
                                            state=POSTPONED_TASK_STATE.WAITING).exists()

    @classmethod
    def get_processed_tasks_query(cls):
        return PostponedTask.objects.exclude(state=POSTPONED_TASK_STATE.WAITING)

    @classmethod
    def remove_old_tasks(cls):
        cls.get_processed_tasks_query().filter(updated_at__lt=datetime.datetime.now() - datetime.timedelta(seconds=postponed_tasks_settings.TASK_LIVE_TIME)).delete()

    @classmethod
    def create(cls, task_logic, live_time=None):
        model = PostponedTask.objects.create(internal_type=task_logic.TYPE,
                                             internal_uuid=task_logic.uuid,
                                             internal_state=task_logic.state,
                                             internal_data=s11n.to_json(task_logic.serialize()),
                                             live_time=live_time)
        return cls(model=model)

    def add_postsave_action(self, action):
        self._postsave_actions.append(action)

    def extend_postsave_actions(self, actions):
        self._postsave_actions.extend(actions)

    def do_postsave_actions(self):
        if self.state.is_waiting or self.state.is_processed:
            for action in self._postsave_actions:
                action()


    def process(self, logger, **kwargs):

        if not self.state.is_waiting:
            return

        if self.live_time is not None and datetime.datetime.now() > self.created_at + datetime.timedelta(seconds=self.live_time):
            self.state = POSTPONED_TASK_STATE.TIMEOUT
            self.save()
            return

        try:
            self.internal_result = self.internal_logic.process(self, **kwargs)

            if self.internal_result == POSTPONED_TASK_LOGIC_RESULT.SUCCESS:
                self.state = POSTPONED_TASK_STATE.PROCESSED
            elif self.internal_result == POSTPONED_TASK_LOGIC_RESULT.ERROR:
                self.state = POSTPONED_TASK_STATE.ERROR
            elif self.internal_result == POSTPONED_TASK_LOGIC_RESULT.CONTINUE:
                pass
            elif self.internal_result == POSTPONED_TASK_LOGIC_RESULT.WAIT:
                pass
            else:
                raise PostponedTaskException(u'unknown process result %r' % (self.process_result, ))

            self.internal_state = self.internal_logic.state
            self.save()

        except Exception, e:
            logger.error('EXCEPTION: %s' % e)

            exception_info = sys.exc_info()

            logger.error('Worker exception: %r' % self,
                         exc_info=exception_info,
                         extra={} )

            self.state = POSTPONED_TASK_STATE.EXCEPTION
            self.comment = u'%s\n\n%s\n\n %s' % exception_info
            self.save()
