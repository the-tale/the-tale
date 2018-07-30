
import smart_imports

smart_imports.all()


def send_mail(accounts, subject, text_content, html_content):
    connection = django_mail.get_connection()
    connection.open()

    system_user = accounts_logic.get_system_user()

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

        email = django_mail.EmailMultiAlternatives(subject, text_content, django_settings.EMAIL_NOREPLY, [account_email], connection=connection)
        email.attach_alternative(html_content, "text/html")

        try:
            email.send()
        except Exception:
            if not django_settings.TESTS_RUNNING:
                logger = logging.getLogger('the-tale.workers.post_service_message_sender')
                logger.error('Exception while send email',
                             exc_info=sys.exc_info(),
                             extra={})

            fails += 1

    connection.close()

    return fails == 0
