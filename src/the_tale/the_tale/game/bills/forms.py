
from django.conf import settings as project_settings
from django.forms import Textarea

from dext.forms import forms, fields

from the_tale.common.utils import bbcode

from the_tale.game.bills.models import Bill
from the_tale.game.bills.conf import bills_settings


class BaseUserForm(forms.Form):
    caption = fields.CharField(label='Название записи', max_length=Bill.CAPTION_MAX_LENGTH, min_length=Bill.CAPTION_MIN_LENGTH)

    chronicle_on_accepted = fields.TextField(label='Текст летописи при принятии', widget=Textarea(attrs={'rows': 2}),
                                             min_length=bills_settings.CHRONICLE_MIN_LENGTH, max_length=bills_settings.CHRONICLE_MAX_LENGTH)



class ModeratorFormMixin(forms.Form):
    approved = fields.BooleanField(label='Одобрено', required=False)
