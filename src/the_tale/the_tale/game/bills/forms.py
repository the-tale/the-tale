
from django.forms import Textarea

from dext.forms import forms, fields

from . import conf
from . import models
from . import relations


class BaseUserForm(forms.Form):
    caption = fields.CharField(label='Название записи',
                               max_length=models.Bill.CAPTION_MAX_LENGTH,
                               min_length=models.Bill.CAPTION_MIN_LENGTH)

    chronicle_on_accepted = fields.TextField(label='Текст летописи при принятии (от {} до {} символов)'.format(conf.bills_settings.CHRONICLE_MIN_LENGTH,
                                                                                                               conf.bills_settings.CHRONICLE_MAX_LENGTH),
                                             widget=Textarea(attrs={'rows': 6}),
                                             min_length=conf.bills_settings.CHRONICLE_MIN_LENGTH,
                                             max_length=conf.bills_settings.CHRONICLE_MAX_LENGTH)

    depends_on = fields.ChoiceField(label='Зависит от', required=False)

    def __init__(self, *args, **kwargs):
        original_bill_id = kwargs.pop('original_bill_id', None)

        super().__init__(*args, **kwargs)

        voting_bills = models.Bill.objects.filter(state=relations.BILL_STATE.VOTING)
        self.fields['depends_on'].choices = [(None, ' — ')] + [(bill.id, bill.caption)
                                                               for bill in voting_bills
                                                               if bill.id != original_bill_id]

    def clean_depends_on(self):
        data = self.cleaned_data.get('depends_on')

        if data == 'None':
            return None

        return data


class ModeratorFormMixin(forms.Form):
    approved = fields.BooleanField(label='Одобрено', required=False)
