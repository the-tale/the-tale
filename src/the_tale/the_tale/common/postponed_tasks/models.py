
import smart_imports

smart_imports.all()


POSTPONED_TASK_STATE = utils_enum.create_enum('POSTPONED_TASK_STATE', (('WAITING', 0, 'ожидает обработки'),
                                                                       ('PROCESSED', 1, 'обработана'),
                                                                       ('RESETED', 2, 'сброшена'),
                                                                       ('ERROR', 3, 'ошибка при обработке'),
                                                                       ('EXCEPTION', 4, 'исключение при обработке'),
                                                                       ('TIMEOUT', 5, 'превышено время выполнения')))

POSTPONED_TASK_LOGIC_RESULT = utils_enum.create_enum('POSTPONED_TASK_LOGIC_RESULT', (('SUCCESS', 0, 'удачное выполнение'),
                                                                                     ('ERROR', 1, 'ошибка'),
                                                                                     ('CONTINUE', 2, 'необходимо продолжить выполнение'),
                                                                                     ('WAIT', 3, 'ожидает других задач')))


class PostponedTask(django_models.Model):

    created_at = django_models.DateTimeField(auto_now_add=True)

    updated_at = django_models.DateTimeField(auto_now=True)

    live_time = django_models.BigIntegerField(null=True, default=None)

    state = django_models.IntegerField(default=POSTPONED_TASK_STATE.WAITING, db_index=True, choices=POSTPONED_TASK_STATE._CHOICES)

    comment = django_models.TextField(blank=True, default='')

    internal_result = django_models.IntegerField(null=True, db_index=True, choices=POSTPONED_TASK_LOGIC_RESULT._CHOICES)

    internal_type = django_models.CharField(max_length=64, db_index=True)

    internal_state = django_models.IntegerField(db_index=True)

    internal_data = django_models.TextField(default='{}')
