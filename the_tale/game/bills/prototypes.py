# coding: utf-8
import datetime

from dext.utils import s11n
from dext.utils.decorators import nested_commit_on_success

from game.prototypes import TimePrototype

from game.bills.models import Bill, BILL_STATE, BILL_REJECTED_REASONS
from game.bills.bills import deserialize_bill
from game.bills.conf import bills_settings

class BillPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(model=Bill.objects.get(id=id_))
        except Bill.DoesNotExist:
            return None

    @property
    def id(self): return self.model.id

    @property
    def state(self):
        if not hasattr(self, '_state'):
            self._state = BILL_STATE(self.model.state)
        return self._state

    @property
    def created_at(self): return self.model.created_at

    @property
    def updated_at(self): return self.model.updated_at

    @property
    def rejected_state(self):
        if not hasattr(self, '_rejected_state'):
            self._rejected_state = BILL_REJECTED_REASONS(self.model.rejected_state)
        return self._rejected_state

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = deserialize_bill(s11n.from_json(self.model.technical_data))
        return self._data

    @property
    def caption(self): return self.model.caption

    @property
    def rationale(self): return self.model.rationale

    @property
    def votes_for(self): return self.model.votes_for

    @property
    def votes_for_percents(self):
        if self.votes_against == 0:
            return 0
        return float(self.votes_for / (self.votes_for + self.votes_against))

    @property
    def votes_against(self): return self.model.votes_against

    @property
    def owner(self): return self.model.owner

    @property
    def time_before_end_step(self):
        if self.state.is_proposal:
            return max(datetime.timedelta(seconds=0),
                       (self.model.step_started_at + datetime.timedelta(seconds=bills_settings.PROPOSAL_LIVE_TIME) - datetime.datetime.now()))
        elif self.state.is_voting:
            return max(datetime.timedelta(seconds=0),
                       (self.model.step_started_at + datetime.timedelta(seconds=bills_settings.VOTING_LIVE_TIME) - datetime.datetime.now()))

    @classmethod
    @nested_commit_on_success
    def create(cls, owner, caption, rationale, bill):
        from forum.logic import create_thread
        from forum.models import SubCategory, MARKUP_METHOD

        thread = create_thread(SubCategory.objects.get(slug=bills_settings.FORUM_PROPOSAL_CATEGORY_SLUG),
                               caption=caption,
                               author=owner,
                               text=rationale,# TODO: replace by special
                               markup_method=MARKUP_METHOD.MARKDOWN)


        model = Bill.objects.create(owner=owner,
                                    type=bill.type,
                                    caption=caption,
                                    rationale=rationale,
                                    created_at_turn=TimePrototype.get_current_turn_number(),
                                    technical_data=s11n.to_json(bill.serialize()),
                                    forum_proposal_thread=thread)

        return cls(model)
