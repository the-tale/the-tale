
import smart_imports

smart_imports.all()


BASE_INDEX_FILTERS = [utils_list_filter.reset_element(),
                      utils_list_filter.static_element('автор:', attribute='owner'),
                      utils_list_filter.choice_element('состояние:', attribute='state', choices=[(None, 'все'),
                                                                                                 (relations.BILL_STATE.VOTING.value, 'голосование'),
                                                                                                 (relations.BILL_STATE.ACCEPTED.value, 'принятые'),
                                                                                                 (relations.BILL_STATE.REJECTED.value, 'отклонённые')]),
                      utils_list_filter.choice_element('тип:', attribute='bill_type', choices=[(None, 'все')] + sorted((relations.BILL_TYPE.select('value', 'text')), key=lambda element: element[1])),
                      utils_list_filter.choice_element('город:', attribute='place', choices=lambda x: [(None, 'все')] + places_storage.places.get_choices())]

LOGINED_INDEX_FILTERS = BASE_INDEX_FILTERS + [utils_list_filter.choice_element('голосование:', attribute='voted', choices=[(None, 'все')] + list(relations.VOTED_TYPE.select('value', 'text'))), ]


class UnloginedIndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = BASE_INDEX_FILTERS


class LoginedIndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = LOGINED_INDEX_FILTERS


def argument_to_bill_type(value): return relations.BILL_TYPE(int(value))


def argument_to_bill_state(value): return relations.BILL_STATE(int(value))


@old_views.validator(code='bills.voting_state_required')
def validate_voting_state(resource, *args, **kwargs): return resource.bill.state.is_VOTING


@old_views.validator(code='bills.not_owner', message='Вы не являетесь создателем данной записи')
def validate_ownership(resource, *args, **kwargs): return resource.account.id == resource.bill.owner.id


@old_views.validator(code='bills.moderator_rights_required', message='Вы не являетесь модератором')
def validate_moderator_rights(resource, *args, **kwargs): return resource.can_moderate_bill()

@old_views.validator(code='bills.moderator_rights_required', message='Вы должны являться владельцем записи либо модератором')
def validate_moderator_or_ownership_rights(resource, *args, **kwargs):
    return resource.can_moderate_bill() or resource.account.id == resource.bill.owner.id

@old_views.validator(code='bills.can_not_participate_in_politics', message='Для создания записей в Книге Судеб вам необходимо закончить регистрацию')
def validate_participate_in_politics(resource, *args, **kwargs): return resource.can_participate_in_politics


@old_views.validator(code='bills.can_not_vote', message='Голосовать могут только подписчики')
def validate_can_vote(resource, *args, **kwargs): return resource.can_vote


class BillResource(utils_resources.Resource):

    @utils_decorators.lazy_property
    def hero(self): return heroes_logic.load_hero(account_id=self.account.id)

    @property
    def can_participate_in_politics(self):
        return self.account.is_authenticated and not self.account.is_fast

    @property
    def active_bills_limit_reached(self):
        return prototypes.BillPrototype.is_active_bills_limit_reached(self.account)

    @property
    def can_vote(self):
        return self.account.is_authenticated and self.account.is_premium

    def can_moderate_bill(self):
        return self.account.is_authenticated and self.account.has_perm('bills.moderate_bill')

    @old_views.validate_argument('bill', prototypes.BillPrototype.get_by_id, 'bills', 'Запись не найдена')
    def initialize(self, bill=None, *args, **kwargs):
        super(BillResource, self).initialize(*args, **kwargs)

        self.bill = bill

        if self.bill and self.bill.state.is_REMOVED:
            return self.auto_error('bills.removed', 'Запись удалена')

    @old_views.validate_argument('page', int, 'bills', 'неверная страница')
    @old_views.validate_argument('owner', accounts_prototypes.AccountPrototype.get_by_id, 'bills', 'неверный владелец записи')
    @old_views.validate_argument('state', argument_to_bill_state, 'bills', 'неверное состояние записи')
    @old_views.validate_argument('bill_type', argument_to_bill_type, 'bills', 'неверный тип записи')
    @old_views.validate_argument('voted', relations.VOTED_TYPE, 'bills', 'неверный тип фильтра голосования')
    @old_views.validate_argument('place', lambda value: places_storage.places[int(value)], 'bills', 'не существует такого города')
    @old_views.handler('', method='get')
    def index(self, page=1, owner=None, state=None, bill_type=None, voted=None, place=None):  # pylint: disable=R0914

        bills_query = models.Bill.objects.exclude(state=relations.BILL_STATE.REMOVED)

        if owner is not None:
            bills_query = bills_query.filter(owner_id=owner.id)

        if state is not None:
            bills_query = bills_query.filter(state=state.value)

        if bill_type is not None:
            bills_query = bills_query.filter(type=bill_type.value)

        if place is not None:
            bills_query = bills_query.filter(actor__place_id=place.id).distinct()

        if not self.account.is_authenticated:
            voted = None

        if voted is not None:

            if voted.is_NO:
                bills_query = bills_query.filter(~django_models.Q(vote__owner=self.account._model)).distinct()
            elif voted.is_YES:
                bills_query = bills_query.filter(vote__owner=self.account._model).distinct()
            else:
                bills_query = bills_query.filter(vote__owner=self.account._model, vote__type=voted.vote_type).distinct()

        url_builder = utils_urls.UrlBuilder(django_reverse('game:bills:'), arguments={'owner': owner.id if owner else None,
                                                                                      'state': state.value if state else None,
                                                                                      'bill_type': bill_type.value if bill_type else None,
                                                                                      'voted': voted.value if voted else None,
                                                                                      'place': place.id if place else None})

        IndexFilter = LoginedIndexFilter if self.account.is_authenticated else UnloginedIndexFilter  # pylint: disable=C0103

        index_filter = IndexFilter(url_builder=url_builder, values={'owner': owner.nick if owner else None,
                                                                    'state': state.value if state else None,
                                                                    'bill_type': bill_type.value if bill_type else None,
                                                                    'voted': voted.value if voted else None,
                                                                    'place': place.id if place else None})

        bills_count = bills_query.count()

        page = int(page) - 1

        paginator = utils_pagination.Paginator(page, bills_count, conf.settings.BILLS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        bill_from, bill_to = paginator.page_borders(page)

        displayed_bills = [prototypes.BillPrototype(bill) for bill in bills_query.select_related().order_by('-updated_at')[bill_from:bill_to]]

        votes = {}
        if self.account.is_authenticated:
            votes = dict((vote.bill_id, prototypes.VotePrototype(vote))
                         for vote in models.Vote.objects.filter(bill_id__in=[bill.id for bill in displayed_bills], owner=self.account._model))

        return self.template('bills/index.html',
                             {'bills': displayed_bills,
                              'votes': votes,
                              'page_type': 'index',
                              'BILLS_BY_ID': bills.BILLS_BY_ID,
                              'paginator': paginator,
                              'index_filter': index_filter})

    @accounts_views.validate_operation_disabled_game_stopped()
    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @accounts_views.validate_ban_any()
    @validate_participate_in_politics()
    @old_views.validate_argument('bill_type', argument_to_bill_type, 'bills.new', 'неверный тип записи')
    @old_views.handler('new', method='get')
    def new(self, bill_type):
        if not bill_type.enabled:
            return self.auto_error('bills.new.bill_type.not_enabled', 'Этот тип записи создать нельзя', response_type='html')

        bill_class = bills.BILLS_BY_ID[bill_type.value]
        return self.template('bills/new.html', {'bill_class': bill_class,
                                                'page_type': 'new',
                                                'form': bill_class.get_user_form_create(owner_id=self.account.id)})

    @accounts_views.validate_operation_disabled_game_stopped()
    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @accounts_views.validate_ban_any()
    @validate_participate_in_politics()
    @old_views.validate_argument('bill_type', argument_to_bill_type, 'bills.create', 'неверный тип записи')
    @old_views.handler('create', method='post')
    def create(self, bill_type):

        if not bill_type.enabled:
            return self.json_error('bills.create.bill_type.not_enabled', 'Этот тип записи создать нельзя')

        if datetime.datetime.now() - self.account.created_at < datetime.timedelta(days=conf.settings.MINIMUM_BILL_OWNER_AGE):
            return self.json_error('bills.create.too_young_owner',
                                   'Новые игроки не могут создать запись в течении %d дней с момента регистрации' % conf.settings.MINIMUM_BILL_OWNER_AGE)

        if self.active_bills_limit_reached:
            return self.json_error('bills.create.active_bills_limit_reached', 'Вы не можете создать запись, пока не закончилось голосование по вашим предыдущим предложениям')

        bill_data = bills.BILLS_BY_ID[bill_type.value]()

        user_form = bill_data.get_user_form_create(self.request.POST, owner_id=self.account.id)

        if user_form.is_valid():
            bill_data.initialize_with_form(user_form)
            bill = prototypes.BillPrototype.create(owner=self.account,
                                                   caption=user_form.c.caption,
                                                   depends_on_id=user_form.c.depends_on,
                                                   chronicle_on_accepted=user_form.c.chronicle_on_accepted,
                                                   bill=bill_data)
            return self.json_ok(data={'next_url': django_reverse('game:bills:show', args=[bill.id])})

        return self.json_error('bills.create.form_errors', user_form.errors)

    @old_views.handler('#bill', name='show', method='get')
    def show(self):
        thread_data = forum_views.ThreadPageData()
        thread_data.initialize(account=self.account, thread=self.bill.forum_thread, page=1, inline=True)

        return self.template('bills/show.html', {'bill': self.bill,
                                                 'thread_data': thread_data,
                                                 'VOTE_TYPE': relations.VOTE_TYPE,
                                                 'page_type': 'show',
                                                 'bill_meta_object': meta_relations.Bill.create_from_object(self.bill),
                                                 'vote': prototypes.VotePrototype.get_for(self.account, self.bill) if self.account.is_authenticated else None,
                                                 'can_vote': self.bill.can_vote(self.hero) if self.hero is not None else None})

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @accounts_views.validate_ban_any()
    @validate_participate_in_politics()
    @validate_ownership()
    @validate_voting_state(message='Можно редактировать только записи, находящиеся в стадии голосования')
    @old_views.handler('#bill', 'edit', name='edit', method='get')
    def edit(self):
        user_form = self.bill.data.get_user_form_update(initial=self.bill.user_form_initials,
                                                        owner_id=self.account.id,
                                                        original_bill_id=self.bill.id)
        return self.template('bills/edit.html', {'bill': self.bill,
                                                 'bill_class': self.bill.data,
                                                 'page_type': 'edit',
                                                 'form': user_form})

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @accounts_views.validate_ban_any()
    @validate_participate_in_politics()
    @validate_ownership()
    @validate_voting_state(message='Можно редактировать только записи, находящиеся в стадии голосования')
    @old_views.handler('#bill', 'update', name='update', method='post')
    def update(self):
        user_form = self.bill.data.get_user_form_update(post=self.request.POST,
                                                        owner_id=self.account.id,
                                                        original_bill_id=self.bill.id)

        if user_form.is_valid():
            self.bill.update(user_form)
            return self.json_ok()

        return self.json_error('bills.update.form_errors', user_form.errors)

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @validate_moderator_or_ownership_rights()
    @old_views.handler('#bill', 'delete', name='delete', method='post')
    def delete(self):
        self.bill.remove(self.account)
        return self.json_ok()

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @validate_moderator_rights()
    @validate_voting_state(message='Можно редактировать только записи, находящиеся в стадии голосования')
    @old_views.handler('#bill', 'moderate', name='moderate', method='get')
    def moderation_page(self):
        moderation_form = self.bill.data.get_moderator_form_update(initial=self.bill.moderator_form_initials,
                                                                   original_bill_id=self.bill.id)
        return self.template('bills/moderate.html', {'bill': self.bill,
                                                     'page_type': 'moderate',
                                                     'form': moderation_form})

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @validate_moderator_rights()
    @validate_voting_state(message='Можно редактировать только записи, находящиеся в стадии голосования')
    @old_views.handler('#bill', 'moderate', name='moderate', method='post')
    def moderate(self):
        moderator_form = self.bill.data.get_moderator_form_update(post=self.request.POST,
                                                                  original_bill_id=self.bill.id)

        if moderator_form.is_valid():
            self.bill.update_by_moderator(moderator_form, self.account)
            return self.json_ok()

        return self.json_error('bills.moderate.form_errors', moderator_form.errors)

    @accounts_views.validate_operation_disabled_game_stopped()
    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    @accounts_views.validate_ban_any()
    @validate_participate_in_politics()
    @validate_can_vote()
    @validate_voting_state(message='На данной стадии за запись нельзя голосовать')
    @old_views.validate_argument('type', lambda t: relations.VOTE_TYPE.index_value[int(t)], 'bills.vote', 'Неверно указан тип голоса')
    @old_views.handler('#bill', 'vote', name='vote', method='post')
    def vote(self, type):  # pylint: disable=W0622

        if not self.bill.can_vote(self.hero):
            return self.json_error('bills.vote.can_not_vote', 'Вы не можете голосовать за эту запись')

        if prototypes.VotePrototype.get_for(self.account, self.bill):
            return self.json_error('bills.vote.vote_exists', 'Вы уже проголосовали')

        with django_transaction.atomic():
            prototypes.VotePrototype.create(self.account, self.bill, type)
            self.bill.recalculate_votes()
            self.bill.save()

        return self.json_ok()
