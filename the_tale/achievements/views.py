# coding: utf-8

import md5

from dext.views import handler, validate_argument, validator
from dext.settings import settings
from dext.utils.urls import url

from common.utils.resources import Resource
from common.utils.decorators import login_required, superuser_required

from accounts.views import validate_fast_account

from bank.dengionline.transaction import Transaction as DOTransaction
from bank.dengionline.relations import CURRENCY_TYPE as DO_CURRENCY_TYPE

from bank.relations import ENTITY_TYPE, CURRENCY_TYPE
from bank.dengionline import exceptions

from accounts.prototypes import AccountPrototype


from achievements.prototypes import SectionPrototype, KitPrototype, RewardPrototype
from achievements.forms import EditSectionForm, EditKitForm


class BaseAchievementsResource(Resource):

    def initialize(self, *args, **kwargs):
        super(BaseAchievementsResource, self).initialize(*args, **kwargs)


class SectionsResource(BaseAchievementsResource):

    @validate_argument('section', SectionPrototype.get_by_id, 'achievements.sections', u'Раздел не найден')
    def initialize(self, section=None, **kwargs):
        super(SectionsResource, self).initialize(**kwargs)
        self.section = section

        self.can_edit_section = self.account.has_perm('mobs.edit_section')
        self.can_moderate_section = self.account.has_perm('mobs.moderate_section')

    @validator(code='achievements.sections.no_edit_rights', message=u'нет прав для редактирования раздела', status_code=404)
    def validate_can_edit_section(self, *args, **kwargs):
        return self.can_edit_section or self.can_moderate_section

    @validator(code='achievements.sections.no_moderate_rights', message=u'нет прав для модерации раздела', status_code=404)
    def validate_can_moderate_section(self, *args, **kwargs):
        return self.can_moderate_section


    @handler('')
    def index(self):
        sections = SectionPrototype.approved_sections()

        return self.template('sections/index.html',
                             {'sections': sections})

    @login_required
    @validate_can_edit_section()
    @handler('new')
    def new(self):
        return self.template('sections/new.html',
                             {'form': EditSectionForm()})


    @login_required
    @validate_can_edit_section()
    @handler('create', method='POST')
    def create(self):
        form = EditSectionForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.sections.create.form_errors', form.errors)

        section = SectionPrototype.create(caption=form.c.caption,
                                          description=form.c.description)

        return self.json_ok(data={'next_url': url('achievements:sections:show', section.id)})


    @handler('#section')
    def show(self):
        return self.template('sections/show.html',
                             {'section': self.section})

    @login_required
    @validate_can_edit_section()
    @handler('#section', 'edit')
    def edit(self):
        form = EditSectionForm(initials={'caption': self.section.caption,
                                         'description': self.section.description})

        return self.template('sections/show.html',
                             {'section': self.section,
                              'form': form})


    @login_required
    @validate_can_edit_section()
    @handler('#section', 'update')
    def update(self, method='POST'):
        form = EditSectionForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.sections.create.form_errors', form.errors)

        self.section.caption = form.c.caption
        self.section.description = form.c.description
        self.section.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_section()
    @handler('#section', 'approve')
    def approve(self, method='POST'):
        self.section.approved = True
        self.section.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_section()
    @handler('#section', 'disapprove')
    def disapprove(self, method='POST'):
        self.section.approved = False
        self.section.save()

        return self.json_ok()


class KitsResource(BaseAchievementsResource):

    @validate_argument('kit', KitPrototype.get_by_id, 'achievements.kits', u'Набор не найден')
    def initialize(self, kit=None, **kwargs):
        super(KitsResource, self).initialize(**kwargs)
        self.kit = kit

        self.can_edit_kit = self.account.has_perm('mobs.edit_kit')
        self.can_moderate_kit = self.account.has_perm('mobs.moderate_kit')

    @validator(code='achievements.kits.no_edit_rights', message=u'нет прав для редактирования набора', status_code=404)
    def validate_can_edit_kit(self, *args, **kwargs):
        return self.can_edit_kit or self.can_moderate_kit

    @validator(code='achievements.kits.no_moderate_rights', message=u'нет прав для модерации набора', status_code=404)
    def validate_can_moderate_kit(self, *args, **kwargs):
        return self.can_moderate_kit


    @handler('')
    def index(self):
        kits = KitPrototype.approved_kits()

        return self.template('kits/index.html',
                             {'kits': kits})

    @login_required
    @validate_can_edit_kit()
    @handler('new')
    def new(self):
        return self.template('kits/new.html',
                             {'form': EditKitForm()})

    @login_required
    @validate_can_edit_kit()
    @handler('create', method='POST')
    def create(self):
        form = EditKitForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.kits.create.form_errors', form.errors)

        kit = KitPrototype.create(section=form.c.section,
                                  caption=form.c.caption,
                                  description=form.c.description)

        return self.json_ok(data={'next_url': url('achievements:kits:show', kit.id)})


    @handler('#kit')
    def show(self):
        return self.template('kits/show.html',
                             {'kit': self.kit})

    @login_required
    @validate_can_edit_kit()
    @handler('#kit', 'edit')
    def edit(self):
        form = EditKitForm(initials={'section': self.kit.section_id,
                                     'caption': self.kit.caption,
                                     'description': self.kit.description})

        return self.template('kits/show.html',
                             {'kit': self.kit,
                              'form': form})

    @login_required
    @validate_can_edit_kit()
    @handler('#kit', 'update')
    def update(self, method='POST'):
        form = EditKitForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.kits.create.form_errors', form.errors)

        self.kit.section = form.c.section
        self.kit.caption = form.c.caption
        self.kit.description = form.c.description
        self.kit.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_kit()
    @handler('#kit', 'approve')
    def approve(self, method='POST'):
        self.kit.approved = True
        self.kit.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_kit()
    @handler('#kit', 'disapprove')
    def disapprove(self, method='POST'):
        self.kit.approved = False
        self.kit.save()

        return self.json_ok()


class RewardsResource(BaseAchievementsResource):

    @validate_argument('achievement', RewardPrototype.get_by_id, 'achievements', u'Набор не найден')
    def initialize(self, achievement=None, **kwargs):
        super(RewardsResource, self).initialize(**kwargs)
        self.achievement = achievement

    @handler('')
    def index(self):
        pass

    @handler('new')
    def new(self):
        pass

    @handler('create', method='POST')
    def create(self):
        pass

    @handler('#achievement')
    def show(self):
        pass

    @handler('#achievement', 'edit')
    def edit(self):
        pass

    @handler('#achievement', 'update')
    def update(self, method='POST'):
        pass




class AccountsResource(BaseAchievementsResource):
    pass
