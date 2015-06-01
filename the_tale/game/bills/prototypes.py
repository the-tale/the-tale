# coding: utf-8

import datetime

from django.core.urlresolvers import reverse
from django.conf import settings as project_settings
from django.db import transaction

from dext.common.utils import s11n

from the_tale.common.utils.decorators import lazy_property
from the_tale.common.utils import bbcode
from the_tale.common.utils.prototypes import BasePrototype

from the_tale.accounts.logic import get_system_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.accounts.achievements.storage import achievements_storage
from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE

from the_tale.game.prototypes import TimePrototype

from the_tale.game.map.places.prototypes import PlacePrototype

from the_tale.forum.prototypes import ThreadPrototype, PostPrototype, SubCategoryPrototype
from the_tale.forum.models import MARKUP_METHOD

from the_tale.game.bills.models import Bill, Vote, Actor
from the_tale.game.bills.conf import bills_settings
from the_tale.game.bills import exceptions
from the_tale.game.bills.relations import BILL_STATE, VOTE_TYPE
from the_tale.game.bills import signals
from the_tale.game.bills import logic


class BillPrototype(BasePrototype):
    _model_class = Bill
    _readonly = ('id', 'type', 'created_at', 'updated_at', 'caption', 'rationale', 'votes_for',
                 'votes_against', 'votes_refrained', 'forum_thread_id', 'min_votes_percents_required',
                 'voting_end_at', 'ended_at', 'chronicle_on_accepted')
    _bidirectional = ('approved_by_moderator', 'state', 'is_declined', 'applyed_at_turn')
    _get_by = ('id', )


    @classmethod
    def accepted_bills_count(cls, account_id):
        return cls._model_class.objects.filter(owner_id=account_id, state=BILL_STATE.ACCEPTED).count()

    @lazy_property
    def declined_by(self): return BillPrototype.get_by_id(self._model.declined_by_id)

    @property
    def data(self):
        from the_tale.game.bills.bills import deserialize_bill
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
                                 'rationale': self.rationale,
                                 'chronicle_on_accepted': self.chronicle_on_accepted})
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
        if self.state.is_ACCEPTED:
            return u'принят закон'
        if self.state.is_REJECTED:
            return u'отклонён закон'
        if self.state.is_VOTING:
            if (self.updated_at - self.created_at).total_seconds() > 1:
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
        allowed_places_ids = hero.places_history.get_allowed_places_ids(bills_settings.PLACES__TO_ACCESS_VOTING)

        place_found = False
        place_allowed = False

        for actor in self.data.actors:
            if isinstance(actor, PlacePrototype):

                if actor.is_new:
                    return True

                place_found = True
                if actor.id in allowed_places_ids:
                    place_allowed = True

        if place_found and not place_allowed:
            return False

        return True

    @transaction.atomic
    def apply(self):
        if not self.state.is_VOTING:
            raise exceptions.ApplyBillInWrongStateError(bill_id=self.id)

        if not self.approved_by_moderator:
            raise exceptions.ApplyUnapprovedBillError(bill_id=self.id)

        if self.time_before_voting_end != datetime.timedelta(seconds=0):
            raise exceptions.ApplyBillBeforeVoteWasEndedError(bill_id=self.id)

        self.recalculate_votes()

        self._model.min_votes_percents_required = bills_settings.MIN_VOTES_PERCENT

        results_text = u'Итоги голосования: %d «за», %d «против» (итого %.1f%% «за»), %d «воздержалось».' % (self.votes_for,
                                                                                                            self.votes_against,
                                                                                                            round(self.votes_for_percents, 3)*100,
                                                                                                            self.votes_refrained)

        self._model.voting_end_at = datetime.datetime.now()

        self.applyed_at_turn = TimePrototype.get_current_turn_number()

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

        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.POLITICS_ACCEPTED_BILLS, object=self.owner):
            self.save()

        PostPrototype.create(ThreadPrototype(self._model.forum_thread),
                             get_system_user(),
                             u'Законопроект принят. Изменения вступят в силу в ближайшее время.\n\n%s' % results_text,
                             technical=True)


        for actor in self.data.actors:
            if isinstance(actor, PlacePrototype):
                actor.stability_modifiers.append((u'закон №%d' % self.id, -self.type.stability))

        logic.initiate_actual_bills_update(self._model.owner_id)

        signals.bill_processed.send(self.__class__, bill=self)
        return True

    @transaction.atomic
    def end(self):
        if not self.state.is_ACCEPTED:
            raise exceptions.EndBillInWrongStateError(bill_id=self.id)

        if self.ended_at is not None:
            raise exceptions.EndBillAlreadyEndedError(bill_id=self.id)

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

    @transaction.atomic
    def decline(self, decliner):
        if not self.state.is_ACCEPTED:
            raise exceptions.DeclinedBillInWrongStateError(bill_id=self.id)

        self.is_declined = True
        self._model.declined_by = decliner._model
        self._model.ended_at = datetime.datetime.now()
        self.data.decline(bill=self)
        self.save()

    def bill_info_text(self, text):
        rendered_text = u'''%(text)s

[b]название:[/b] %(caption)s

[b]запись в летописи о принятии:[/b]
%(on_accepted)s

[b]обоснование:[/b]
%(rationale)s
''' % {'text': text,
       'caption': self.caption,
       'rationale': self.rationale,
       'on_accepted': self.chronicle_on_accepted if self.chronicle_on_accepted else '—'}

        return rendered_text

    @transaction.atomic
    def update(self, form):

        Vote.objects.filter(bill_id=self.id).delete()

        VotePrototype.create(self.owner, self, VOTE_TYPE.FOR)

        self.data.initialize_with_user_data(form)

        self._model.updated_at = datetime.datetime.now()
        self._model.caption = form.c.caption
        self._model.rationale = form.c.rationale
        self._model.approved_by_moderator = False
        self._model.chronicle_on_accepted = form.c.chronicle_on_accepted

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

    @transaction.atomic
    def update_by_moderator(self, form):
        self.data.initialize_with_moderator_data(form)
        self._model.approved_by_moderator = form.c.approved
        self.save()

        signals.bill_moderated.send(self.__class__, bill=self)


    @classmethod
    @transaction.atomic
    def create(cls, owner, caption, rationale, bill, chronicle_on_accepted):

        model = Bill.objects.create(owner=owner._model,
                                    type=bill.type,
                                    caption=caption,
                                    rationale=rationale,
                                    created_at_turn=TimePrototype.get_current_turn_number(),
                                    technical_data=s11n.to_json(bill.serialize()),
                                    state=BILL_STATE.VOTING,
                                    chronicle_on_accepted=chronicle_on_accepted,
                                    votes_for=1) # author always wote for bill

        bill_prototype = cls(model)

        text = u'Обсуждение [url="%s%s"]закона[/url]' % (project_settings.SITE_URL,
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

    @transaction.atomic
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
    @transaction.atomic
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
    def votes_count(cls, account_id): return cls._model_class.objects.filter(owner_id=account_id).count()

    @classmethod
    def votes_for_count(cls, account_id): return cls._model_class.objects.filter(owner_id=account_id, type=VOTE_TYPE.FOR).count()

    @classmethod
    def votes_against_count(cls, account_id): return cls._model_class.objects.filter(owner_id=account_id, type=VOTE_TYPE.AGAINST).count()

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

        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.POLITICS_VOTES_AGAINST, object=owner):
            with achievements_storage.verify(type=ACHIEVEMENT_TYPE.POLITICS_VOTES_FOR, object=owner):
                with achievements_storage.verify(type=ACHIEVEMENT_TYPE.POLITICS_VOTES_TOTAL, object=owner):
                    model = Vote.objects.create(owner=owner._model,
                                                bill=bill._model,
                                                type=type)

        return cls(model)

    def save(self):
        self._model.save()
