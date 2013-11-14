# coding: utf-8

from dext.views import handler, validate_argument, validator
from dext.utils.urls import url

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required


from the_tale.accounts.prototypes import AccountPrototype

from the_tale.accounts.achievements.prototypes import AchievementPrototype, AccountAchievementsPrototype
from the_tale.accounts.achievements.relations import ACHIEVEMENT_GROUP
from the_tale.accounts.achievements.storage import achievements_storage
from the_tale.accounts.achievements.forms import EditAchievementForm


def argument_to_group(value): return ACHIEVEMENT_GROUP(int(value))
def argument_to_achievement(value): return achievements_storage[int(value)]


class AchievementsResource(Resource):

    @validate_argument('group', argument_to_group, 'accounts.achievements', u'Группа не найдена')
    @validate_argument('achievement', argument_to_achievement, 'accounts.achievements', u'Достижение не найдено')
    def initialize(self, group=None, achievement=None, *args, **kwargs):
        super(AchievementsResource, self).initialize(*args, **kwargs)
        self.achievement = achievement
        self.group = group

    @property
    def can_edit_achievements(self): return self.account.has_perm('achievements.edit_achievement')

    @validator(code='accounts.achievements.no_edit_rights', message=u'нет прав для редактирования достижений')
    def validate_can_edit_achievements(self, *args, **kwargs):
        return self.can_edit_achievements


    @validate_argument('account', AccountPrototype.get_by_id, 'accounts.achievements', u'Игрок не найден')
    @handler('#group', name='group')
    def show_group(self, account=None):
        if account is None and self.account.is_authenticated():
            account = self.account

        account_achievements = None
        if account:
            account_achievements = AccountAchievementsPrototype.get_by_account_id(account.id)

        return self.template('achievements/group.html',
                             {'master_account': account,
                              'account_achievements': account_achievements,
                              'achievements': sorted(achievements_storage.by_group(self.group, only_approved=not self.can_edit_achievements),
                                                     key=lambda achievement: achievement.order),
                              'groups': sorted(ACHIEVEMENT_GROUP._records, key=lambda group: group.name)})


    @login_required
    @validate_can_edit_achievements()
    @handler('new')
    def new(self):
        return self.template('achievements/new.html',
                             {'form': EditAchievementForm()})


    @login_required
    @validate_can_edit_achievements()
    @handler('create', method='post')
    def create(self):
        form = EditAchievementForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('accounts.achievements.create.form_errors', form.errors)


        achievement = AchievementPrototype.create(group=form.c.group,
                                                  type=form.c.type,
                                                  caption=form.c.caption,
                                                  description=form.c.description,
                                                  approved=form.c.approved,
                                                  barrier=form.c.barrier)

        return self.json_ok(data={'next_url': url('accounts:achievements:group', achievement.group.value)})


    @login_required
    @validate_can_edit_achievements()
    @handler('#achievement', 'edit')
    def edit(self):
        form = EditAchievementForm(initial={ 'approved': self.achievement.approved,
                                             'group': self.achievement.group,
                                             'type': self.achievement.type,
                                             'caption': self.achievement.caption,
                                             'barrier': self.achievement.barrier,
                                             'description': self.achievement.description})
        return self.template('achievements/new.html',
                             {'form': form})


    @login_required
    @validate_can_edit_achievements()
    @handler('#achievement', 'update', method='post')
    def update(self):
        form = EditAchievementForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('accounts.achievements.update.form_errors', form.errors)


        self.achievement.group = form.c.group
        self.achievement.type = form.c.type
        self.achievement.caption = form.c.caption
        self.achievement.description = form.c.description
        self.achievement.approved = form.c.approved
        self.achievement.barrier = form.c.barrier

        self.achievement.save()

        return self.json_ok(data={'next_url': url('accounts:achievements:group', self.achievement.group.value)})
