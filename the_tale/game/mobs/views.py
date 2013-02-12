# coding: utf-8
import uuid

from django.core.urlresolvers import reverse

from dext.views import handler, validator, validate_argument
from dext.utils.decorators import nested_commit_on_success
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource

from common.utils.decorators import login_required

from game.map.places.models import TERRAIN

from game.mobs.models import MOB_RECORD_STATE
from game.mobs.prototypes import MobRecordPrototype
from game.mobs.storage import mobs_storage
from game.mobs.forms import MobRecordForm, ModerateMobRecordForm


class MobResource(Resource):

    @validate_argument('mob', MobRecordPrototype.get_by_id, 'mobs', u'Запись о монстре не найдена')
    def initialize(self, mob=None, *args, **kwargs):
        super(MobResource, self).initialize(*args, **kwargs)
        self.mob = mob

        self.can_create_mob = self.user.has_perm('mobs.create_mobrecord')
        self.can_moderate_mob = self.user.has_perm('mobs.moderate_mobrecord')

    @validator(code='mobs.create_mob_rights_required', message=u'Вы не можете создавать мобов')
    def validate_create_rights(self, *args, **kwargs): return self.can_create_mob

    @validator(code='mobs.moderate_mob_rights_required', message=u'Вы не можете принимать мобов в игру')
    def validate_moderate_rights(self, *args, **kwargs): return self.can_moderate_mob

    @validator(code='mobs.disabled_state_required', message=u'Для проведения этой операции монстр должен быть убран из игры')
    def validate_disabled_state(self, *args, **kwargs): return self.mob.state.is_disabled

    @validate_argument('state', MOB_RECORD_STATE, 'mobs', u'неверное состояние записи о монстре')
    @validate_argument('terrain', TERRAIN, 'mobs', u'неверный тип территории')
    @handler('', method='get')
    def index(self, state=MOB_RECORD_STATE(MOB_RECORD_STATE.ENABLED), terrain=None):

        mobs = mobs_storage.all()

        if not self.can_create_mob and not self.can_moderate_mob:
            mobs = filter(lambda mob: mob.state.is_enabled, mobs)

        is_filtering = False

        print state.value

        if state is not None:
            if not state.is_enabled: # if not default
                is_filtering = True
            mobs = filter(lambda mob: mob.state == state, mobs)

        if terrain is not None:
            is_filtering = True
            mobs = filter(lambda mob: terrain.value in mob.terrains, mobs)


        url_builder = UrlBuilder(reverse('game:mobs:'), arguments={ 'state': state.value if state else None,
                                                                    'terrain': terrain.value if terrain else None})

        return self.template('mobs/index.html',
                             {'mobs': mobs,
                              'is_filtering': is_filtering,
                              'MOB_RECORD_STATE': MOB_RECORD_STATE,
                              'TERRAIN': TERRAIN,
                              'state': state,
                              'terrain': terrain,
                              'url_builder': url_builder} )

    @login_required
    @validate_create_rights()
    @handler('new', method='get')
    def new(self):
        return self.template('mobs/new.html', {'form': MobRecordForm()})

    @login_required
    @validate_create_rights()
    @nested_commit_on_success
    @handler('create', method='post')
    def create(self):

        form = MobRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('mobs.create.form_errors', form.errors)

        mob = MobRecordPrototype.create(uuid=uuid.uuid4().hex,
                                        level=form.c.level,
                                        name=form.c.name,
                                        description=form.c.description,
                                        abilities=form.c.abilities,
                                        terrains=form.c.terrains,
                                        editor=self.account,
                                        state=MOB_RECORD_STATE.DISABLED)
        return self.json_ok(data={'next_url': reverse('game:mobs:show', args=[mob.id])})




    @handler('#mob', name='show', method='get')
    def show(self):

        if self.mob.state.is_disabled and not (self.can_create_mob or self.can_moderate_mob):
            return self.auto_error('mobs.show.mob_disabled', u'монстр находится вне игры', status_code=404)

        return self.template('mobs/show.html', {'mob': self.mob})

    @login_required
    @validate_disabled_state()
    @validate_create_rights()
    @handler('#mob', 'edit', name='edit', method='get')
    def edit(self):
        form = MobRecordForm(initial={'name': self.mob.name,
                                      'description': self.mob.description,
                                      'level': self.mob.level,
                                      'terrains': self.mob.terrains,
                                      'abilities': self.mob.abilities})

        return self.template('mobs/edit.html', {'mob': self.mob,
                                                'form': form} )

    @login_required
    @validate_disabled_state()
    @validate_create_rights()
    @nested_commit_on_success
    @handler('#mob', 'update', name='update', method='post')
    def update(self):

        form = MobRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('mobs.update.form_errors', form.errors)

        self.mob.update_by_creator(form)

        return self.json_ok()

    # @validate_moderator_rights()
    # @handler('#bill', 'delete', name='delete', method='post')
    # def delete(self):
    #     self.bill.remove(self.account)
    #     return self.json_ok()

    @login_required
    @validate_moderate_rights()
    @handler('#mob', 'moderate', name='moderate', method='get')
    def moderation_page(self):
        form = ModerateMobRecordForm(initial={'description': self.mob.description,
                                              'level': self.mob.level,
                                              'terrains': self.mob.terrains,
                                              'abilities': self.mob.abilities,
                                              'uuid': self.mob.uuid,
                                              'name_forms': self.mob.name_forms.serialize(),
                                              'approved': self.mob.state.is_enabled})

        return self.template('mobs/moderate.html', {'mob': self.mob,
                                                    'form': form} )

    @login_required
    @validate_moderate_rights()
    @nested_commit_on_success
    @handler('#mob', 'moderate', name='moderate', method='post')
    def moderate(self):
        form = ModerateMobRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('mobs.moderate.form_errors', form.errors)

        self.mob.update_by_moderator(form)

        return self.json_ok()
