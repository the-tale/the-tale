# coding: utf-8

import datetime

from django.core.urlresolvers import reverse
from django.conf import settings as project_settings

from dext.utils import s11n
from dext.utils.decorators import nested_commit_on_success

from common.utils.decorators import lazy_property
from common.utils import bbcode
from common.utils.prototypes import BasePrototype

from accounts.prototypes import AccountPrototype

from game.prototypes import TimePrototype

from forum.prototypes import ThreadPrototype, PostPrototype, SubCategoryPrototype
from forum.models import MARKUP_METHOD

from game.bills.models import Bill, Vote, Actor
from game.bills.conf import bills_settings
from game.bills.exceptions import BillException
from game.bills.relations import BILL_STATE
from game.bills import signals


class BillPrototype(BasePrototype):
    _model_class = Bill
    _readonly = ('id', 'type', 'created_at', 'updated_at', 'caption', 'rationale', 'votes_for',
                 'votes_against', 'forum_thread_id', 'min_votes_required', 'min_votes_percents_required')
    _bidirectional = ('approved_by_moderator', 'state')
    _get_by = ('id', )

    @property
    def data(self):
        from game.bills.bills import deserialize_bill
        if not hasattr(self, '_data'):
            self._data = deserialize_bill(s11n.from_json(self._model.technical_data))
        return self._data

    @property
    def rationale_html(self): return bbcode.render(self._model.rationale)

    @lazy_property
    def forum_thread(self): return ThreadPrototype.get_by_id(self.forum_thread_id)

    @property
    def votes_for_percents(self):
        if self.votes_against + self.votes_for == 0:
            return 0
        return float(self.votes_for) / (self.votes_for + self.votes_against)

    @property
    def owner(self):
        if not hasattr(self, '_owner'):
            self._owner = AccountPrototype(self._model.owner)
        return self._owner

    def set_remove_initiator(self, initiator): self._model.remove_initiator = initiator._model

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
                   (self._model.updated_at + datetime.timedelta(seconds=bills_settings.BILL_LIVE_TIME) - datetime.datetime.now()))

    def recalculate_votes(self):
        self._model.votes_for = Vote.objects.filter(bill=self._model, value=True).count()
        self._model.votes_against = Vote.objects.filter(bill=self._model, value=False).count()

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
        if not self.state._is_VOTING:
            raise BillException('trying to apply bill in not voting state')

        if not self.approved_by_moderator:
            raise BillException('trying to apply bill which did not approved by moderator')

        if self.time_before_end_step != datetime.timedelta(seconds=0):
            raise BillException('trying to apply bill before voting period was end')

        self.recalculate_votes()

        self._model.min_votes_required = bills_settings.MIN_VOTES_NUMBER
        self._model.min_votes_percents_required = bills_settings.MIN_VOTES_PERCENT


        if (self.is_percents_barier_not_passed or self.is_votes_barier_not_passed ):
            self.state = BILL_STATE.REJECTED
            self.save()

            PostPrototype.create(ThreadPrototype(self._model.forum_thread),
                                 self.owner,
                                 u'Законопроект отклонён.',
                                 technical=True)

            signals.bill_processed.send(self.__class__, bill=self)
            return False

        self.data.apply()

        self.state = BILL_STATE.ACCEPTED
        self.save()

        PostPrototype.create(ThreadPrototype(self._model.forum_thread),
                             self.owner,
                             u'Законопроект принят. Изменения вступят в силу в ближайшее время.',
                             technical=True)

        signals.bill_processed.send(self.__class__, bill=self)
        return True


    @nested_commit_on_success
    def update(self, form):

        Vote.objects.filter(bill_id=self.id).delete()

        self.data.initialize_with_user_data(form)

        self._model.updated_at = datetime.datetime.now()
        self._model.caption = form.c.caption
        self._model.rationale = form.c.rationale
        self._model.votes_for = 1
        self._model.votes_against = 0
        self._model.approved_by_moderator = False

        self.save()

        ActorPrototype.update_actors(self, self.data.actors)

        VotePrototype.create(self.owner, self, True)

        thread = ThreadPrototype(self._model.forum_thread)
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
        self._model.approved_by_moderator = form.c.approved
        self.save()

        signals.bill_moderated.send(self.__class__, bill=self)


    @classmethod
    @nested_commit_on_success
    def create(cls, owner, caption, rationale, bill):

        model = Bill.objects.create(owner=owner._model,
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

        ActorPrototype.update_actors(bill_prototype, bill_prototype.data.actors)

        VotePrototype.create(owner, bill_prototype, True)

        signals.bill_created.send(sender=cls, bill=bill_prototype)

        return bill_prototype

    def save(self):
        self._model.technical_data=s11n.to_json(self.data.serialize())
        self._model.save()

    @nested_commit_on_success
    def remove(self, initiator):
        self.set_remove_initiator(initiator)
        self.state = BILL_STATE.REMOVED
        self.save()

        thread = ThreadPrototype(self._model.forum_thread)
        thread.caption = thread.caption + u' [удалён]'
        thread.save()

        PostPrototype.create(thread,
                             initiator,
                             u'Законопроект был удалён',
                             technical=True)

        signals.bill_removed.send(self.__class__, bill=self)


class ActorPrototype(BasePrototype):
    _model_class = Actor
    _readonly = ('id',)
    _bidirectional = ()

    @classmethod
    def get_query_for_bill(cls, bill):
        return list(Actor.objects.filter(bill_id=bill.id))

    @classmethod
    def create(cls, bill, place=None):

        model = Actor.objects.create(bill=bill._model,
                                     place=place._model if place else None)
        return cls(model)

    @classmethod
    @nested_commit_on_success
    def update_actors(cls, bill, actors):
        from game.map.places.prototypes import PlacePrototype

        Actor.objects.filter(bill_id=bill.id).delete()

        for actor in actors:
            cls.create(bill,
                       place=actor if isinstance(actor, PlacePrototype) else None)


    def save(self):
        self._model.save()


class VotePrototype(BasePrototype):
    _model_class = Vote
    _readonly = ('id', 'value')
    _bidirectional = ()

    @classmethod
    def get_for(cls, owner, bill):
        try:
            return Vote.objects.get(owner=owner._model, bill=bill._model)
        except Vote.DoesNotExist:
            return None

    @property
    def owner(self): return AccountPrototype(self._model.owner)

    @classmethod
    def create(cls, owner, bill, value):

        model = Vote.objects.create(owner=owner._model,
                                    bill=bill._model,
                                    value=value)

        return cls(model)

    def save(self):
        self._model.save()
