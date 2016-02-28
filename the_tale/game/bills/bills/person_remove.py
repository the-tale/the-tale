# coding: utf-8

from the_tale.game.bills.relations import BILL_TYPE
from the_tale.game.bills.bills.base_person_bill import BasePersonBill


class PersonRemove(BasePersonBill):

    type = BILL_TYPE.PERSON_REMOVE

    UserForm = None
    ModeratorForm = None

    CAPTION = u'Исключение из Совета'
    DESCRIPTION = u'В случае, если горожанин утратил доверие духов-хранителей, его можно исключить из Совета города. Исключать можно только наименее влиятельных советников (но советник будет исключён, даже если за время голосования существенно увеличит своё влияние и станет самым влиятельным горожанином).'

    def has_meaning(self):
        return False

    def apply(self, bill=None):
        raise NotImplementedError()
