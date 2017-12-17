# coding: utf-8
import uuid

from django.core.urlresolvers import reverse

from dext.views import handler, validator, validate_argument
from dext.common.utils.urls import UrlBuilder

from the_tale.common.utils import list_filter
from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required

from tt_logic.map.relations import TERRAIN

from the_tale.game import relations as game_relations

from .relations import MOB_RECORD_STATE, INDEX_ORDER_TYPE
from .prototypes import MobRecordPrototype
from .storage import mobs_storage
from .forms import MobRecordForm, ModerateMobRecordForm
from . import meta_relations


BASE_INDEX_FILTERS = [list_filter.reset_element(),
                      list_filter.choice_element('тип:', attribute='type', choices=[(None, 'все')] + sorted(list(game_relations.BEING_TYPE.select('value', 'text')), key=lambda x: x[1])),
                      list_filter.choice_element('архетип:', attribute='archetype', choices=[(None, 'все')] + sorted(list(game_relations.ARCHETYPE.select('value', 'text')), key=lambda x: x[1])),
                      list_filter.choice_element('территория:', attribute='terrain', choices=[(None, 'все')] + sorted(list(TERRAIN.select('value', 'text')), key=lambda x: x[1])),
                      list_filter.choice_element('сортировка:',
                                                 attribute='order_by',
                                                 choices=INDEX_ORDER_TYPE.select('value', 'text'),
                                                 default_value=INDEX_ORDER_TYPE.BY_NAME.value) ]

MODERATOR_INDEX_FILTERS = BASE_INDEX_FILTERS + [list_filter.choice_element('состояние:',
                                                                           attribute='state',
                                                                           default_value=MOB_RECORD_STATE.ENABLED.value,
                                                                           choices=MOB_RECORD_STATE.select('value', 'text'))]


class UnloginedIndexFilter(list_filter.ListFilter):
    ELEMENTS = BASE_INDEX_FILTERS

class ModeratorIndexFilter(list_filter.ListFilter):
    ELEMENTS = MODERATOR_INDEX_FILTERS



def argument_to_mob(value): return mobs_storage.get(int(value), None)

class MobResourceBase(Resource):

    @validate_argument('mob', argument_to_mob, 'mobs', 'Запись о монстре не найдена')
    def initialize(self, mob=None, *args, **kwargs):
        super(MobResourceBase, self).initialize(*args, **kwargs)
        self.mob = mob

        self.can_create_mob = self.account.has_perm('mobs.create_mobrecord')
        self.can_moderate_mob = self.account.has_perm('mobs.moderate_mobrecord')


def argument_to_mob_state(value): return MOB_RECORD_STATE(int(value))

def argument_to_mob_type(value): return game_relations.BEING_TYPE(int(value))

def argument_to_archetype(value): return game_relations.ARCHETYPE(int(value))


class GuideMobResource(MobResourceBase):

    @validator(code='mobs.mob_disabled', message='монстр находится вне игры', status_code=404)
    def validate_mob_disabled(self, *args, **kwargs):
        return not self.mob.state.is_DISABLED or self.can_create_mob or self.can_moderate_mob

    @validate_argument('state', argument_to_mob_state, 'mobs', 'неверное состояние записи о монстре')
    @validate_argument('terrain', lambda value: TERRAIN(int(value)), 'mobs', 'неверный тип территории')
    @validate_argument('order_by', INDEX_ORDER_TYPE, 'mobs', 'неверный тип сортировки')
    @validate_argument('archetype', argument_to_archetype, 'mobs', 'неверный архетип монстра')
    @validate_argument('type', argument_to_mob_type, 'mobs', 'неверный тип монстра')
    @handler('', method='get')
    def index(self, state=MOB_RECORD_STATE.ENABLED, terrain=None, order_by=INDEX_ORDER_TYPE.BY_NAME, type=None, archetype=None):

        mobs = mobs_storage.all()

        if not self.can_create_mob and not self.can_moderate_mob:
            mobs = [mob for mob in mobs if mob.state.is_ENABLED] # pylint: disable=W0110

        is_filtering = False

        if not state.is_ENABLED: # if not default
            is_filtering = True
        mobs = [mob for mob in mobs if mob.state == state] # pylint: disable=W0110

        if terrain is not None:
            is_filtering = True
            mobs = [mob for mob in mobs if terrain in mob.terrains] # pylint: disable=W0110

        if order_by.is_BY_NAME:
            mobs = sorted(mobs, key=lambda mob: mob.name)
        elif order_by.is_BY_LEVEL:
            mobs = sorted(mobs, key=lambda mob: mob.level)

        if type is not None:
            mobs = [mob for mob in mobs if mob.type == type] # pylint: disable=W0110

        if archetype is not None:
            mobs = [mob for mob in mobs if mob.archetype == archetype] # pylint: disable=W0110

        url_builder = UrlBuilder(reverse('guide:mobs:'), arguments={ 'state': state.value if state is not None else None,
                                                                     'terrain': terrain.value if terrain is not None else None,
                                                                     'type': type.value if type is not None else None,
                                                                     'archetype': archetype.value if archetype is not None else None,
                                                                     'order_by': order_by.value})

        IndexFilter = ModeratorIndexFilter if self.can_create_mob or self.can_moderate_mob else UnloginedIndexFilter #pylint: disable=C0103

        index_filter = IndexFilter(url_builder=url_builder, values={'state': state.value if state is not None else None,
                                                                    'terrain': terrain.value if terrain is not None else None,
                                                                    'type': type.value if type is not None else None,
                                                                    'archetype': archetype.value if archetype is not None else None,
                                                                    'order_by': order_by.value})


        return self.template('mobs/index.html',
                             {'mobs': mobs,
                              'is_filtering': is_filtering,
                              'MOB_RECORD_STATE': MOB_RECORD_STATE,
                              'TERRAIN': TERRAIN,
                              'state': state,
                              'terrain': terrain,
                              'order_by': order_by,
                              'INDEX_ORDER_TYPE': INDEX_ORDER_TYPE,
                              'url_builder': url_builder,
                              'index_filter': index_filter,
                              'section': 'mobs'} )

    @validate_mob_disabled()
    @handler('#mob', name='show', method='get')
    def show(self):
        return self.template('mobs/show.html', {'mob': self.mob,
                                                'mob_meta_object': meta_relations.Mob.create_from_object(self.mob),
                                                'section': 'mobs'})

    @validate_mob_disabled()
    @handler('#mob', 'info', method='get')
    def show_dialog(self):
        return self.template('mobs/info.html', {'mob': self.mob,
                                                'mob_meta_object': meta_relations.Mob.create_from_object(self.mob),})


class GameMobResource(MobResourceBase):

    @validator(code='mobs.create_mob_rights_required', message='Вы не можете создавать мобов')
    def validate_create_rights(self, *args, **kwargs): return self.can_create_mob

    @validator(code='mobs.moderate_mob_rights_required', message='Вы не можете принимать мобов в игру')
    def validate_moderate_rights(self, *args, **kwargs): return self.can_moderate_mob

    @validator(code='mobs.disabled_state_required', message='Для проведения этой операции монстр должен быть убран из игры')
    def validate_disabled_state(self, *args, **kwargs): return self.mob.state.is_DISABLED

    @login_required
    @validate_create_rights()
    @handler('new', method='get')
    def new(self):
        form = MobRecordForm()
        return self.template('mobs/new.html', {'form': form})

    @login_required
    @validate_create_rights()
    @handler('create', method='post')
    def create(self):

        form = MobRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('mobs.create.form_errors', form.errors)

        if [mob for mob in mobs_storage.all() if mob.name == form.c.name.normal_form()]:
            return self.json_error('mobs.create.duplicate_name', 'Монстр с таким названием уже создан')

        mob = MobRecordPrototype.create(uuid=uuid.uuid4().hex,
                                        level=form.c.level,
                                        utg_name=form.c.name,
                                        type=form.c.type,
                                        archetype=form.c.archetype,
                                        description=form.c.description,
                                        abilities=form.c.abilities,
                                        terrains=form.c.terrains,
                                        editor=self.account,
                                        global_action_probability=form.c.global_action_probability,
                                        state=MOB_RECORD_STATE.DISABLED,
                                        communication_verbal=form.c.communication_verbal,
                                        communication_gestures=form.c.communication_gestures,
                                        communication_telepathic=form.c.communication_telepathic,
                                        intellect_level=form.c.intellect_level,
                                        is_mercenary=form.c.is_mercenary,
                                        is_eatable=form.c.is_eatable)
        return self.json_ok(data={'next_url': reverse('guide:mobs:show', args=[mob.id])})


    @login_required
    @validate_disabled_state()
    @validate_create_rights()
    @handler('#mob', 'edit', name='edit', method='get')
    def edit(self):
        form = MobRecordForm(initial=MobRecordForm.get_initials(self.mob))

        return self.template('mobs/edit.html', {'mob': self.mob,
                                                'form': form} )

    @login_required
    @validate_disabled_state()
    @validate_create_rights()
    @handler('#mob', 'update', name='update', method='post')
    def update(self):

        form = MobRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('mobs.update.form_errors', form.errors)

        if [mob for mob in mobs_storage.all() if mob.name == form.c.name.normal_form() and mob.id != self.mob.id]:
            return self.json_error('mobs.update.duplicate_name', 'Монстр с таким названием уже создан')

        self.mob.update_by_creator(form, editor=self.account)

        return self.json_ok(data={'next_url': reverse('guide:mobs:show', args=[self.mob.id])})

    @login_required
    @validate_moderate_rights()
    @handler('#mob', 'moderate', name='moderate', method='get')
    def moderation_page(self):
        form = ModerateMobRecordForm(initial=ModerateMobRecordForm.get_initials(self.mob))

        return self.template('mobs/moderate.html', {'mob': self.mob,
                                                    'form': form} )

    @login_required
    @validate_moderate_rights()
    @handler('#mob', 'moderate', name='moderate', method='post')
    def moderate(self):
        form = ModerateMobRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('mobs.moderate.form_errors', form.errors)

        self.mob.update_by_moderator(form, editor=self.account)

        return self.json_ok(data={'next_url': reverse('guide:mobs:show', args=[self.mob.id])})
