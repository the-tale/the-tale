# coding: utf-8

from rels import Column
from rels.django import DjangoEnum


class XSOLLA_RESULT(DjangoEnum):

    records = ( ('OK', 0, 'OK'),
                ('REPEATE_REQUEST', 1, 'Временная ошибка, повторите запрос позже'),
                ('WRONG_USER_ID', 2, 'Неверный идентификатор пользователя'),
                ('WRONG_MD5', 3, 'Неверная подпись md5'),
                ('WRONG_REQUEST_FORMAT', 4, 'Неверный формат запроса (неверная сумма, неполный набор параметров)'),
                ('OTHER_ERROR', 5, 'Другая ошибка (желательно описать ее в comment)'),
                ('PAYMENT_RESTRICTED', 7, 'Прием платежа от данного пользователя запрещен по техническим причинам') )


class COMMAND_TYPE(DjangoEnum):
    records = ( ('CHECK', 'check', 'проверка существования пользователя'),
                ('PAY', 'pay', 'зачисление средств'),
                ('CANCEL', 'cancel', 'отмена платежа') )


class COMMON_RESULT(DjangoEnum):
    xsolla_result = Column(unique=False, primary=False)
    records = ( ('DISALLOWED_IP', 0, 'попытка достпуа с ip не внесённого в список разрешённых', XSOLLA_RESULT.OTHER_ERROR),
                ('WRONG_COMMAND', 1, 'неверный идентификатор команды', XSOLLA_RESULT.OTHER_ERROR),
                ('UNKNOWN_ERROR', 2, 'ошибка при обработке запроса', XSOLLA_RESULT.OTHER_ERROR))

class CANCEL_RESULT(DjangoEnum):
    xsolla_result = Column(unique=False, primary=False)
    records = ( ('NOT_SUPPORTED', 0, 'отмена платежей не поддерживается', XSOLLA_RESULT.OTHER_ERROR), )


class INVOICE_STATE(DjangoEnum):
    records = ( ('ERROR_WHILE_CREATING', 0, 'ошибка при создании платежа'),
                ('CREATED', 1, 'создан'),
                ('ERROR_WHILE_PROCESSING', 2, 'ошибка при начислении средств'),
                ('PROCESSED', 3, 'платёж обработан'),
                ('SKIPPED_BECOUSE_TEST', 4, 'обработка пропущена, т.к. платёж проверочный') )


class CHECK_USER_RESULT(DjangoEnum):
    xsolla_result = Column(unique=False, primary=False)
    records = ( ('USER_EXISTS', 0, 'пользователь найден', XSOLLA_RESULT.OK),
                ('USER_NOT_EXISTS', 1, 'пользователь не найден', XSOLLA_RESULT.PAYMENT_RESTRICTED),
                ('WRONG_MD5', 2, 'неверная контрольная сумма', XSOLLA_RESULT.WRONG_MD5),
                ('NOT_SPECIFIED_V1', 3, 'не указан параметр v1', XSOLLA_RESULT.WRONG_REQUEST_FORMAT) )


class PAY_RESULT(DjangoEnum):
    xsolla_result = Column(unique=False, primary=False)
    invoice_state = Column(unique=False, primary=False)
    records = ( ('USER_NOT_EXISTS', 0, 'пользователь не найден', XSOLLA_RESULT.WRONG_USER_ID, INVOICE_STATE.ERROR_WHILE_CREATING),
                ('WRONG_MD5', 1, 'неверная контрольная сумма', XSOLLA_RESULT.WRONG_MD5, INVOICE_STATE.ERROR_WHILE_CREATING),
                ('WRONG_SUM_FORMAT', 2, 'неверный формат суммы', XSOLLA_RESULT.WRONG_REQUEST_FORMAT, INVOICE_STATE.ERROR_WHILE_CREATING),
                ('FRACTION_IN_SUM', 3, 'дробная часть в сумме начислений', XSOLLA_RESULT.WRONG_REQUEST_FORMAT, INVOICE_STATE.ERROR_WHILE_CREATING),
                ('SUCCESS', 4, 'платёж зарегистрирован', XSOLLA_RESULT.OK, INVOICE_STATE.CREATED),
                ('NOT_POSITIVE_SUM', 5, 'сумма платежа меньше 0 либо равна ему', XSOLLA_RESULT.WRONG_REQUEST_FORMAT, INVOICE_STATE.ERROR_WHILE_CREATING ),
                ('NOT_SPECIFIED_V1', 6, 'не указан параметр v1', XSOLLA_RESULT.WRONG_REQUEST_FORMAT, INVOICE_STATE.ERROR_WHILE_CREATING),
                ('NOT_SPECIFIED_ID', 7, 'не указан параметр id', XSOLLA_RESULT.WRONG_REQUEST_FORMAT, INVOICE_STATE.ERROR_WHILE_CREATING),
                ('NOT_SPECIFIED_SUM', 8, 'не указан параметр sum', XSOLLA_RESULT.WRONG_REQUEST_FORMAT, INVOICE_STATE.ERROR_WHILE_CREATING),
                ('WRONG_DATE_FORMAT', 9, 'неверный формат даты', XSOLLA_RESULT.WRONG_REQUEST_FORMAT, INVOICE_STATE.ERROR_WHILE_CREATING))
