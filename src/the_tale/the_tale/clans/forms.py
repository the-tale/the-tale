
import smart_imports

smart_imports.all()


class ClanForm(dext_forms.Form):

    name = dext_fields.CharField(label='Название', max_length=models.Clan.MAX_NAME_LENGTH, min_length=models.Clan.MIN_NAME_LENGTH)
    abbr = dext_fields.CharField(label='Аббревиатура (до %d символов)' % models.Clan.MAX_ABBR_LENGTH, max_length=models.Clan.MAX_ABBR_LENGTH, min_length=models.Clan.MIN_ABBR_LENGTH)
    motto = dext_fields.CharField(label='Девиз', max_length=models.Clan.MAX_MOTTO_LENGTH)
    description = utils_bbcode.BBField(label='Описание', max_length=models.Clan.MAX_DESCRIPTION_LENGTH)

    accept_requests_from_players = dext_fields.BooleanField(required=False,
                                                            label='Игроки могут отправлять запросы на вступление в гильдию')


class MembershipRequestForm(dext_forms.Form):
    text = utils_bbcode.BBField(label='Текст', max_length=models.MembershipRequest.MAX_TEXT_LENGTH)


class RoleForm(dext_forms.Form):
    role = dext_fields.TypedChoiceField(label='звание', coerce=relations.MEMBER_ROLE.get_from_name)

    def __init__(self, allowed_roles, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [(role, role.text) for role in allowed_roles]
