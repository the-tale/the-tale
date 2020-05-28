
import smart_imports

smart_imports.all()


class BillPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Bill
    _readonly = ('id', 'type', 'created_at', 'updated_at', 'caption', 'votes_for',
                 'votes_against', 'votes_refrained', 'forum_thread_id', 'min_votes_percents_required',
                 'voting_end_at', 'ended_at', 'chronicle_on_accepted')
    _bidirectional = ('approved_by_moderator', 'state', 'is_declined', 'applyed_at_turn')
    _get_by = ('id', )

    @classmethod
    def accepted_bills_count(cls, account_id):
        return cls._model_class.objects.filter(owner_id=account_id, state=relations.BILL_STATE.ACCEPTED).count()

    @utils_decorators.lazy_property
    def declined_by(self):
        return BillPrototype.get_by_id(self._model.declined_by_id)

    @utils_decorators.lazy_property
    def depends_on(self):
        if not self._model.depends_on_id:
            return None

        return BillPrototype.get_by_id(self._model.depends_on_id)

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = bills.deserialize_bill(s11n.from_json(self._model.technical_data))
        return self._data

    @utils_decorators.lazy_property
    def forum_thread(self):
        return forum_prototypes.ThreadPrototype.get_by_id(self.forum_thread_id)

    @property
    def votes_for_percents(self):
        if self.votes_against + self.votes_for == 0:
            return 0
        return float(self.votes_for) / (self.votes_for + self.votes_against)

    @property
    def owner(self):
        if not hasattr(self, '_owner'):
            self._owner = accounts_prototypes.AccountPrototype(self._model.owner)
        return self._owner

    def set_remove_initiator(self, initiator):
        self._model.remove_initiator = initiator._model

    @property
    def user_form_initials(self):
        special_initials = self.data.user_form_initials()
        special_initials.update({'caption': self.caption,
                                 'depends_on': self._model.depends_on_id,
                                 'chronicle_on_accepted': self.chronicle_on_accepted})
        return special_initials

    @property
    def moderator_form_initials(self):
        special_initials = self.user_form_initials
        special_initials.update({'approved': self.approved_by_moderator})
        return special_initials

    @property
    def time_before_voting_end(self):
        return max(datetime.timedelta(seconds=0),
                   (self._model.updated_at + datetime.timedelta(seconds=conf.settings.BILL_LIVE_TIME) - datetime.datetime.now()))

    def recalculate_votes(self):
        self._model.votes_for = models.Vote.objects.filter(bill=self._model, type=relations.VOTE_TYPE.FOR).count()
        self._model.votes_against = models.Vote.objects.filter(bill=self._model, type=relations.VOTE_TYPE.AGAINST).count()
        self._model.votes_refrained = models.Vote.objects.filter(bill=self._model, type=relations.VOTE_TYPE.REFRAINED).count()

    @property
    def is_percents_barier_not_passed(self): return self.votes_for_percents < conf.settings.MIN_VOTES_PERCENT

    @property
    def last_bill_event_text(self):
        if self.state.is_ACCEPTED:
            return 'одобрена запись'
        if self.state.is_REJECTED:
            return 'отклонена запись'
        if self.state.is_VOTING:
            if (self.updated_at - self.created_at).total_seconds() > 1:
                return 'исправлена запись'
            else:
                return 'создана запись'
        if self.state.is_STOPPED:
            return 'запись утратила смысл'
        raise exceptions.UnknownLastEventTextError(bill_id=self.id)

    @classmethod
    def get_minimum_created_time_of_active_bills(cls):
        created_at = models.Bill.objects.filter(state=relations.BILL_STATE.VOTING).aggregate(django_models.Min('created_at'))['created_at__min']
        return created_at if created_at is not None else datetime.datetime.now()

    @classmethod
    def get_recently_modified_bills(cls, bills_number):
        return [cls(model=model) for model in cls._model_class.objects.exclude(state=relations.BILL_STATE.REMOVED).order_by('-updated_at')[:bills_number]]

    @property
    def actors(self):
        actors = []

        for actor in self.data.actors:
            if actor is None:
                continue
            if actor not in actors:
                actors.append(actor)

        return actors

    def can_vote(self, hero):
        allowed_places_ids = places_logic.get_hero_popularity(hero.id).get_allowed_places_ids(conf.settings.PLACES__TO_ACCESS_VOTING,
                                                                                              border=c.BILLS_FAME_BORDER)
        place_found = False
        place_allowed = False

        for actor in self.actors:
            if isinstance(actor, places_objects.Place):

                if actor.is_new:
                    return True

                place_found = True
                if actor.id in allowed_places_ids:
                    place_allowed = True

        if place_found and not place_allowed:
            return False

        return True

    def has_meaning(self):
        if self.depends_on and self.depends_on.state.break_dependent_bills:
            return False

        return self.data.has_meaning()

    def stop(self):
        if not self.state.is_VOTING:
            raise exceptions.StopBillInWrongStateError(bill_id=self.id)

        results_text = 'Итоги голосования: %d «за», %d «против» (итого %.1f%% «за»), %d «воздержалось».' % (self.votes_for,
                                                                                                            self.votes_against,
                                                                                                            round(self.votes_for_percents, 3) * 100,
                                                                                                            self.votes_refrained)

        with django_transaction.atomic():
            self._model.voting_end_at = datetime.datetime.now()
            self.state = relations.BILL_STATE.STOPPED
            self.save()

            forum_prototypes.PostPrototype.create(forum_prototypes.ThreadPrototype(self._model.forum_thread),
                                                  accounts_logic.get_system_user(),
                                                  'Запись потеряла смысл, голосование остановлено. %s' % results_text,
                                                  technical=True)

    def apply(self):
        if not self.state.is_VOTING:
            raise exceptions.ApplyBillInWrongStateError(bill_id=self.id)

        if not self.approved_by_moderator:
            raise exceptions.ApplyUnapprovedBillError(bill_id=self.id)

        if self.time_before_voting_end != datetime.timedelta(seconds=0):
            raise exceptions.ApplyBillBeforeVoteWasEndedError(bill_id=self.id)

        self.recalculate_votes()

        self._model.min_votes_percents_required = conf.settings.MIN_VOTES_PERCENT

        results_text = 'Итоги голосования: %d «за», %d «против» (итого %.1f%% «за»), %d «воздержалось».' % (self.votes_for,
                                                                                                            self.votes_against,
                                                                                                            round(self.votes_for_percents, 3) * 100,
                                                                                                            self.votes_refrained)

        self._model.voting_end_at = datetime.datetime.now()

        self.applyed_at_turn = game_turn.number()

        with django_transaction.atomic():

            if self.is_percents_barier_not_passed:
                self.state = relations.BILL_STATE.REJECTED
                self.save()

                forum_prototypes.PostPrototype.create(forum_prototypes.ThreadPrototype(self._model.forum_thread),
                                                      accounts_logic.get_system_user(),
                                                      'Запись отклонена.\n\n%s' % results_text,
                                                      technical=True)
                return False

            self.data.apply(self)

            self.state = relations.BILL_STATE.ACCEPTED

            with achievements_storage.achievements.verify(type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_ACCEPTED_BILLS, object=self.owner):
                self.save()

            forum_prototypes.PostPrototype.create(forum_prototypes.ThreadPrototype(self._model.forum_thread),
                                                  accounts_logic.get_system_user(),
                                                  'Запись одобрена. Изменения вступят в силу в ближайшее время.\n\n%s' % results_text,
                                                  technical=True)

            for actor in self.actors:
                if isinstance(actor, places_objects.Place):
                    places_logic.register_effect(place_id=actor.id,
                                                 attribute=places_relations.ATTRIBUTE.STABILITY,
                                                 value=-self.type.stability,
                                                 name='запись №{}'.format(self.id),
                                                 delta=actor.attrs.stability_renewing_speed,
                                                 refresh_effects=True,
                                                 refresh_places=True,
                                                 info={'source': 'bills',
                                                       'bills_id': self.id})

        self.owner.update_actual_bills()

        chronicle_tt_services.chronicle.cmd_add_event(tags=[actor.meta_object().tag for actor in self.actors] + [self.meta_object().tag],
                                                      message=self.chronicle_on_accepted,
                                                      attributes={'bill_id': self.id})

        return True

    @django_transaction.atomic
    def end(self):
        if not self.state.is_ACCEPTED:
            raise exceptions.EndBillInWrongStateError(bill_id=self.id)

        if self.ended_at is not None:
            raise exceptions.EndBillAlreadyEndedError(bill_id=self.id)

        results_text = 'Срок действия [url="%s%s"]записи[/url] истёк.' % (django_settings.SITE_URL,
                                                                          django_reverse('game:bills:show', args=[self.id]))

        self._model.ended_at = datetime.datetime.now()

        self.data.end(self)

        self.save()

        forum_prototypes.PostPrototype.create(forum_prototypes.ThreadPrototype(self._model.forum_thread),
                                              accounts_logic.get_system_user(),
                                              results_text,
                                              technical=True)

        return True

    @django_transaction.atomic
    def decline(self, decliner):
        if not self.state.is_ACCEPTED:
            raise exceptions.DeclinedBillInWrongStateError(bill_id=self.id)

        self.is_declined = True
        self._model.declined_by = decliner._model
        self._model.ended_at = datetime.datetime.now()
        self.data.decline(bill=self)
        self.save()

    def bill_info_text(self, text):
        rendered_text = '''%(text)s

[b]название:[/b] %(caption)s

[b]запись в летописи о принятии:[/b]
%(on_accepted)s
''' % {'text': text,
            'caption': self.caption,
            'on_accepted': self.chronicle_on_accepted if self.chronicle_on_accepted else '—'}

        return rendered_text

    def _initialize_with_form(self, form, is_updated=True):
        self.data.initialize_with_form(form)

        if is_updated:
            self._model.updated_at = datetime.datetime.now()

        self._model.caption = form.c.caption
        self._model.depends_on_id = form.c.depends_on
        self._model.approved_by_moderator = False
        self._model.chronicle_on_accepted = form.c.chronicle_on_accepted

    @django_transaction.atomic
    def update(self, form):

        models.Vote.objects.filter(bill_id=self.id).delete()

        VotePrototype.create(self.owner, self, relations.VOTE_TYPE.FOR)

        self._initialize_with_form(form)

        self.recalculate_votes()

        self.save()

        ActorPrototype.update_actors(self, self.actors)

        thread = forum_prototypes.ThreadPrototype(self._model.forum_thread)
        thread.caption = form.c.caption
        thread.save()

        text = '[url="%s%s"]Запись[/url] была отредактирована, все голоса сброшены.' % (django_settings.SITE_URL,
                                                                                        django_reverse('game:bills:show', args=[self.id]))

        forum_prototypes.PostPrototype.create(thread,
                                              accounts_logic.get_system_user(),
                                              self.bill_info_text(text),
                                              technical=True)

    @django_transaction.atomic
    def update_by_moderator(self, form):
        self._initialize_with_form(form, is_updated=False)
        self._model.approved_by_moderator = form.c.approved
        self.save()

    @classmethod
    @django_transaction.atomic
    def create(cls, owner, caption, bill, chronicle_on_accepted, depends_on_id=None):

        model = models.Bill.objects.create(owner=owner._model,
                                           type=bill.type,
                                           caption=caption,
                                           created_at_turn=game_turn.number(),
                                           technical_data=s11n.to_json(bill.serialize()),
                                           state=relations.BILL_STATE.VOTING,
                                           depends_on_id=depends_on_id,
                                           chronicle_on_accepted=chronicle_on_accepted,
                                           votes_for=1)  # author always wote for bill

        bill_prototype = cls(model)

        text = 'Обсуждение [url="%s%s"]записи[/url]' % (django_settings.SITE_URL,
                                                        django_reverse('game:bills:show', args=[model.id]))

        thread = forum_prototypes.ThreadPrototype.create(forum_prototypes.SubCategoryPrototype.get_by_uid(conf.settings.FORUM_CATEGORY_UID),
                                                         caption=caption,
                                                         author=accounts_logic.get_system_user(),
                                                         text=bill_prototype.bill_info_text(text),
                                                         technical=True,
                                                         markup_method=forum_relations.MARKUP_METHOD.POSTMARKUP)

        model.forum_thread = thread._model
        model.save()

        ActorPrototype.update_actors(bill_prototype, bill_prototype.actors)

        VotePrototype.create(owner, bill_prototype, relations.VOTE_TYPE.FOR)

        return bill_prototype

    @classmethod
    def is_active_bills_limit_reached(cls, account):
        bills_count = cls._model_class.objects.filter(owner_id=account.id, state=relations.BILL_STATE.VOTING).count()

        if account.is_premium:
            return bills_count >= c.PREMIUM_ACCOUNT_MAX_ACTIVE_BILLS

        return bills_count >= c.FREE_ACCOUNT_MAX_ACTIVE_BILLS

    def save(self):
        self._model.technical_data = s11n.to_json(self.data.serialize())
        self._model.save()

    @django_transaction.atomic
    def remove(self, initiator):
        self.set_remove_initiator(initiator)
        self.state = relations.BILL_STATE.REMOVED
        self.save()

        thread = forum_prototypes.ThreadPrototype(self._model.forum_thread)
        thread.caption = thread.caption + ' [удалена]'
        thread.save()

        forum_prototypes.PostPrototype.create(thread,
                                              accounts_logic.get_system_user(),
                                              'Запись была удалена',
                                              technical=True)

    @classmethod
    def get_applicable_bills_ids(cls):
        time_barrier = datetime.datetime.now() - datetime.timedelta(seconds=conf.settings.BILL_LIVE_TIME)
        return cls._model_class.objects.filter(state=relations.BILL_STATE.VOTING,
                                               approved_by_moderator=True,
                                               updated_at__lt=time_barrier).order_by('updated_at').values_list('id', flat=True)

    @classmethod
    def get_active_bills_ids(cls):
        return cls._model_class.objects.filter(state=relations.BILL_STATE.VOTING).values_list('id', flat=True)

    @property
    def is_delayed(self):
        return self.depends_on and self.depends_on.state.is_VOTING

    def meta_object(self):
        return meta_relations.Bill.create_from_object(self)


class ActorPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Actor
    _readonly = ('id',)
    _bidirectional = ()

    @classmethod
    def get_query_for_bill(cls, bill):
        return list(models.Actor.objects.filter(bill_id=bill.id))

    @classmethod
    def create(cls, bill, place=None):

        model = models.Actor.objects.create(bill=bill._model,
                                            place_id=place.id if place else None)
        return cls(model)

    @classmethod
    @django_transaction.atomic
    def update_actors(cls, bill, actors):
        models.Actor.objects.filter(bill_id=bill.id).delete()

        for actor in actors:
            cls.create(bill,
                       place=actor if isinstance(actor, places_objects.Place) else None)

    def save(self):
        self._model.save()


class VotePrototype(utils_prototypes.BasePrototype):
    _model_class = models.Vote
    _readonly = ('id', 'type')
    _bidirectional = ()

    @classmethod
    def votes_count(cls, account_id): return cls._model_class.objects.filter(owner_id=account_id).count()

    @classmethod
    def votes_for_count(cls, account_id): return cls._model_class.objects.filter(owner_id=account_id, type=relations.VOTE_TYPE.FOR).count()

    @classmethod
    def votes_against_count(cls, account_id): return cls._model_class.objects.filter(owner_id=account_id, type=relations.VOTE_TYPE.AGAINST).count()

    @classmethod
    def get_for(cls, owner, bill):
        try:
            return models.Vote.objects.get(owner=owner._model, bill=bill._model)
        except models.Vote.DoesNotExist:
            return None

    @property
    def owner(self): return accounts_prototypes.AccountPrototype(self._model.owner)

    @classmethod
    def create(cls, owner, bill, type):  # pylint: disable=W0622

        with achievements_storage.achievements.verify(type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_AGAINST, object=owner):
            with achievements_storage.achievements.verify(type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_FOR, object=owner):
                with achievements_storage.achievements.verify(type=achievements_relations.ACHIEVEMENT_TYPE.POLITICS_VOTES_TOTAL, object=owner):
                    model = models.Vote.objects.create(owner=owner._model,
                                                       bill=bill._model,
                                                       type=type)

        return cls(model)

    def save(self):
        self._model.save()
