# coding: utf-8

from django.db import models

from the_tale.common.utils.enum import create_enum

POSTPONED_TASK_STATE = create_enum('POSTPONED_TASK_STATE', (('WAITING', 0, u'ожидает обработки'),
                                                            ('PROCESSED', 1, u'обработана'),
                                                            ('RESETED', 2, u'сброшена'),
                                                            ('ERROR', 3, u'ошибка при обработке'),
                                                            ('EXCEPTION', 4, u'исключение при обработке'),
                                                            ('TIMEOUT', 5, u'превышено время выполнения')) )

POSTPONED_TASK_LOGIC_RESULT = create_enum('POSTPONED_TASK_LOGIC_RESULT', (('SUCCESS', 0, u'удачное выполнение'),
                                                                          ('ERROR', 1, u'ошибка'),
                                                                          ('CONTINUE', 2, u'необходимо продолжить выполнение'),
                                                                          ('WAIT', 3, u'ожидает других задач') ) )


class PostponedTask(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    live_time = models.BigIntegerField(null=True, default=None)

    state = models.IntegerField(default=POSTPONED_TASK_STATE.WAITING, db_index=True, choices=POSTPONED_TASK_STATE._CHOICES)

    comment = models.TextField(blank=True, default='')

    internal_result = models.IntegerField(null=True, db_index=True, choices=POSTPONED_TASK_LOGIC_RESULT._CHOICES)

    internal_type = models.CharField(max_length=64, db_index=True)

    internal_state = models.IntegerField(db_index=True)

    internal_data = models.TextField(default=u'{}')
