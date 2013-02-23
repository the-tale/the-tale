# coding: utf-8
import datetime
import postmarkup

from django.core.urlresolvers import reverse
from django.conf import settings as project_settings

from dext.utils import s11n
from dext.utils.decorators import nested_commit_on_success

from accounts.prototypes import AccountPrototype

from game.prototypes import TimePrototype

from forum.prototypes import ThreadPrototype, PostPrototype, SubCategoryPrototype
from forum.models import MARKUP_METHOD

from game.bills.models import Bill, Vote, BILL_STATE
from game.bills.bills import deserialize_bill
from game.bills.conf import bills_settings
from game.bills.exceptions import BillException
from game.bills import signals


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
    def type(self): return self.model.type

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
    def rationale_html(self): return postmarkup.render_bbcode(self.model.rationale)

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
    def owner(self):
        if not hasattr(self, '_owner'):
            self._owner = AccountPrototype(self.model.owner)
        return self._owner

    def set_remove_initiator(self, initiator): self.model.remove_initiator = initiator.model

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

    @property
    def is_votes_barier_not_passed(self): return self.votes_for < bills_settings.MIN_VOTES_NUMBER

    @property
    def is_percents_barier_not_passed(self): return self.votes_for_percents < bills_settings.MIN_VOTES_PERCENT

    @classmethod
    def get_minimum_created_time_of_active_bills(self):
        from django.db.models import Min
        created_at =  Bill.objects.filter(state=BILL_STATE.VOTING).aggregate(Min('created_at'))['created_at__min']
        return created_at if created_at is not None else datetime.datetime.now()

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


        if (self.is_percents_barier_not_passed or self.is_votes_barier_not_passed ):
            self.set_state(BILL_STATE.REJECTED)
            self.save()

            PostPrototype.create(ThreadPrototype(self.model.forum_thread),
                                 self.owner,
                                 u'Законопроект отклонён.',
                                 technical=True)

            signals.bill_processed.send(self.__class__, bill=self)
            return False

        self.data.apply()

        self.set_state(BILL_STATE.ACCEPTED)
        self.save()

        PostPrototype.create(ThreadPrototype(self.model.forum_thread),
                             self.owner,
                             u'Законопроект принят. Изменения вступят в силу в ближайшее время.',
                             technical=True)

        signals.bill_processed.send(self.__class__, bill=self)
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

        thread = ThreadPrototype(self.model.forum_thread)
        thread.caption = form.c.caption
        thread.save()

        PostPrototype.create(thread,
                             self.owner,
                             u'Законопроект был отредактирован, все голоса сброшены.',
                             technical=True)

        signals.bill_edited.send(self.__class__, bill=self)

    @nested_commit_on_success
    def update_by_moderator(self, form):
        self.data.initialize_with_moderator_data(form)
        self.model.approved_by_moderator = form.c.approved
        self.save()

        signals.bill_moderated.send(self.__class__, bill=self)


    @classmethod
    @nested_commit_on_success
    def create(cls, owner, caption, rationale, bill):

        model = Bill.objects.create(owner=owner.model,
                                    type=bill.type,
                                    caption=caption,
                                    rationale=rationale,
                                    created_at_turn=TimePrototype.get_current_turn_number(),
                                    technical_data=s11n.to_json(bill.serialize()),
                                    votes_for=1) # author always wote for bill

        text=u'обсуждение [url="%s%s"]закона[/url]' % (project_settings.SITE_URL,
                                                       reverse('game:bills:show', args=[model.id]) )

        thread = ThreadPrototype.create(SubCategoryPrototype.get_by_slug(bills_settings.FORUM_CATEGORY_SLUG),
                                        caption=caption,
                                        author=owner,
                                        text=text + u'\n\n' + rationale,
                                        markup_method=MARKUP_METHOD.POSTMARKUP)

        model.forum_thread = thread.model
        model.save()


        bill_prototype = cls(model)

        VotePrototype.create(owner, bill_prototype, True)

        signals.bill_created.send(sender=cls, bill=bill_prototype)

        return bill_prototype

    def save(self):
        self.model.technical_data=s11n.to_json(self.data.serialize())
        self.model.save()

    @nested_commit_on_success
    def remove(self, initiator):
        self.set_remove_initiator(initiator)
        self.state = BILL_STATE.REMOVED
        self.save()

        thread = ThreadPrototype(self.model.forum_thread)
        thread.caption = thread.caption + u' [удалён]'
        thread.save()

        PostPrototype.create(thread,
                             initiator,
                             u'Законопроект был удалён',
                             technical=True)

        signals.bill_removed.send(self.__class__, bill=self)



class VotePrototype(object):

    def __init__(self, model=None):
        self.model = model

    @classmethod
    def get_for(cls, owner, bill):
        try:
            return Vote.objects.get(owner=owner.model, bill=bill.model)
        except Vote.DoesNotExist:
            return None

    @property
    def id(self): return self.model.id

    @property
    def owner(self): return AccountPrototype(self.model.owner)

    @property
    def value(self): return self.model.value

    @classmethod
    def create(cls, owner, bill, value):

        model = Vote.objects.create(owner=owner.model,
                                    bill=bill.model,
                                    value=value)

        return cls(model)

    def save(self):
        self.model.save()
