# coding: utf-8

import sys

from django.core import mail
from django.conf import settings as project_settings

from the_tale.accounts.logic import get_system_user


def send_mail(accounts, subject, text_content, html_content):
    connection = mail.get_connection()
    connection.open()

    system_user = get_system_user()

    fails = 0

    for account in accounts:

        if isinstance(account, (tuple, list)):
            account_email = account[1]
            account = account[0]
        else:
            account_email = account.email

        if not account_email:
            continue

        if account.id == system_user.id or account.is_bot:
            continue

        email = mail.EmailMultiAlternatives(subject, text_content, project_settings.EMAIL_NOREPLY, [account_email], connection=connection)
        email.attach_alternative(html_content, "text/html")

        try:
            email.send()
        except Exception:
            from django.utils.log import getLogger
            if not project_settings.TESTS_RUNNING:
                logger = getLogger('the-tale.workers.post_service_message_sender')
                logger.error('Exception while send email',
                             exc_info=sys.exc_info(),
                             extra={} )

            fails += 1

    connection.close()

    return fails == 0
