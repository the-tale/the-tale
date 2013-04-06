# coding: utf-8

from django.core import mail
from django.conf import settings as project_settings

from dext.jinja2 import render

from accounts.prototypes import AccountPrototype, ChangeCredentialsTaskPrototype

# TODO: rewrite to autodiscover() logic
#       code for this can be chosen form postponed_tasks and moved to utils


class BaseMessageHandler(object):
    TYPE = None

    @property
    def settings_type_uid(self): return '<%s>' % self.TYPE

    def serialize(self): raise NotImplemented

    @classmethod
    def deserialize(cls, data): raise NotImplemented

    def process(self): raise NotImplemented

    @property
    def uid(self): raise NotImplemented


class TestHandler(BaseMessageHandler):

    TYPE = 'test'

    def __init__(self):
        super(BaseMessageHandler, self).__init__()

    def serialize(self):
        return {'type': self.TYPE}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        return obj

    def process(self):
        return True

    @property
    def uid(self): return 'test-message'


class PersonalMessageHandler(BaseMessageHandler):

    TYPE = 'personal_message'

    def __init__(self, message_id=None):
        super(PersonalMessageHandler, self).__init__()
        self.message_id = message_id

    def serialize(self):
        return {'type': self.TYPE,
                'message_id': self.message_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.message_id = data['message_id']
        return obj

    @property
    def uid(self): return 'personal-message-%d-message' % self.message_id

    def process(self):
        from accounts.personal_messages.prototypes import MessagePrototype as PersonalMessagePrototype

        message = PersonalMessagePrototype.get_by_id(self.message_id)

        if message is None:
            return True # message can be removed by admins or with removed thread

        account = message.recipient

        if not account.personal_messages_subscription:
            return True

        EMAIL_HTML_TEMPLATE = 'post_service/emails/personal_message.html'
        EMAIL_TEXT_TEMPLATE = 'post_service/emails/personal_message.txt'

        subject = u'«Сказка»: личное сообщение'

        context = {'message': message}

        html_content = render.template(EMAIL_HTML_TEMPLATE, context)
        text_content = render.template(EMAIL_TEXT_TEMPLATE, context)

        connection = mail.get_connection()
        connection.open()

        if not account.email:
            return True

        email = mail.EmailMultiAlternatives(subject, text_content, project_settings.EMAIL_NOREPLY, [account.email], connection=connection)
        email.attach_alternative(html_content, "text/html")
        email.send()

        connection.close()

        return True


class ForumPostHandler(BaseMessageHandler):

    TYPE = 'forum_post'

    def __init__(self, post_id=None):
        super(ForumPostHandler, self).__init__()
        self.post_id = post_id

    def serialize(self):
        return {'type': self.TYPE,
                'post_id': self.post_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.post_id = data['post_id']
        return obj

    @property
    def uid(self): return 'forum-post-%d-message' % self.post_id

    def process(self):
        from forum.prototypes import PostPrototype, SubscriptionPrototype

        post = PostPrototype.get_by_id(self.post_id)

        if post is None:
            return True # post can be removed by admins or with removed thread

        accounts = SubscriptionPrototype.get_accounts_for_thread(post.thread)

        EMAIL_HTML_TEMPLATE = 'post_service/emails/new_forum_post.html'
        EMAIL_TEXT_TEMPLATE = 'post_service/emails/new_forum_post.txt'

        subject = u'«Сказка»: %s' % post.thread.caption

        context = {'post': post}

        html_content = render.template(EMAIL_HTML_TEMPLATE, context)
        text_content = render.template(EMAIL_TEXT_TEMPLATE, context)

        connection = mail.get_connection()
        connection.open()

        for account in accounts:
            if not account.email:
                continue

            email = mail.EmailMultiAlternatives(subject, text_content, project_settings.EMAIL_NOREPLY, [account.email], connection=connection)
            email.attach_alternative(html_content, "text/html")
            email.send()

        connection.close()

        return True


class ForumThreadHandler(BaseMessageHandler):

    TYPE = 'forum_thread'

    def __init__(self, thread_id=None):
        super(ForumThreadHandler, self).__init__()
        self.thread_id = thread_id

    def serialize(self):
        return {'type': self.TYPE,
                'thread_id': self.thread_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.thread_id = data['thread_id']
        return obj

    @property
    def uid(self): return 'forum-thread-%d-message' % self.thread_id

    def process(self):
        from forum.prototypes import ThreadPrototype, SubscriptionPrototype

        thread = ThreadPrototype.get_by_id(self.thread_id)

        if thread is None:
            return True # thread can be removed by admins or with removed thread

        post = thread.get_first_post()

        accounts = SubscriptionPrototype.get_accounts_for_subcategory(thread.subcategory)

        EMAIL_HTML_TEMPLATE = 'post_service/emails/new_forum_thread.html'
        EMAIL_TEXT_TEMPLATE = 'post_service/emails/new_forum_thread.txt'

        subject = u'«Сказка»: новая тема на форуме'

        context = {'thread': thread,
                   'post': post}

        html_content = render.template(EMAIL_HTML_TEMPLATE, context)
        text_content = render.template(EMAIL_TEXT_TEMPLATE, context)

        connection = mail.get_connection()
        connection.open()

        for account in accounts:
            if not account.email:
                continue

            email = mail.EmailMultiAlternatives(subject, text_content, project_settings.EMAIL_NOREPLY, [account.email], connection=connection)
            email.attach_alternative(html_content, "text/html")
            email.send()

        connection.close()

        return True


class ResetPasswordHandler(BaseMessageHandler):

    TYPE = 'reset_password'

    def __init__(self, account_id=None, task_uuid=None):
        super(ResetPasswordHandler, self).__init__()
        self.account_id = account_id
        self.task_uuid = task_uuid

    def serialize(self):
        return {'type': self.TYPE,
                'account_id': self.account_id,
                'task_uuid': self.task_uuid}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.account_id = data['account_id']
        obj.task_uuid = data['task_uuid']
        return obj

    @property
    def uid(self): return 'reset-password-%d-%s-message' % (self.account_id, self.task_uuid)

    def process(self):
        account = AccountPrototype.get_by_id(self.account_id)

        EMAIL_HTML_TEMPLATE = 'post_service/emails/reset_password.html'
        EMAIL_TEXT_TEMPLATE = 'post_service/emails/reset_password.txt'

        subject = u'«Сказка»: сброс пароля'

        context = {'account': account,
                   'task_uuid': self.task_uuid}

        html_content = render.template(EMAIL_HTML_TEMPLATE, context)
        text_content = render.template(EMAIL_TEXT_TEMPLATE, context)

        connection = mail.get_connection()
        connection.open()

        email = mail.EmailMultiAlternatives(subject, text_content, project_settings.EMAIL_NOREPLY, [account.email], connection=connection)
        email.attach_alternative(html_content, "text/html")
        email.send()

        connection.close()

        return True

class ChangeEmailNotificationHandler(BaseMessageHandler):

    TYPE = 'change-email-notification'

    def __init__(self, task_id=None):
        super(ChangeEmailNotificationHandler, self).__init__()
        self.task_id = task_id

    def serialize(self):
        return {'type': self.TYPE,
                'task_id': self.task_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.task_id = data['task_id']
        return obj

    @property
    def uid(self): return 'change-email-notificatoon-%d-message' % self.task_id

    def process(self):

        EMAIL_HTML_TEMPLATE = 'post_service/emails/change_email_notification.html'
        EMAIL_TEXT_TEMPLATE = 'post_service/emails/change_email_notification.txt'

        subject = u'«Сказка»: подтвердите email'

        task = ChangeCredentialsTaskPrototype.get_by_id(self.task_id)

        context = {'task': task}

        html_content = render.template(EMAIL_HTML_TEMPLATE, context)
        text_content = render.template(EMAIL_TEXT_TEMPLATE, context)

        connection = mail.get_connection()
        connection.open()

        email = mail.EmailMultiAlternatives(subject, text_content, project_settings.EMAIL_NOREPLY, [task.account.email], connection=connection)
        email.attach_alternative(html_content, "text/html")
        email.send()

        connection.close()

        return True




HANDLERS = dict( (handler.TYPE, handler)
                 for handler in globals().values()
                 if isinstance(handler, type) and issubclass(handler, BaseMessageHandler) and handler != BaseMessageHandler)

def deserialize_handler(data):
    return HANDLERS[data['type']].deserialize(data)
