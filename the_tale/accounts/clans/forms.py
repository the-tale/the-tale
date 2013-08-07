# coding: utf-8
from django.forms import ValidationError

from dext.forms import forms, fields

from common.utils import bbcode

from accounts.clans.models import Clan, MembershipRequest

class ClanForm(forms.Form):

    name = fields.CharField(label=u'Название', max_length=Clan.MAX_NAME_LENGTH, min_length=Clan.MIN_NAME_LENGTH)
    abbr = fields.CharField(label=u'Аббревиатура', max_length=Clan.MAX_ABBR_LENGTH, min_length=Clan.MIN_ABBR_LENGTH)
    motto = fields.CharField(label=u'Девиз', max_length=Clan.MAX_MOTTO_LENGTH)
    description = bbcode.BBField(label=u'Описание', max_length=Clan.MAX_DESCRIPTION_LENGTH)

    def clean_name(self):
        name = self.cleaned_data['name']

        if Clan.objects.filter(name=name).exists():
            raise ValidationError(u'Клан с таким названием уже существует')

        return name

    def clean_abbr(self):
        abbr = self.cleaned_data['abbr']

        if Clan.objects.filter(abbr=abbr).exists():
            raise ValidationError(u'Клан с такой аббревиатурой уже существует')

        return abbr


class MembershipRequestForm(forms.Form):
    text = bbcode.BBField(label=u'Описание', max_length=MembershipRequest.MAX_TEXT_LENGTH)
