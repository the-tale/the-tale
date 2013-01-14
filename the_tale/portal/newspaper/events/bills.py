# coding: utf-8

from portal.newspaper.models import NEWSPAPER_EVENT_SECTION, NEWSPAPER_EVENT_TYPE

class EventBillBase(object):

    SECTION = NEWSPAPER_EVENT_SECTION.BILLS
    TEMPLATE = None
    TYPE = None

    def __init__(self, bill_id=None, bill_type=None, caption=None):
        self.bill_id = bill_id
        self.bill_type = bill_type
        self.caption = caption

    def serialize(self):
        return {'bill_id': self.bill_id,
                'bill_type': self.bill_type,
                'caption': self.caption,
                'type': self.TYPE}

    def deserialize(self, data):
        self.bill_id = data['bill_id']
        self.bill_type = data['bill_type']
        self.caption = data['caption']


class EventBillCreated(EventBillBase):
    TYPE = NEWSPAPER_EVENT_TYPE.BILL_CREATED
    TEMPLATE = 'newspaper/events/bill_created.html'

class EventBillEdited(EventBillBase):
    TYPE = NEWSPAPER_EVENT_TYPE.BILL_EDITED
    TEMPLATE = 'newspaper/events/bill_edited.html'

class EventBillRemoved(EventBillBase):
    TYPE = NEWSPAPER_EVENT_TYPE.BILL_REMOVED
    TEMPLATE = 'newspaper/events/bill_removed.html'

class EventBillProcessed(EventBillBase):
    TYPE = NEWSPAPER_EVENT_TYPE.BILL_PROCESSED
    TEMPLATE = 'newspaper/events/bill_processed.html'

    def __init__(self, accepted=None, **kwargs):
        super(EventBillProcessed, self).__init__(**kwargs)
        self.accepted = accepted

    def serialize(self):
        data = super(EventBillProcessed, self).serialize()
        data['accepted'] = self.accepted
        return data

    def deserialize(self, data):
        super(EventBillProcessed, self).deserialize(data)
        self.accepted = data['accepted']
