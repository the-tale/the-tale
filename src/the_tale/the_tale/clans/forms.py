
import smart_imports

smart_imports.all()


class ClanForm(utils_forms.Form):

    name = utils_fields.CharField(label='Название', max_length=models.Clan.MAX_NAME_LENGTH, min_length=models.Clan.MIN_NAME_LENGTH)
    abbr = utils_fields.CharField(label='Аббревиатура (до %d символов)' % models.Clan.MAX_ABBR_LENGTH, max_length=models.Clan.MAX_ABBR_LENGTH, min_length=models.Clan.MIN_ABBR_LENGTH)
    motto = utils_fields.CharField(label='Девиз', max_length=models.Clan.MAX_MOTTO_LENGTH)
    description = utils_bbcode.BBField(label='Описание', max_length=models.Clan.MAX_DESCRIPTION_LENGTH)

    linguistics_name = linguistics_forms.WordField(word_type=utg_relations.WORD_TYPE.NOUN,
                                                   skip_markers=(utg_relations.NOUN_FORM.COUNTABLE,),
                                                   label='Название гильдии для генерации текста')

    accept_requests_from_players = utils_fields.BooleanField(required=False,
                                                             label='Игроки могут отправлять запросы на вступление в гильдию')


class MembershipRequestForm(utils_forms.Form):
    text = utils_bbcode.BBField(label='Текст', max_length=models.MembershipRequest.MAX_TEXT_LENGTH)


class RoleForm(utils_forms.Form):
    role = utils_fields.TypedChoiceField(label='звание', coerce=relations.MEMBER_ROLE.get_from_name)

    def __init__(self, allowed_roles, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [(role, role.text) for role in allowed_roles]
