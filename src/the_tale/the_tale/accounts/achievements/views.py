
import smart_imports

smart_imports.all()


def argument_to_group(value): return relations.ACHIEVEMENT_GROUP.index_slug.get(value)


def argument_to_achievement(value): return storage.achievements[int(value)]


@dext_old_views.validator(code='accounts.achievements.no_edit_rights', message='нет прав для редактирования достижений')
def validate_can_edit_achievements(resource, *args, **kwargs):
    return resource.can_edit_achievements


class AchievementsResource(utils_resources.Resource):

    @dext_old_views.validate_argument('group', argument_to_group, 'accounts.achievements', 'Группа не найдена')
    @dext_old_views.validate_argument('achievement', argument_to_achievement, 'accounts.achievements', 'Достижение не найдено')
    def initialize(self, group=None, achievement=None, *args, **kwargs):
        super(AchievementsResource, self).initialize(*args, **kwargs)
        self.achievement = achievement
        self.group = group
        self.master_account = None

    @property
    def can_edit_achievements(self): return self.account.has_perm('achievements.edit_achievement')

    @utils_decorators.lazy_property
    def groups(self):
        return sorted(relations.ACHIEVEMENT_GROUP.records, key=lambda group: group.text)

    def group_url(self, group):
        if self.master_account:
            return dext_urls.url('accounts:achievements:group', group.slug, account=self.master_account.id)
        else:
            return dext_urls.url('accounts:achievements:group', group.slug)

    def index_url(self):
        if self.master_account:
            return dext_urls.url('accounts:achievements:', account=self.master_account.id)
        else:
            return dext_urls.url('accounts:achievements:')

    @dext_old_views.validate_argument('account', accounts_prototypes.AccountPrototype.get_by_id, 'accounts.achievements', 'Игрок не найден')
    @dext_old_views.handler('')
    def index(self, account=None):

        if account is None and self.account.is_authenticated:
            return self.redirect(dext_urls.url('accounts:achievements:', account=self.account.id))

        self.master_account = account

        account_achievements = None
        last_achievements = []
        if account:
            account_achievements = prototypes.AccountAchievementsPrototype.get_by_account_id(account.id)
            last_achievements = account_achievements.last_achievements(number=conf.settings.LAST_ACHIEVEMENTS_NUMBER)

        groups_table = utils_logic.split_into_table(self.groups, 3)

        return self.template('achievements/index.html',
                             {'account_achievements': account_achievements,
                              'groups_table': groups_table,
                              'groups_statistics': storage.achievements.get_groups_statistics(account_achievements),
                              'last_achievements': last_achievements})

    @dext_old_views.validate_argument('account', accounts_prototypes.AccountPrototype.get_by_id, 'accounts.achievements', 'Игрок не найден')
    @dext_old_views.handler('#group', name='group')
    def show_group(self, account=None):
        if account is None and self.account.is_authenticated:
            return self.redirect(dext_urls.url('accounts:achievements:group', self.group.slug, account=self.account.id))

        self.master_account = account

        account_achievements = None
        if account:
            account_achievements = prototypes.AccountAchievementsPrototype.get_by_account_id(account.id)
            achievements = sorted(storage.achievements.by_group(self.group, only_approved=not self.can_edit_achievements),
                                  key=account_achievements.sort_key_for)
        else:
            achievements = sorted(storage.achievements.by_group(self.group, only_approved=not self.can_edit_achievements),
                                  key=lambda achievement: achievement.order)

        return self.template('achievements/group.html',
                             {'account_achievements': account_achievements,
                              'groups_statistics': storage.achievements.get_groups_statistics(account_achievements),
                              'achievements': achievements})

    @utils_decorators.login_required
    @validate_can_edit_achievements()
    @dext_old_views.handler('new')
    def new(self):
        return self.template('achievements/new.html',
                             {'form': forms.NewAchievementForm()})

    @utils_decorators.login_required
    @validate_can_edit_achievements()
    @dext_old_views.handler('create', method='post')
    def create(self):
        form = forms.NewAchievementForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('accounts.achievements.create.form_errors', form.errors)

        achievement = prototypes.AchievementPrototype.create(group=form.c.group,
                                                             type=form.c.type,
                                                             caption=form.c.caption,
                                                             description=form.c.description,
                                                             approved=False,
                                                             barrier=form.c.barrier,
                                                             points=form.c.points,
                                                             item_1=form.c.item_1,
                                                             item_2=form.c.item_2,
                                                             item_3=form.c.item_3)

        return self.json_ok(data={'next_url': dext_urls.url('accounts:achievements:group', achievement.group.slug)})

    @utils_decorators.login_required
    @validate_can_edit_achievements()
    @dext_old_views.handler('#achievement', 'edit')
    def edit(self):
        form = forms.EditAchievementForm(initial={'approved': self.achievement.approved,
                                                  'group': self.achievement.group,
                                                  'type': self.achievement.type,
                                                  'caption': self.achievement.caption,
                                                  'barrier': self.achievement.barrier,
                                                  'description': self.achievement.description,
                                                  'order': self.achievement.order,
                                                  'points': self.achievement.points,
                                                  'item_1': self.achievement.item_1.id if self.achievement.item_1 is not None else None,
                                                  'item_2': self.achievement.item_2.id if self.achievement.item_2 is not None else None,
                                                  'item_3': self.achievement.item_3.id if self.achievement.item_3 is not None else None})
        return self.template('achievements/edit.html',
                             {'form': form})

    @utils_decorators.login_required
    @validate_can_edit_achievements()
    @dext_old_views.handler('#achievement', 'update', method='post')
    def update(self):
        form = forms.EditAchievementForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('accounts.achievements.update.form_errors', form.errors)

        with django_transaction.atomic():

            is_changed = (self.achievement.type != form.c.type or
                          self.achievement.approved != form.c.approved or
                          self.achievement.barrier != form.c.barrier or
                          self.achievement.points != form.c.points or
                          self.achievement.item_1 != form.c.item_1 or
                          self.achievement.item_2 != form.c.item_2 or
                          self.achievement.item_3 != form.c.item_3)

            self.achievement.group = form.c.group
            self.achievement.type = form.c.type
            self.achievement.caption = form.c.caption
            self.achievement.description = form.c.description
            self.achievement.approved = form.c.approved
            self.achievement.barrier = form.c.barrier
            self.achievement.points = form.c.points
            self.achievement.order = form.c.order

            self.achievement.item_1_id = form.c.item_1.id if form.c.item_1 is not None else None
            self.achievement.item_2_id = form.c.item_2.id if form.c.item_2 is not None else None
            self.achievement.item_3_id = form.c.item_3.id if form.c.item_3 is not None else None

            self.achievement.save()

            if is_changed:
                prototypes.GiveAchievementTaskPrototype.create(account_id=None, achievement_id=self.achievement.id)

        return self.json_ok(data={'next_url': dext_urls.url('accounts:achievements:group', self.achievement.group.slug)})
