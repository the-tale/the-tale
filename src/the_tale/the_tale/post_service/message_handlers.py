
import smart_imports

smart_imports.all()


class BaseMessageHandler(object):
    TYPE = NotImplemented

    @property
    def settings_type_uid(self): return '<%s>' % self.TYPE

    def serialize(self): raise NotImplementedError

    @classmethod
    def deserialize(cls, data): raise NotImplementedError

    def process(self): raise NotImplementedError

    @property
    def uid(self): raise NotImplementedError


class TestHandler(BaseMessageHandler):

    TYPE = 'test'

    def __init__(self):
        super(TestHandler, self).__init__()

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
    EMAIL_HTML_TEMPLATE = 'post_service/emails/personal_message.html'
    EMAIL_TEXT_TEMPLATE = 'post_service/emails/personal_message.txt'

    def __init__(self, message_id=None, account_id=None):
        super(PersonalMessageHandler, self).__init__()
        self.message_id = message_id
        self.account_id = account_id

    def serialize(self):
        return {'type': self.TYPE,
                'message_id': self.message_id,
                'account_id': self.account_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.message_id = data['message_id']
        obj.account_id = data['account_id']
        return obj

    @property
    def uid(self): return 'personal-message-{}-{}'.format(self.account_id, self.message_id)

    def process(self):
        message = personal_messages_tt_services.personal_messages.cmd_get_message(self.account_id, message_id=self.message_id)

        if message is None:
            return True  # message can be removed by admins or with removed thread

        account = accounts_prototypes.AccountPrototype.get_by_id(self.account_id)

        if not account.personal_messages_subscription:
            return True

        if account.id == accounts_logic.get_system_user().id or account.is_bot:
            return True

        if not account.email:
            return True

        subject = '«Сказка»: личное сообщение'

        context = {'message': message,
                   'sender': accounts_prototypes.AccountPrototype.get_by_id(message.sender_id)}

        html_content = utils_jinja2.render(self.EMAIL_HTML_TEMPLATE, context)
        text_content = utils_jinja2.render(self.EMAIL_TEXT_TEMPLATE, context)

        return logic.send_mail([account], subject, text_content, html_content)


class ForumPostHandler(BaseMessageHandler):

    TYPE = 'forum_post'
    EMAIL_HTML_TEMPLATE = 'post_service/emails/new_forum_post.html'
    EMAIL_TEXT_TEMPLATE = 'post_service/emails/new_forum_post.txt'

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
        post = forum_prototypes.PostPrototype.get_by_id(self.post_id)

        if post is None:
            return True  # post can be removed by admins or with removed thread

        accounts = forum_prototypes.SubscriptionPrototype.get_accounts_for_thread(post.thread)

        subject = '«Сказка»: %s' % post.thread.caption

        context = {'post': post}

        html_content = utils_jinja2.render(self.EMAIL_HTML_TEMPLATE, context)
        text_content = utils_jinja2.render(self.EMAIL_TEXT_TEMPLATE, context)

        return logic.send_mail(accounts, subject, text_content, html_content)


class ForumThreadHandler(BaseMessageHandler):

    TYPE = 'forum_thread'
    EMAIL_HTML_TEMPLATE = 'post_service/emails/new_forum_thread.html'
    EMAIL_TEXT_TEMPLATE = 'post_service/emails/new_forum_thread.txt'

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
        thread = forum_prototypes.ThreadPrototype.get_by_id(self.thread_id)

        if thread is None:
            return True  # thread can be removed by admins or with removed thread

        post = thread.get_first_post()

        accounts = forum_prototypes.SubscriptionPrototype.get_accounts_for_subcategory(thread.subcategory)

        subject = '«Сказка»: новая тема на форуме'

        context = {'thread': thread,
                   'post': post}

        html_content = utils_jinja2.render(self.EMAIL_HTML_TEMPLATE, context)
        text_content = utils_jinja2.render(self.EMAIL_TEXT_TEMPLATE, context)

        return logic.send_mail(accounts, subject, text_content, html_content)


class ResetPasswordHandler(BaseMessageHandler):

    TYPE = 'reset_password'
    EMAIL_HTML_TEMPLATE = 'post_service/emails/reset_password.html'
    EMAIL_TEXT_TEMPLATE = 'post_service/emails/reset_password.txt'

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
        account = accounts_prototypes.AccountPrototype.get_by_id(self.account_id)

        if account.id == accounts_logic.get_system_user().id or account.is_bot:
            return True

        subject = '«Сказка»: сброс пароля'

        context = {'account': account,
                   'task_uuid': self.task_uuid}

        html_content = utils_jinja2.render(self.EMAIL_HTML_TEMPLATE, context)
        text_content = utils_jinja2.render(self.EMAIL_TEXT_TEMPLATE, context)

        return logic.send_mail([account], subject, text_content, html_content)


class ChangeEmailNotificationHandler(BaseMessageHandler):

    TYPE = 'change-email-notification'
    EMAIL_HTML_TEMPLATE = 'post_service/emails/change_email_notification.html'
    EMAIL_TEXT_TEMPLATE = 'post_service/emails/change_email_notification.txt'

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

        subject = '«Сказка»: подтвердите email'

        task = accounts_prototypes.ChangeCredentialsTaskPrototype.get_by_id(self.task_id)

        if task.account.id == accounts_logic.get_system_user().id or task.account.is_bot:
            return True

        context = {'task': task}

        html_content = utils_jinja2.render(self.EMAIL_HTML_TEMPLATE, context)
        text_content = utils_jinja2.render(self.EMAIL_TEXT_TEMPLATE, context)

        return logic.send_mail([(task.account, task.new_email)], subject, text_content, html_content)


class NewsHandler(BaseMessageHandler):
    TYPE = 'news_post'
    EMAIL_HTML_TEMPLATE = 'post_service/emails/new_news.html'
    EMAIL_TEXT_TEMPLATE = 'post_service/emails/new_news.txt'

    def __init__(self, news_id=None):
        super(NewsHandler, self).__init__()
        self.news_id = news_id

    def serialize(self):
        return {'type': self.TYPE,
                'news_id': self.news_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.news_id = data['news_id']
        return obj

    @property
    def uid(self): return 'news-%d-message' % self.news_id

    def process(self):
        news = news_logic.load_news(self.news_id)

        if news is None:
            return True

        accounts = (accounts_prototypes.AccountPrototype(model=account_model) for account_model in accounts_prototypes.AccountPrototype._db_filter(news_subscription=True).iterator())

        subject = '«Сказка»::Новости: %s' % news.caption

        context = {'news': news}

        html_content = utils_jinja2.render(self.EMAIL_HTML_TEMPLATE, context)
        text_content = utils_jinja2.render(self.EMAIL_TEXT_TEMPLATE, context)

        return logic.send_mail(accounts, subject, text_content, html_content)


HANDLERS = dict((handler.TYPE, handler)
                for handler in globals().values()
                if isinstance(handler, type) and issubclass(handler, BaseMessageHandler) and handler != BaseMessageHandler)


def deserialize_handler(data):
    return HANDLERS[data['type']].deserialize(data)
