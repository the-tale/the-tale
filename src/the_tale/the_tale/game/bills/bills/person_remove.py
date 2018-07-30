
import smart_imports

smart_imports.all()


class PersonRemove(base_person_bill.BasePersonBill):
    type = relations.BILL_TYPE.PERSON_REMOVE

    UserForm = None
    ModeratorForm = None

    CAPTION = 'Исключение из Совета'
    DESCRIPTION = 'В случае, если горожанин утратил доверие духов-хранителей, его можно исключить из Совета города. Исключать можно только наименее влиятельных советников (но советник будет исключён, даже если за время голосования существенно увеличит своё влияние и станет самым влиятельным горожанином).'

    def has_meaning(self):
        return False

    def apply(self, bill=None):
        raise NotImplementedError()
