
import smart_imports

smart_imports.all()


class EditProfileForm(utils_forms.Form):

    nick = utils_fields.RegexField(label='Имя',
                                   regex=conf.settings.NICK_REGEX,
                                   min_length=conf.settings.NICK_MIN_LENGTH,
                                   max_length=conf.settings.NICK_MAX_LENGTH)

    email = utils_fields.EmailField(label='Email (логин)')

    password = utils_fields.PasswordField(label='Новый пароль',
                                          required=False)


class SettingsForm(utils_forms.Form):
    personal_messages_subscription = utils_fields.BooleanField(required=False,
                                                               label='Получать письма о новых личных сообщениях')

    news_subscription = utils_fields.BooleanField(required=False,
                                                  label='Получать письма о новостях')

    accept_invites_from_clans = utils_fields.BooleanField(required=False,
                                                          label='Гильдии могут приглашать вас присоединиться к ним')

    description = bbcode_fields.BBField(required=False,
                                        label='Несколько слов о Вас, для страницы Вашего аккаунта',
                                        max_length=conf.settings.MAX_ACCOUNT_DESCRIPTION_LENGTH)

    gender = utils_fields.TypedChoiceField(required=True,
                                           label='Пол (необходим для корректного создания фраз, в которых упоминается игрок)',
                                           choices=((game_relations.GENDER.MALE, game_relations.GENDER.MALE.text),
                                                    (game_relations.GENDER.FEMALE, game_relations.GENDER.FEMALE.text)),
                                           coerce=game_relations.GENDER.get_from_name,
                                           initial=game_relations.GENDER.MALE)


class LoginForm(utils_forms.Form):

    email = utils_fields.EmailField(label='Email')
    password = utils_fields.PasswordField(label='Пароль')
    remember = utils_fields.BooleanField(label='Запомнить меня', required=False)


class ResetPasswordForm(utils_forms.Form):

    email = utils_fields.EmailField(label='Email')


class GiveAwardForm(utils_forms.Form):
    type = utils_fields.TypedChoiceField(label='тип', choices=relations.AWARD_TYPE.choices(), coerce=relations.AWARD_TYPE.get_from_name)
    description = utils_fields.TextField(label='обоснование', required=False)


class BanForm(utils_forms.Form):
    ban_type = utils_fields.TypedChoiceField(label='тип', choices=relations.BAN_TYPE.choices(), coerce=relations.BAN_TYPE.get_from_name)
    ban_time = utils_fields.TypedChoiceField(label='длительность', choices=relations.BAN_TIME.choices(), coerce=relations.BAN_TIME.get_from_name)

    description = utils_fields.TextField(label='обоснование', required=True)


class SendMoneyForm(utils_forms.Form):

    money = utils_fields.IntegerField(label='Печеньки')

    comment = utils_fields.CharField(label='Комментарий (для истории платежей)', min_length=10)

    def clean_money(self):
        money = self.cleaned_data['money']

        if money < conf.settings.MINIMUM_SEND_MONEY:
            raise django_forms.ValidationError('Сумма должна быть не меньше %(min_money)s печенек' % {'min_money': conf.settings.MINIMUM_SEND_MONEY})

        return money
