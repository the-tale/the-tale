# coding: utf-8

from django.forms import ValidationError, HiddenInput

from dext.forms import forms, fields

from the_tale.common.utils import bbcode


class RecipientsForm(forms.Form):

    recipients = fields.TextField(label='', widget=HiddenInput())

    def clean_recipients(self):
        recipients = self.cleaned_data['recipients']

        try:
            recipients = [int(id_.strip()) for id_ in recipients.split(',')]
        except ValueError:
            raise ValidationError(u'Неверный идентификатор получателя')

        return recipients



class NewMessageForm(RecipientsForm):

    text = bbcode.BBField(label=u'Сообщение')
