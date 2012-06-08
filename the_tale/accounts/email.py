# coding: utf-8

from django.conf import settings as project_settings

from common.utils.email import EMail


class ChangeEmailNotification(EMail):

    HTML_TEMPLATE = 'accounts/email_change_email_notification.html'
    TEXT_TEMPLATE = 'accounts/email_change_email_notification.txt'

    SENDER = project_settings.EMAIL_NOREPLY

    SUBJECT = u'Сказка: подтвердите email'
