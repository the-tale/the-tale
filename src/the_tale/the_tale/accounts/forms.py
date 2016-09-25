# coding: utf-8

from django.forms import ValidationError

from dext.forms import forms, fields

from the_tale.common.utils import bbcode

from the_tale.accounts import conf
from the_tale.accounts import relations


class EditProfileForm(forms.Form):

    nick = fields.RegexField(label=u'Имя',
                             regex=conf.accounts_settings.NICK_REGEX,
                             min_length=conf.accounts_settings.NICK_MIN_LENGTH,
                             max_length=conf.accounts_settings.NICK_MAX_LENGTH)

    email = fields.EmailField(label=u'Email (логин)')

    password = fields.PasswordField(label=u'Новый пароль',
                                    required=False)

class SettingsForm(forms.Form):
    personal_messages_subscription = fields.BooleanField(required=False,
                                                         label=u'получать письма о новых личных сообщениях')

    news_subscription = fields.BooleanField(required=False,
                                            label=u'получать письма о новостях')

    description = bbcode.BBField(required=False, label=u'Несколько слов о Вас, для страницы Вашего аккаунта', max_length=conf.accounts_settings.MAX_ACCOUNT_DESCRIPTION_LENGTH)


class LoginForm(forms.Form):

    email = fields.EmailField(label=u'Email')
    password = fields.PasswordField(label=u'Пароль')
    remember = fields.BooleanField(label=u'Запомнить меня', required=False)


class ResetPasswordForm(forms.Form):

    email = fields.EmailField(label=u'Email')


class GiveAwardForm(forms.Form):
    type = fields.TypedChoiceField(label=u'тип', choices=relations.AWARD_TYPE.choices(), coerce=relations.AWARD_TYPE.get_from_name)
    description = fields.TextField(label=u'обоснование', required=False)


class BanForm(forms.Form):
    ban_type = fields.TypedChoiceField(label=u'тип', choices=relations.BAN_TYPE.choices(), coerce=relations.BAN_TYPE.get_from_name)
    ban_time = fields.TypedChoiceField(label=u'длительность', choices=relations.BAN_TIME.choices(), coerce=relations.BAN_TIME.get_from_name)

    description = fields.TextField(label=u'обоснование', required=True)



class SendMoneyForm(forms.Form):

    money = fields.IntegerField(label=u'Печеньки')

    comment = fields.CharField(label=u'Комментарий (для истории платежей)', min_length=10)

    def clean_money(self):
        money = self.cleaned_data['money']

        if money < conf.accounts_settings.MINIMUM_SEND_MONEY:
            raise ValidationError(u'Сумма должна быть не меньше %(min_money)s печенек' % {'min_money': conf.accounts_settings.MINIMUM_SEND_MONEY})

        return money
