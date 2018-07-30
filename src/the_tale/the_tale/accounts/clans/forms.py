
import smart_imports

smart_imports.all()


class ClanForm(dext_forms.Form):

    name = dext_fields.CharField(label='Название', max_length=models.Clan.MAX_NAME_LENGTH, min_length=models.Clan.MIN_NAME_LENGTH)
    abbr = dext_fields.CharField(label='Аббревиатура (до %d символов)' % models.Clan.MAX_ABBR_LENGTH, max_length=models.Clan.MAX_ABBR_LENGTH, min_length=models.Clan.MIN_ABBR_LENGTH)
    motto = dext_fields.CharField(label='Девиз', max_length=models.Clan.MAX_MOTTO_LENGTH)
    description = utils_bbcode.BBField(label='Описание', max_length=models.Clan.MAX_DESCRIPTION_LENGTH)


class MembershipRequestForm(dext_forms.Form):
    text = utils_bbcode.BBField(label='Текст', max_length=models.MembershipRequest.MAX_TEXT_LENGTH)
