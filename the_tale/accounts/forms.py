# coding: utf-8

from dext.forms import forms, fields

from the_tale.accounts.conf import accounts_settings
from the_tale.accounts.relations import AWARD_TYPE, BAN_TYPE, BAN_TIME


class EditProfileForm(forms.Form):

    nick = fields.RegexField(label=u'Имя',
                             regex=accounts_settings.NICK_REGEX,
                             min_length=accounts_settings.NICK_MIN_LENGTH,
                             max_length=accounts_settings.NICK_MAX_LENGTH)

    email = fields.EmailField(label=u'Email (логин)')

    password = fields.PasswordField(label=u'Новый пароль',
                                    required=False)

class SettingsForm(forms.Form):
    personal_messages_subscription = fields.BooleanField(required=False,
                                                         label=u'получать письма о новых личных сообщениях')


class LoginForm(forms.Form):

    email = fields.EmailField(label=u'Email')
    password = fields.PasswordField(label=u'Пароль')
    remember = fields.BooleanField(label=u'Запомнить меня', required=False)


class ResetPasswordForm(forms.Form):

    email = fields.EmailField(label=u'Email')


class GiveAwardForm(forms.Form):
    type = fields.TypedChoiceField(label=u'тип', choices=AWARD_TYPE._choices(), coerce=AWARD_TYPE._get_from_name)
    description = fields.TextField(label=u'обоснование', required=False)


class BanForm(forms.Form):
    ban_type = fields.TypedChoiceField(label=u'тип', choices=BAN_TYPE._choices(), coerce=BAN_TYPE._get_from_name)
    ban_time = fields.TypedChoiceField(label=u'длительность', choices=BAN_TIME._choices(), coerce=BAN_TIME._get_from_name)

    description = fields.TextField(label=u'обоснование', required=True)
