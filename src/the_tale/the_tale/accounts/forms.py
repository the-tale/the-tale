# coding: utf-8

from django.forms import ValidationError

from dext.forms import forms, fields

from the_tale.common.utils import bbcode

from the_tale.accounts import conf
from the_tale.accounts import relations
from the_tale.game.relations import GENDER


class EditProfileForm(forms.Form):

    nick = fields.RegexField(label='Имя',
                             regex=conf.accounts_settings.NICK_REGEX,
                             min_length=conf.accounts_settings.NICK_MIN_LENGTH,
                             max_length=conf.accounts_settings.NICK_MAX_LENGTH)

    email = fields.EmailField(label='Email (логин)')

    password = fields.PasswordField(label='Новый пароль',
                                    required=False)


profile_gender = ((GENDER.MASCULINE, GENDER.MASCULINE.text), (GENDER.FEMININE, GENDER.FEMININE.text))


class SettingsForm(forms.Form):
    personal_messages_subscription = fields.BooleanField(required=False,
                                                         label='получать письма о новых личных сообщениях')

    news_subscription = fields.BooleanField(required=False,
                                            label='получать письма о новостях')

    description = bbcode.BBField(required=False, label='Несколько слов о Вас, для страницы Вашего аккаунта', max_length=conf.accounts_settings.MAX_ACCOUNT_DESCRIPTION_LENGTH)

    gender = fields.TypedChoiceField(required=False, label='Пол', choices=profile_gender, coerce=GENDER.get_from_name, initial=GENDER.MASCULINE.value)


class LoginForm(forms.Form):

    email = fields.EmailField(label='Email')
    password = fields.PasswordField(label='Пароль')
    remember = fields.BooleanField(label='Запомнить меня', required=False)


class ResetPasswordForm(forms.Form):

    email = fields.EmailField(label='Email')


class GiveAwardForm(forms.Form):
    type = fields.TypedChoiceField(label='тип', choices=relations.AWARD_TYPE.choices(), coerce=relations.AWARD_TYPE.get_from_name)
    description = fields.TextField(label='обоснование', required=False)


class BanForm(forms.Form):
    ban_type = fields.TypedChoiceField(label='тип', choices=relations.BAN_TYPE.choices(), coerce=relations.BAN_TYPE.get_from_name)
    ban_time = fields.TypedChoiceField(label='длительность', choices=relations.BAN_TIME.choices(), coerce=relations.BAN_TIME.get_from_name)

    description = fields.TextField(label='обоснование', required=True)


class SendMoneyForm(forms.Form):

    money = fields.IntegerField(label='Печеньки')

    comment = fields.CharField(label='Комментарий (для истории платежей)', min_length=10)

    def clean_money(self):
        money = self.cleaned_data['money']

        if money < conf.accounts_settings.MINIMUM_SEND_MONEY:
            raise ValidationError('Сумма должна быть не меньше %(min_money)s печенек' % {'min_money': conf.accounts_settings.MINIMUM_SEND_MONEY})

        return money
