# coding: utf-8
import datetime

from dext.utils import s11n
from dext.utils.decorators import nested_commit_on_success

from game.prototypes import TimePrototype

from forum.logic import create_post

from game.bills.models import Bill, Vote, BILL_STATE
from game.bills.bills import deserialize_bill
from game.bills.conf import bills_settings
from game.bills.exceptions import BillException

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

    def get_state(self):
        if not hasattr(self, '_state'):
            self._state = BILL_STATE(self.model.state)
        return self._state
    def set_state(self, value):
        self.state.update(value)
        self.model.state = self.state.value
    state = property(get_state, set_state)

    @property
    def created_at(self): return self.model.created_at

    @property
    def updated_at(self): return self.model.updated_at

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
        if self.votes_against + self.votes_for == 0:
            return 0
        return float(self.votes_for) / (self.votes_for + self.votes_against)

    @property
    def votes_against(self): return self.model.votes_against

    @property
    def owner(self): return self.model.owner

    @property
    def user_form_initials(self):
        special_initials = self.data.user_form_initials
        special_initials.update({'caption': self.caption,
                                 'rationale': self.rationale})
        return special_initials


    @property
    def moderator_form_initials(self):
        special_initials = self.data.moderator_form_initials
        special_initials.update({'approved': self.approved_by_moderator})
        return special_initials

    @property
    def time_before_end_step(self):
        return max(datetime.timedelta(seconds=0),
                   (self.model.updated_at + datetime.timedelta(seconds=bills_settings.BILL_LIVE_TIME) - datetime.datetime.now()))

    @property
    def forum_thread_id(self): return self.model.forum_thread_id

    @property
    def min_votes_required(self): return self.model.min_votes_required

    @property
    def min_votes_percents_required(self): return self.model.min_votes_percents_required

    def get_approved_by_moderator(self): return self.model.approved_by_moderator
    def set_approved_by_moderator(self, value): self.model.approved_by_moderator = value
    approved_by_moderator = property(get_approved_by_moderator, set_approved_by_moderator)

    def recalculate_votes(self):
        self.model.votes_for = Vote.objects.filter(bill=self.model, value=True).count()
        self.model.votes_against = Vote.objects.filter(bill=self.model, value=False).count()

    @nested_commit_on_success
    def apply(self):
        if not self.state.is_voting:
            raise BillException('trying to apply bill in not voting state')

        if not self.approved_by_moderator:
            raise BillException('trying to apply bill which did not approved by moderator')

        if self.time_before_end_step != datetime.timedelta(seconds=0):
            raise BillException('trying to apply bill before voting period was end')

        self.recalculate_votes()

        self.model.min_votes_required = bills_settings.MIN_VOTES_NUMBER
        self.model.min_votes_percents_required = bills_settings.MIN_VOTES_PERCENT


        if (self.votes_for_percents < bills_settings.MIN_VOTES_PERCENT or
            self.votes_for < bills_settings.MIN_VOTES_NUMBER):
            self.model.state = BILL_STATE.REJECTED
            self.save()
            return False

        self.data.apply()

        self.model.state = BILL_STATE.ACCEPTED
        self.save()

        return True


    @nested_commit_on_success
    def update(self, form):

        Vote.objects.filter(bill_id=self.id).delete()

        self.data.initialize_with_user_data(form)
        self.model.updated_at = datetime.datetime.now()
        self.model.caption = form.c.caption
        self.model.rationale = form.c.rationale
        self.model.votes_for = 1
        self.model.votes_against = 0
        self.model.approved_by_moderator = False

        self.save()

        VotePrototype.create(self.owner, self, True)

        create_post(self.model.forum_thread.subcategory,
                    self.model.forum_thread,
                    self.owner,
                    u'Законопроект был отредактирован, все голоса сброшены.')

    @nested_commit_on_success
    def update_by_moderator(self, form):
        self.data.initialize_with_moderator_data(form)
        self.model.approved_by_moderator = form.c.approved
        self.save()


    @classmethod
    @nested_commit_on_success
    def create(cls, owner, caption, rationale, bill):
        from forum.logic import create_thread
        from forum.models import SubCategory, MARKUP_METHOD

        thread = create_thread(SubCategory.objects.get(slug=bills_settings.FORUM_CATEGORY_SLUG),
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
                                    votes_for=1, # author always wote for bill
                                    # min_votes_required=bills_settings.MIN_VOTES_NUMBER, # must be setup on voting end
                                    # min_votes_percents_required=bills_settings.MIN_VOTES_PERCENT,
                                    forum_thread=thread)

        bill = cls(model)

        VotePrototype.create(owner, bill, True)

        return bill

    def save(self):
        self.model.technical_data=s11n.to_json(self.data.serialize())
        self.model.save()

    @nested_commit_on_success
    def remove(self):
        self.model.forum_thread.delete()
        self.model.delete()


class VotePrototype(object):

    def __init__(self, model=None):
        self.model = model

    @classmethod
    def get_for(cls, owner, bill):
        try:
            return Vote.objects.get(owner=owner, bill=bill.model)
        except Vote.DoesNotExist:
            return None

    @property
    def owner(self): return self.model.owner

    @property
    def value(self): return self.model.value

    @classmethod
    def create(cls, owner, bill, value):

        model = Vote.objects.create(owner=owner,
                                    bill=bill.model,
                                    value=value)

        return cls(model)

    def save(self):
        self.model.save()
