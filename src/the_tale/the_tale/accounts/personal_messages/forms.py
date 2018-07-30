
import smart_imports

smart_imports.all()


class RecipientsForm(dext_forms.Form):

    recipients = dext_fields.TextField(label='', widget=django_forms.HiddenInput())

    def clean_recipients(self):
        recipients = self.cleaned_data['recipients']

        try:
            recipients = [int(id_.strip()) for id_ in recipients.split(',')]
        except ValueError:
            raise django_forms.ValidationError('Неверный идентификатор получателя')

        return recipients


class NewMessageForm(RecipientsForm):

    text = utils_bbcode.BBField(label='Сообщение')
