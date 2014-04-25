# coding: utf-8
import uuid

from django.core.urlresolvers import reverse

from dext.views import handler, validator, validate_argument
from dext.utils.urls import UrlBuilder

from the_tale.common.utils import list_filter
from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required

from the_tale.game.map.relations import TERRAIN

from the_tale.game.artifacts import relations
from the_tale.game.artifacts import effects
from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype
from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.artifacts.forms import ArtifactRecordForm, ModerateArtifactRecordForm

EFFECTS_CHOICES = sorted(relations.ARTIFACT_EFFECT.select('value', 'text'),
                         key=lambda v: v[1])

BASE_INDEX_FILTERS = [list_filter.reset_element(),
                      list_filter.choice_element(u'экипировка:', attribute='type', choices=[(None, u'все')] + list(relations.ARTIFACT_TYPE.select('value', 'text'))),
                      list_filter.choice_element(u'сила:', attribute='power_type', choices=[(None, u'все')] + list(relations.ARTIFACT_POWER_TYPE.select('value', 'text'))),
                      list_filter.choice_element(u'эффекты:', attribute='effect', choices=[(None, u'все')] + EFFECTS_CHOICES),
                      list_filter.choice_element(u'сортировка:',
                                                 attribute='order_by',
                                                 choices=[(None, u'все')] + list(relations.INDEX_ORDER_TYPE.select('value', 'text')),
                                                 default_value=relations.INDEX_ORDER_TYPE.BY_NAME.value) ]

MODERATOR_INDEX_FILTERS = list(BASE_INDEX_FILTERS)
MODERATOR_INDEX_FILTERS.append(list_filter.choice_element(u'состояние:',
                                                          attribute='state',
                                                          choices=list(relations.ARTIFACT_RECORD_STATE.select('value', 'text')),
                                                          default_value=relations.ARTIFACT_RECORD_STATE.ENABLED.value))

class BaseIndexFilter(list_filter.ListFilter):
    ELEMENTS = BASE_INDEX_FILTERS

class ModeratorIndexFilter(list_filter.ListFilter):
    ELEMENTS = MODERATOR_INDEX_FILTERS

def argument_to_artifact_type(value): return relations.ARTIFACT_TYPE(int(value))
def argument_to_artifact(value): return artifacts_storage.get(int(value), None)
def argument_to_effect_type(value): return relations.ARTIFACT_EFFECT(int(value))
def argument_to_power_type(value): return relations.ARTIFACT_POWER_TYPE(int(value))


class ArtifactResourceBase(Resource):

    @validate_argument('artifact', argument_to_artifact, 'artifacts', u'Запись об артефакте не найдена')
    def initialize(self, artifact=None, *args, **kwargs):
        super(ArtifactResourceBase, self).initialize(*args, **kwargs)
        self.artifact = artifact

        self.can_create_artifact = self.account.has_perm('artifacts.create_artifactrecord')
        self.can_moderate_artifact = self.account.has_perm('artifacts.moderate_artifactrecord')


class GuideArtifactResource(ArtifactResourceBase):


    @validator(code='artifacts.artifact_disabled', message=u'артефакт находится вне игры', status_code=404)
    def validate_artifact_disabled(self, *args, **kwargs):
        return not self.artifact.state.is_DISABLED or self.can_create_artifact or self.can_moderate_artifact


    @validate_argument('state', lambda v: relations.ARTIFACT_RECORD_STATE.index_value[int(v)], 'artifacts', u'неверное состояние записи об артефакте')
    @validate_argument('type', argument_to_artifact_type, 'artifacts', u'неверный тип слота экипировки')
    @validate_argument('effect', argument_to_effect_type, 'artifacts', u'неверный тип эффекта')
    @validate_argument('power_type', argument_to_power_type, 'artifacts', u'неверный тип артефакта')
    @validate_argument('order_by', relations.INDEX_ORDER_TYPE, 'artifacts', u'неверный тип сортировки')
    @handler('', method='get')
    def index(self,
              state=relations.ARTIFACT_RECORD_STATE.ENABLED,
              effect=None,
              type=None, # pylint: disable=W0622
              power_type=None, # pylint: disable=W0622
              order_by=relations.INDEX_ORDER_TYPE.BY_NAME):

        artifacts = artifacts_storage.all()

        if not self.can_create_artifact and not self.can_moderate_artifact:
            artifacts = filter(lambda artifact: artifact.state.is_ENABLED, artifacts) # pylint: disable=W0110

        if state is not None:
            artifacts = filter(lambda artifact: artifact.state == state, artifacts) # pylint: disable=W0110

        if effect is not None:
            artifacts = filter(lambda artifact: artifact.rare_effect == effect or artifact.epic_effect == effect, artifacts) # pylint: disable=W0110

        if type is not None:
            artifacts = filter(lambda artifact: artifact.type == type, artifacts) # pylint: disable=W0110

        if power_type is not None:
            artifacts = filter(lambda artifact: artifact.power_type == power_type, artifacts) # pylint: disable=W0110

        if order_by.is_BY_NAME:
            artifacts = sorted(artifacts, key=lambda artifact: artifact.name)
        elif order_by.is_BY_LEVEL:
            artifacts = sorted(artifacts, key=lambda artifact: artifact.level)

        if self.can_create_artifact or self.can_moderate_artifact:
            IndexFilter = ModeratorIndexFilter
        else:
            IndexFilter = BaseIndexFilter

        url_builder = UrlBuilder(reverse('guide:artifacts:'), arguments={ 'state': state.value if state else None,
                                                                          'type': type.value if type else None,
                                                                          'power_type': power_type.value if power_type else None,
                                                                          'effect': effect.value if effect else None,
                                                                          'order_by': order_by.value})

        index_filter = IndexFilter(url_builder=url_builder, values={'state': state.value if state else None,
                                                                    'type': type.value if type else None,
                                                                    'power_type': power_type.value if power_type else None,
                                                                    'effect': effect.value if effect else None,
                                                                    'order_by': order_by.value if order_by else None})

        return self.template('artifacts/index.html',
                             {'artifacts': artifacts,
                              'ARTIFACT_RECORD_STATE': relations.ARTIFACT_RECORD_STATE,
                              'TERRAIN': TERRAIN,
                              'ARTIFACT_TYPE': relations.ARTIFACT_TYPE,
                              'state': state,
                              'type': type,
                              'order_by': order_by,
                              'index_filter': index_filter,
                              'section': 'artifacts',
                              'EFFECTS': sorted(effects.EFFECTS.values(), key=lambda v: v.TYPE.text)} )

    @validate_artifact_disabled()
    @handler('#artifact', name='show', method='get')
    def show(self):
        return self.template('artifacts/show.html', {'artifact': self.artifact,
                                                     'section': 'artifacts',
                                                     'EFFECTS': effects.EFFECTS})

    @validate_artifact_disabled()
    @handler('#artifact', 'info', method='get')
    def show_dialog(self):
        return self.template('artifacts/info.html', {'artifact': self.artifact,
                                                     'EFFECTS': effects.EFFECTS})


class GameArtifactResource(ArtifactResourceBase):

    @validator(code='artifacts.create_artifact_rights_required', message=u'Вы не можете создавать артефакты')
    def validate_create_rights(self, *args, **kwargs): return self.can_create_artifact

    @validator(code='artifacts.moderate_artifact_rights_required', message=u'Вы не можете принимать артефакты в игру')
    def validate_moderate_rights(self, *args, **kwargs): return self.can_moderate_artifact

    @validator(code='artifacts.disabled_state_required', message=u'Для проведения этой операции артефакт должен быть убран из игры')
    def validate_disabled_state(self, *args, **kwargs): return self.artifact.state.is_DISABLED

    @login_required
    @validate_create_rights()
    @handler('new', method='get')
    def new(self):
        return self.template('artifacts/new.html', {'form': ArtifactRecordForm(initial={'rare_effect': relations.ARTIFACT_EFFECT.NO_EFFECT,
                                                                                        'epic_effect': relations.ARTIFACT_EFFECT.NO_EFFECT})})

    @login_required
    @validate_create_rights()
    @handler('create', method='post')
    def create(self):

        form = ArtifactRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('artifacts.create.form_errors', form.errors)

        artifact = ArtifactRecordPrototype.create(uuid=uuid.uuid4().hex,
                                                  level=form.c.level,
                                                  name=form.c.name,
                                                  description=form.c.description,
                                                  type_=form.c.type,
                                                  editor=self.account,
                                                  state=relations.ARTIFACT_RECORD_STATE.DISABLED,
                                                  power_type=form.c.power_type,
                                                  rare_effect=form.c.rare_effect,
                                                  epic_effect=form.c.epic_effect,
                                                  mob=form.c.mob)
        return self.json_ok(data={'next_url': reverse('guide:artifacts:show', args=[artifact.id])})


    @login_required
    @validate_disabled_state()
    @validate_create_rights()
    @handler('#artifact', 'edit', name='edit', method='get')
    def edit(self):
        form = ArtifactRecordForm(initial={'name': self.artifact.name,
                                           'level': self.artifact.level,
                                           'type': self.artifact.type,
                                           'power_type': self.artifact.power_type,
                                           'rare_effect': self.artifact.rare_effect,
                                           'epic_effect': self.artifact.epic_effect,
                                           'description': self.artifact.description,
                                           'mob': self.artifact.mob.id if self.artifact.mob is not None else None})

        return self.template('artifacts/edit.html', {'artifact': self.artifact,
                                                     'form': form} )

    @login_required
    @validate_disabled_state()
    @validate_create_rights()
    @handler('#artifact', 'update', name='update', method='post')
    def update(self):

        form = ArtifactRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('artifacts.update.form_errors', form.errors)

        self.artifact.update_by_creator(form, editor=self.account)

        return self.json_ok(data={'next_url': reverse('guide:artifacts:show', args=[self.artifact.id])})

    @login_required
    @validate_moderate_rights()
    @handler('#artifact', 'moderate', name='moderate', method='get')
    def moderation_page(self):
        form = ModerateArtifactRecordForm(initial={'name': self.artifact.name,
                                                   'level': self.artifact.level,
                                                   'type': self.artifact.type,
                                                   'power_type': self.artifact.power_type,
                                                   'rare_effect': self.artifact.rare_effect,
                                                   'epic_effect': self.artifact.epic_effect,
                                                   'description': self.artifact.description,
                                                   'uuid': self.artifact.uuid,
                                                   'name_forms': self.artifact.name_forms.serialize(),
                                                   'approved': self.artifact.state.is_ENABLED,
                                                   'mob': self.artifact.mob.id if self.artifact.mob is not None else None})

        return self.template('artifacts/moderate.html', {'artifact': self.artifact,
                                                         'form': form} )

    @login_required
    @validate_moderate_rights()
    @handler('#artifact', 'moderate', name='moderate', method='post')
    def moderate(self):
        form = ModerateArtifactRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('artifacts.moderate.form_errors', form.errors)

        self.artifact.update_by_moderator(form, editor=self.account)

        return self.json_ok(data={'next_url': reverse('guide:artifacts:show', args=[self.artifact.id])})
