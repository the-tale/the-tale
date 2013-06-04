# coding: utf-8

from django import forms as django_forms

from dext.forms import forms, fields

from accounts.payments.logic import real_amount_to_game


INITIAL_AMOUNT = 10


class DengiOnlineForm(forms.Form):

    real_amount = fields.IntegerField(label=u'USD', initial=INITIAL_AMOUNT)
    game_amount = fields.IntegerField(label=u'Печеньки',
                                      initial=real_amount_to_game(INITIAL_AMOUNT),
                                      widget=django_forms.TextInput(attrs={'disabled': 'disabled',
                                                                           'readonly':'readonly'}))

    def clean(self):
        cleaned_data = super(DengiOnlineForm, self).clean()

        if 'game_amount' not in cleaned_data or 'real_amount' not in cleaned_data:
            return cleaned_data

        if cleaned_data['game_amount'] != real_amount_to_game(cleaned_data['real_amount']):
            raise django_forms.ValidationError(u'Расхождение в ожидаемой сумме игровой валюты')

        return cleaned_data

    def clean_real_amount(self):
        amount = self.cleaned_data['real_amount']

        if amount <= 0:
            raise django_forms.ValidationError(u'Размер суммы должен быть больше 0')

        return amount


class GMForm(forms.Form):
    amount = fields.IntegerField(label=u'Печеньки')
    description = fields.TextField(label=u'Описание', required=True)
