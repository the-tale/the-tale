# coding: utf-8

import datetime

from django.core.urlresolvers import reverse
from django.conf import settings as project_settings

from dext.utils import s11n
from dext.utils.decorators import nested_commit_on_success

from the_tale.common.utils.decorators import lazy_property
from the_tale.common.utils import bbcode
from the_tale.common.utils.prototypes import BasePrototype

from the_tale.accounts.logic import get_system_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.prototypes import TimePrototype
from the_tale.game.balance import constants as c

from the_tale.forum.prototypes import ThreadPrototype, PostPrototype, SubCategoryPrototype
from the_tale.forum.models import MARKUP_METHOD

from the_tale.game.bills.models import Bill, Vote, Actor
from the_tale.game.bills.conf import bills_settings
from the_tale.game.bills import exceptions
from the_tale.game.bills.relations import BILL_STATE, VOTE_TYPE, BILL_DURATION
from the_tale.game.bills import signals


class BillPrototype(BasePrototype):
    _model_class = Bill
    _readonly = ('id', 'type', 'created_at', 'updated_at', 'caption', 'rationale', 'votes_for',
                 'votes_against', 'votes_refrained', 'forum_thread_id', 'min_votes_percents_required',
                 'voting_end_at', 'ended_at', 'ends_at_turn', 'duration')
    _bidirectional = ('approved_by_moderator', 'state', 'is_declined')
    _get_by = ('id', )

    @lazy_property
    def declined_by(self): return BillPrototype.get_by_id(self._model.declined_by_id)

    @property
    def data(self):
        from the_tale.game.bills.bills import deserialize_bill
        if not hasattr(self, '_data'):
            self._data = deserialize_bill(s11n.from_json(self._model.technical_data))
        return self._data

    @property
    def time_before_end(self):
        return datetime.timedelta(seconds=(self.ends_at_turn - TimePrototype.get_current_turn_number()) * c.TURN_DELTA)

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
                                 'rationale': self.rationale,
                                 'duration': self.duration})
        return special_initials

    @property
    def moderator_form_initials(self):
        special_initials = self.data.moderator_form_initials
        special_initials.update({'approved': self.approved_by_moderator})
        return special_initials

    @property
    def time_before_voting_end(self):
        return max(datetime.timedelta(seconds=0),
                   (self._model.updated_at + datetime.timedelta(seconds=bills_settings.BILL_LIVE_TIME) - datetime.datetime.now()))

    def recalculate_votes(self):
        self._model.votes_for = Vote.objects.filter(bill=self._model, type=VOTE_TYPE.FOR).count()
        self._model.votes_against = Vote.objects.filter(bill=self._model, type=VOTE_TYPE.AGAINST).count()
        self._model.votes_refrained = Vote.objects.filter(bill=self._model, type=VOTE_TYPE.REFRAINED).count()

    @property
    def is_percents_barier_not_passed(self): return self.votes_for_percents < bills_settings.MIN_VOTES_PERCENT

    @property
    def last_bill_event_text(self):
        if self.state._is_ACCEPTED:
            return u'принят закон'
        if self.state._is_REJECTED:
            return u'отклонён закон'
        if self.state._is_VOTING:
            if (self.updated_at - self.created_at).seconds > 1:
                return u'исправлен закон'
            else:
                return u'выдвинут закон'
        raise exceptions.UnknownLastEventTextError(bill_id=self.id)

    @classmethod
    def get_minimum_created_time_of_active_bills(cls):
        from django.db.models import Min
        created_at =  Bill.objects.filter(state=BILL_STATE.VOTING).aggregate(Min('created_at'))['created_at__min']
        return created_at if created_at is not None else datetime.datetime.now()

    @classmethod
    def get_recently_modified_bills(cls, bills_number):
        return [cls(model=model) for model in cls._model_class.objects.exclude(state=BILL_STATE.REMOVED).order_by('-updated_at')[:bills_number]]

    def can_vote(self, hero):
        from the_tale.game.map.places.prototypes import PlacePrototype

        allowed_places_ids = hero.places_history.get_allowed_places_ids(bills_settings.PLACES__TO_ACCESS_VOTING)

        place_found = False
        place_allowed = False

        for actor in self.data.actors:
            if isinstance(actor, PlacePrototype):
                place_found = True
                if actor.id in allowed_places_ids:
                    place_allowed = True

        if place_found and not place_allowed:
            return False

        return True

    @nested_commit_on_success
    def apply(self):
        if not self.state._is_VOTING:
            raise exceptions.ApplyBillInWrongStateError(bill_id=self.id)

        if not self.approved_by_moderator:
            raise exceptions.ApplyUnapprovedBillError(bill_id=self.id)

        if self.time_before_voting_end != datetime.timedelta(seconds=0):
            raise exceptions.ApplyUnapprovedBillError(bill_id=self.id)

        self.recalculate_votes()

        self._model.min_votes_percents_required = bills_settings.MIN_VOTES_PERCENT

        results_text = u'Итоги голосования: %d «за», %d «против» (итого %d%% «за»), %d «воздержалось».' % (self.votes_for,
                                                                                                           self.votes_against,
                                                                                                           self.votes_for_percents*100,
                                                                                                           self.votes_refrained)

        self._model.voting_end_at = datetime.datetime.now()
        if not self.duration._is_UNLIMITED:
            self._model.ends_at_turn = TimePrototype.get_current_turn_number() + self.duration.game_months * c.TURNS_IN_GAME_MONTH

        if self.is_percents_barier_not_passed:
            self.state = BILL_STATE.REJECTED
            self.save()

            PostPrototype.create(ThreadPrototype(self._model.forum_thread),
                                 get_system_user(),
                                 u'Законопроект отклонён.\n\n%s' % results_text,
                                 technical=True)

            signals.bill_processed.send(self.__class__, bill=self)
            return False

        self.data.apply(self)

        self.state = BILL_STATE.ACCEPTED
        self.save()

        PostPrototype.create(ThreadPrototype(self._model.forum_thread),
                             get_system_user(),
                             u'Законопроект принят. Изменения вступят в силу в ближайшее время.\n\n%s' % results_text,
                             technical=True)

        signals.bill_processed.send(self.__class__, bill=self)
        return True

    @nested_commit_on_success
    def end(self):
        if not self.state._is_ACCEPTED:
            raise exceptions.EndBillInWrongStateError(bill_id=self.id)

        if self.ended_at is not None:
            raise exceptions.EndBillAlreadyEndedError(bill_id=self.id)

        if self.ends_at_turn > TimePrototype.get_current_turn_number():
            raise exceptions.EndBillBeforeTimeError(bill_id=self.id)

        results_text = u'Срок действия [url="%s%s"]закона[/url] истёк.' % (project_settings.SITE_URL,
                                                                           reverse('game:bills:show', args=[self.id]) )

        self._model.ended_at = datetime.datetime.now()

        self.data.end(self)

        self.save()

        PostPrototype.create(ThreadPrototype(self._model.forum_thread),
                             get_system_user(),
                             results_text,
                             technical=True)

        signals.bill_ended.send(self.__class__, bill=self)
        return True

    @nested_commit_on_success
    def decline(self, decliner):
        if not self.state._is_ACCEPTED:
            raise exceptions.DeclinedBillInWrongStateError(bill_id=self.id)

        self.is_declined = True
        self._model.declined_by = decliner._model
        self._model.ended_at = datetime.datetime.now()
        self.data.decline(bill=self)
        self.save()

    def bill_info_text(self, text):
        return u'''%s

[b]название:[/b] %s

[b]обоснование:[/b]
%s
''' % (text, self.caption, self.rationale)

    @nested_commit_on_success
    def update(self, form):

        Vote.objects.filter(bill_id=self.id).delete()

        VotePrototype.create(self.owner, self, VOTE_TYPE.FOR)

        self.data.initialize_with_user_data(form)

        self._model.updated_at = datetime.datetime.now()
        self._model.caption = form.c.caption
        self._model.rationale = form.c.rationale
        self._model.duration = form.c.duration
        self._model.approved_by_moderator = False

        self.recalculate_votes()

        self.save()

        ActorPrototype.update_actors(self, self.data.actors)

        thread = ThreadPrototype(self._model.forum_thread)
        thread.caption = form.c.caption
        thread.save()

        text = u'[url="%s%s"]Законопроект[/url] был отредактирован, все голоса сброшены.' % (project_settings.SITE_URL,
                                                                                             reverse('game:bills:show', args=[self.id]) )

        PostPrototype.create(thread,
                             get_system_user(),
                             self.bill_info_text(text),
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
    def create(cls, owner, caption, rationale, bill, duration=BILL_DURATION.UNLIMITED):

        model = Bill.objects.create(owner=owner._model,
                                    type=bill.type,
                                    caption=caption,
                                    rationale=rationale,
                                    created_at_turn=TimePrototype.get_current_turn_number(),
                                    technical_data=s11n.to_json(bill.serialize()),
                                    state=BILL_STATE.VOTING,
                                    duration=duration,
                                    votes_for=1) # author always wote for bill

        bill_prototype = cls(model)

        text = u'обсуждение [url="%s%s"]закона[/url]' % (project_settings.SITE_URL,
                                                         reverse('game:bills:show', args=[model.id]) )

        thread = ThreadPrototype.create(SubCategoryPrototype.get_by_uid(bills_settings.FORUM_CATEGORY_UID),
                                        caption=caption,
                                        author=get_system_user(),
                                        text=bill_prototype.bill_info_text(text),
                                        technical=True,
                                        markup_method=MARKUP_METHOD.POSTMARKUP)

        model.forum_thread = thread._model
        model.save()


        ActorPrototype.update_actors(bill_prototype, bill_prototype.data.actors)

        VotePrototype.create(owner, bill_prototype, VOTE_TYPE.FOR)

        signals.bill_created.send(sender=cls, bill=bill_prototype)

        return bill_prototype

    @classmethod
    def is_active_bills_limit_reached(cls, account):
        return cls._model_class.objects.filter(owner_id=account.id, state=BILL_STATE.VOTING).exists()

    def save(self):
        self._model.technical_data = s11n.to_json(self.data.serialize())
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
                             get_system_user(),
                             u'Законопроект был удалён',
                             technical=True)

        signals.bill_removed.send(self.__class__, bill=self)

    @classmethod
    def get_applicable_bills(cls):
        bills_models = cls._model_class.objects.filter(state=BILL_STATE.VOTING,
                                                       approved_by_moderator=True,
                                                       updated_at__lt=datetime.datetime.now() - datetime.timedelta(seconds=bills_settings.BILL_LIVE_TIME))
        return [cls(model=model) for model in bills_models]

    @classmethod
    def get_bills_to_end(cls):
        bills_models = cls._model_class.objects.filter(state=BILL_STATE.ACCEPTED,
                                                       ended_at=None,
                                                       ends_at_turn__lt=TimePrototype.get_current_turn_number())
        return [cls(model=model) for model in bills_models]




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
        from the_tale.game.map.places.prototypes import PlacePrototype

        Actor.objects.filter(bill_id=bill.id).delete()

        for actor in actors:
            cls.create(bill,
                       place=actor if isinstance(actor, PlacePrototype) else None)


    def save(self):
        self._model.save()


class VotePrototype(BasePrototype):
    _model_class = Vote
    _readonly = ('id', 'type')
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
    def create(cls, owner, bill, type): # pylint: disable=W0622

        model = Vote.objects.create(owner=owner._model,
                                    bill=bill._model,
                                    type=type)

        return cls(model)

    def save(self):
        self._model.save()
