# coding: utf-8
import copy

from django.core.mail import EmailMultiAlternatives

from dext.jinja2 import render


class EMail(object):

    HTML_TEMPLATE = None
    TEXT_TEMPLATE = None

    SENDER = None

    SUBJECT = None


    def __init__(self, context={}):
        full_context = copy.copy(context)
        full_context['subject'] = self.SUBJECT
        full_context['sender'] = self.SENDER

        self.text_content = render.template(self.TEXT_TEMPLATE, full_context)
        self.html_content = render.template(self.HTML_TEMPLATE, full_context)


    def send(self, recipients):
        email = EmailMultiAlternatives(self.SUBJECT, self.text_content, self.SENDER, recipients)
        email.attach_alternative(self.html_content, "text/html")
        email.send()
