# coding: utf-8

from dext.forms import forms, fields

from the_tale.common.utils import bbcode

from the_tale.collections.storage import items_storage

from the_tale.accounts.achievements.prototypes import AchievementPrototype
from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP, ACHIEVEMENT_TYPE


def create_clean_item_method(number):

    def clean_item(self):
        item = self.cleaned_data.get('item_%d' % number)

        if item != '':
            return items_storage[int(item)]

        return None

    return clean_item


class NewAchievementForm(forms.Form):

    approved = fields.BooleanField(label=u'Одобрена', required=False)

    order = fields.IntegerField()

    group = fields.TypedChoiceField(label=u'Группа', choices=sorted(ACHIEVEMENT_GROUP.choices(), key=lambda g: g[1]), coerce=ACHIEVEMENT_GROUP.get_from_name)
    type = fields.TypedChoiceField(label=u'Тип', choices=sorted(ACHIEVEMENT_TYPE.choices(), key=lambda g: g[1]), coerce=ACHIEVEMENT_TYPE.get_from_name)

    caption = fields.CharField(label=u'Название', max_length=AchievementPrototype.CAPTION_MAX_LENGTH, min_length=1)

    description = bbcode.BBField(label=u'Описание', min_length=1, max_length=AchievementPrototype.DESCRIPTION_MAX_LENGTH)

    barrier = fields.IntegerField(label=u'Барьер')

    points = fields.IntegerField(label=u'Очки')

    item_1 = fields.ChoiceField(label=u'награда 1', choices=[], required=False)
    item_2 = fields.ChoiceField(label=u'награда 2', choices=[], required=False)
    item_3 = fields.ChoiceField(label=u'награда 3', choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super(NewAchievementForm, self).__init__(*args, **kwargs)
        self.fields['item_1'].choices = [('', u'-----')] + items_storage.form_choices()
        self.fields['item_2'].choices = [('', u'-----')] + items_storage.form_choices()
        self.fields['item_3'].choices = [('', u'-----')] + items_storage.form_choices()

    clean_item_1 = create_clean_item_method(1)
    clean_item_2 = create_clean_item_method(2)
    clean_item_3 = create_clean_item_method(3)



class EditAchievementForm(NewAchievementForm):

    approved = fields.BooleanField(label=u'Одобрена', required=False)
