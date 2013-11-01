# coding: utf-8

from dext.views import handler, validate_argument, validator
from dext.utils.urls import url

from common.utils.resources import Resource
from common.utils.decorators import login_required

from achievements.prototypes import SectionPrototype, KitPrototype, RewardPrototype
from achievements.forms import EditSectionForm, EditKitForm, EditRewardForm


class BaseAchievementsResource(Resource):

    @validate_argument('section', SectionPrototype.get_by_id, 'achievements', u'Раздел не найден')
    @validate_argument('kit', KitPrototype.get_by_id, 'achievements', u'Набор не найден')
    @validate_argument('reward', RewardPrototype.get_by_id, 'achievements', u'Награла не найдена')
    def initialize(self, section=None, kit=None, reward=None, **kwargs):
        super(BaseAchievementsResource, self).initialize(**kwargs)
        self.reward = reward
        self.kit = kit
        self.section = section

        if self.reward:
            self.kit = self.reward.kit

        if self.kit:
            self.section = self.kit.section

    @property
    def edit_section_permission(self): return self.account.has_perm('achievements.edit_section')

    @property
    def moderate_section_permission(self): return self.account.has_perm('achievements.moderate_section')

    @property
    def edit_kit_permission(self): return self.account.has_perm('achievements.edit_kit')

    @property
    def moderate_kit_permission(self): return self.account.has_perm('achievements.moderate_kit')

    @property
    def edit_reward_permission(self): return self.account.has_perm('achievements.edit_reward')

    @property
    def moderate_reward_permission(self): return self.account.has_perm('achievements.moderate_reward')

    @property
    def can_see_all_sections(self): return self.edit_section_permission or self.moderate_section_permission

    @property
    def can_edit_section(self):
        if self.section and self.section.approved:
            return self.can_moderate_section
        return self.edit_section_permission or self.moderate_section_permission

    @property
    def can_moderate_section(self): return self.moderate_section_permission

    @property
    def can_edit_kit(self):
        if self.kit and self.kit.approved:
            return self.can_moderate_kit
        return self.edit_kit_permission or self.moderate_kit_permission

    @property
    def can_moderate_kit(self): return self.moderate_kit_permission

    @property
    def can_edit_reward(self):
        if self.reward and self.reward.approved:
            return self.can_moderate_reward
        return self.edit_reward_permission or self.moderate_reward_permission

    @property
    def can_moderate_reward(self): return self.moderate_reward_permission

    @property
    def sections(self):
        if self.moderate_section_permission or self.edit_section_permission:
            return SectionPrototype.all_sections()
        else:
            return SectionPrototype.approved_sections()

    @property
    def kits(self):
        if self.moderate_kit_permission or self.edit_kit_permission:
            return KitPrototype.all_kits()
        else:
            return KitPrototype.approved_kits()


class SectionsResource(BaseAchievementsResource):


    @validator(code='achievements.sections.no_edit_rights', message=u'нет прав для редактирования раздела')
    def validate_can_edit_section(self, *args, **kwargs):
        return self.can_edit_section

    @validator(code='achievements.sections.no_moderate_rights', message=u'нет прав для модерации раздела')
    def validate_can_moderate_section(self, *args, **kwargs):
        return self.can_moderate_section

    @validator(code='achievements.sections.not_approved', message=u'раздел не найден', status_code=404)
    def validate_section_approved(self, *args, **kwargs):
        return self.section and (self.can_edit_section or self.section.approved)

    @login_required
    @validate_can_edit_section()
    @handler('')
    def index(self):
        return self.template('achievements/sections/index.html',
                             {})

    @login_required
    @validate_can_edit_section()
    @handler('new')
    def new(self):
        return self.template('achievements/sections/new.html',
                             {'form': EditSectionForm()})


    @login_required
    @validate_can_edit_section()
    @handler('create', method='post')
    def create(self):
        form = EditSectionForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.sections.create.form_errors', form.errors)

        section = SectionPrototype.create(caption=form.c.caption,
                                          description=form.c.description)

        return self.json_ok(data={'next_url': url('achievements:sections:show', section.id)})


    @validate_section_approved()
    @handler('#section', name='show')
    def show(self):
        return self.template('achievements/sections/show.html',
                             {'kits': KitPrototype.get_list_by_section_id(self.section.id)})

    @login_required
    @validate_can_edit_section()
    @handler('#section', 'edit')
    def edit(self):
        form = EditSectionForm(initial={'caption': self.section.caption,
                                        'description': self.section.description})

        return self.template('achievements/sections/edit.html',
                             {'form': form})


    @login_required
    @validate_can_edit_section()
    @handler('#section', 'update')
    def update(self, method='post'):
        form = EditSectionForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.sections.update.form_errors', form.errors)

        self.section.caption = form.c.caption
        self.section.description = form.c.description
        self.section.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_section()
    @handler('#section', 'approve')
    def approve(self, method='post'):
        self.section.approved = True
        self.section.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_section()
    @handler('#section', 'disapprove')
    def disapprove(self, method='post'):
        self.section.approved = False
        self.section.save()

        return self.json_ok()


class KitsResource(BaseAchievementsResource):

    @validator(code='achievements.kits.no_edit_rights', message=u'нет прав для редактирования набора')
    def validate_can_edit_kit(self, *args, **kwargs):
        return self.can_edit_kit or self.can_moderate_kit

    @validator(code='achievements.kits.no_moderate_rights', message=u'нет прав для модерации набора')
    def validate_can_moderate_kit(self, *args, **kwargs):
        return self.can_moderate_kit

    @validator(code='achievements.kits.not_approved', message=u'набор не найден', status_code=404)
    def validate_kit_approved(self, *args, **kwargs):
        return self.kit and (self.can_edit_kit or self.kit.approved)

    @login_required
    @validate_can_edit_kit()
    @handler('')
    def index(self):
        return self.template('achievements/kits/index.html',
                             {})

    @login_required
    @validate_can_edit_kit()
    @handler('new')
    def new(self):
        return self.template('achievements/kits/new.html',
                             {'form': EditKitForm()})

    @login_required
    @validate_can_edit_kit()
    @handler('create', method='post')
    def create(self):
        form = EditKitForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.kits.create.form_errors', form.errors)

        kit = KitPrototype.create(section=form.c.section,
                                  caption=form.c.caption,
                                  description=form.c.description)

        return self.json_ok(data={'next_url': url('achievements:kits:show', kit.id)})


    @handler('#kit', name='show')
    def show(self):
        return self.template('achievements/kits/show.html',
                             {'rewards': RewardPrototype.get_list_by_kit_id(self.kit.id)})

    @login_required
    @validate_can_edit_kit()
    @handler('#kit', 'edit')
    def edit(self):
        form = EditKitForm(initial={'section': self.kit.section_id,
                                    'caption': self.kit.caption,
                                    'description': self.kit.description})

        return self.template('achievements/kits/edit.html',
                             {'form': form})

    @login_required
    @validate_can_edit_kit()
    @handler('#kit', 'update')
    def update(self, method='post'):
        form = EditKitForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.kits.update.form_errors', form.errors)

        self.kit.section_id = form.c.section.id
        self.kit.caption = form.c.caption
        self.kit.description = form.c.description
        self.kit.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_kit()
    @handler('#kit', 'approve')
    def approve(self, method='post'):
        self.kit.approved = True
        self.kit.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_kit()
    @handler('#kit', 'disapprove')
    def disapprove(self, method='post'):
        self.kit.approved = False
        self.kit.save()

        return self.json_ok()


class RewardsResource(BaseAchievementsResource):

    @validator(code='achievements.rewards.no_edit_rights', message=u'нет прав для редактирования награды')
    def validate_can_edit_reward(self, *args, **kwargs):
        return self.can_edit_reward or self.can_moderate_reward

    @validator(code='achievements.rewards.no_moderate_rights', message=u'нет прав для модерации награды')
    def validate_can_moderate_reward(self, *args, **kwargs):
        return self.can_moderate_reward

    @login_required
    @validate_can_edit_reward()
    @handler('new')
    def new(self):
        return self.template('achievements/rewards/new.html',
                             {'form': EditRewardForm()})

    @login_required
    @validate_can_edit_reward()
    @handler('create', method='post')
    def create(self):
        form = EditRewardForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.rewards.create.form_errors', form.errors)

        reward = RewardPrototype.create(kit=form.c.kit,
                                        caption=form.c.caption,
                                        text=form.c.text)

        return self.json_ok(data={'next_url': url('achievements:kits:show', reward.kit_id)})

    @login_required
    @validate_can_edit_reward()
    @handler('#reward', 'edit')
    def edit(self):
        form = EditRewardForm(initial={ 'kit': self.reward.kit_id,
                                        'caption': self.reward.caption,
                                        'text': self.reward.text})

        return self.template('achievements/rewards/edit.html',
                             {'form': form})

    @login_required
    @validate_can_edit_reward()
    @handler('#reward', 'update')
    def update(self, method='post'):
        form = EditRewardForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.rewards.update.form_errors', form.errors)

        self.reward.kit_id = form.c.kit.id
        self.reward.caption = form.c.caption
        self.reward.text = form.c.text
        self.reward.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_reward()
    @handler('#reward', 'approve')
    def approve(self, method='post'):
        self.reward.approved = True
        self.reward.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_reward()
    @handler('#reward', 'disapprove')
    def disapprove(self, method='post'):
        self.reward.approved = False
        self.reward.save()

        return self.json_ok()


class AccountsResource(BaseAchievementsResource):
    pass
