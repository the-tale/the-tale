# coding: utf-8

from django.core import mail
from django.conf import settings as project_settings

from dext.jinja2 import render

# TODO: rewrite to autodiscover() logic
#       code for this can be chosen form postponed_tasks and moved to utils


class BaseMessageHandler(object):
    TYPE = None

    def serialize(self): raise NotImplemented

    @classmethod
    def deserialize(cls, data): raise NotImplemented

    def process(self): raise NotImplemented


class TestHandler(BaseMessageHandler):

    TYPE = 'test'

    def __init__(self):
        super(BaseMessageHandler, self).__init__()

    def serialize(self):
        return {'type': self.TYPE}

    @classmethod
    def deserialize(cls):
        obj = cls()
        return obj

    def process(self):
        return True


class ForumPostHandler(BaseMessageHandler):

    TYPE = 'forum_post'

    def __init__(self, post_id=None):
        super(BaseMessageHandler, self).__init__()
        self.post_id = post_id

    def serialize(self):
        return {'type': self.TYPE,
                'post_id': self.post_id}

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.post_id = data['post_id']
        return obj

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



HANDLERS = dict( (handler.TYPE, handler)
                 for handler in globals().values()
                 if isinstance(handler, type) and issubclass(handler, BaseMessageHandler) and handler != BaseMessageHandler)

def deserialize_handler(data):
    return HANDLERS[data['type']].deserialize(data)
