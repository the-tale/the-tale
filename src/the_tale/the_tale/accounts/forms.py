
import smart_imports

smart_imports.all()


class EditProfileForm(dext_forms.Form):

    nick = dext_fields.RegexField(label='Имя',
                                  regex=conf.settings.NICK_REGEX,
                                  min_length=conf.settings.NICK_MIN_LENGTH,
                                  max_length=conf.settings.NICK_MAX_LENGTH)

    email = dext_fields.EmailField(label='Email (логин)')

    password = dext_fields.PasswordField(label='Новый пароль',
                                         required=False)


class SettingsForm(dext_forms.Form):
    personal_messages_subscription = dext_fields.BooleanField(required=False,
                                                              label='Получать письма о новых личных сообщениях')

    news_subscription = dext_fields.BooleanField(required=False,
                                                 label='Получать письма о новостях')

    accept_invites_from_clans = dext_fields.BooleanField(required=False,
                                                         label='Гильдии могут приглашать вас присоединиться к ним')

    description = utils_bbcode.BBField(required=False, label='Несколько слов о Вас, для страницы Вашего аккаунта', max_length=conf.settings.MAX_ACCOUNT_DESCRIPTION_LENGTH)

    gender = dext_fields.TypedChoiceField(required=True,
                                          label='Пол (необходим для корректного создания фраз, в которых упоминается игрок)',
                                          choices=((game_relations.GENDER.MALE, game_relations.GENDER.MALE.text),
                                                   (game_relations.GENDER.FEMALE, game_relations.GENDER.FEMALE.text)),
                                          coerce=game_relations.GENDER.get_from_name,
                                          initial=game_relations.GENDER.MALE)


class LoginForm(dext_forms.Form):

    email = dext_fields.EmailField(label='Email')
    password = dext_fields.PasswordField(label='Пароль')
    remember = dext_fields.BooleanField(label='Запомнить меня', required=False)


class ResetPasswordForm(dext_forms.Form):

    email = dext_fields.EmailField(label='Email')


class GiveAwardForm(dext_forms.Form):
    type = dext_fields.TypedChoiceField(label='тип', choices=relations.AWARD_TYPE.choices(), coerce=relations.AWARD_TYPE.get_from_name)
    description = dext_fields.TextField(label='обоснование', required=False)


class BanForm(dext_forms.Form):
    ban_type = dext_fields.TypedChoiceField(label='тип', choices=relations.BAN_TYPE.choices(), coerce=relations.BAN_TYPE.get_from_name)
    ban_time = dext_fields.TypedChoiceField(label='длительность', choices=relations.BAN_TIME.choices(), coerce=relations.BAN_TIME.get_from_name)

    description = dext_fields.TextField(label='обоснование', required=True)


class SendMoneyForm(dext_forms.Form):

    money = dext_fields.IntegerField(label='Печеньки')

    comment = dext_fields.CharField(label='Комментарий (для истории платежей)', min_length=10)

    def clean_money(self):
        money = self.cleaned_data['money']

        if money < conf.settings.MINIMUM_SEND_MONEY:
            raise django_forms.ValidationError('Сумма должна быть не меньше %(min_money)s печенек' % {'min_money': conf.settings.MINIMUM_SEND_MONEY})

        return money
