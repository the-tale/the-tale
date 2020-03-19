
import smart_imports

smart_imports.all()


EFFECTS_CHOICES = sorted(relations.ARTIFACT_EFFECT.select('value', 'text'),
                         key=lambda v: v[1])

BASE_INDEX_FILTERS = [utils_list_filter.reset_element(),
                      utils_list_filter.choice_element('экипировка:', attribute='type', choices=[(None, 'все')] + list(relations.ARTIFACT_TYPE.select('value', 'text'))),
                      utils_list_filter.choice_element('сила:', attribute='power_type', choices=[(None, 'все')] + list(relations.ARTIFACT_POWER_TYPE.select('value', 'text'))),
                      utils_list_filter.choice_element('эффекты:', attribute='effect', choices=[(None, 'все')] + EFFECTS_CHOICES),
                      utils_list_filter.choice_element('сортировка:',
                                                       attribute='order_by',
                                                       choices=[(None, 'все')] + list(relations.INDEX_ORDER_TYPE.select('value', 'text')),
                                                       default_value=relations.INDEX_ORDER_TYPE.BY_NAME.value)]

MODERATOR_INDEX_FILTERS = list(BASE_INDEX_FILTERS)
MODERATOR_INDEX_FILTERS.append(utils_list_filter.choice_element('состояние:',
                                                                attribute='state',
                                                                choices=list(relations.ARTIFACT_RECORD_STATE.select('value', 'text')),
                                                                default_value=relations.ARTIFACT_RECORD_STATE.ENABLED.value))


class BaseIndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = BASE_INDEX_FILTERS


class ModeratorIndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = MODERATOR_INDEX_FILTERS


def argument_to_artifact_type(value): return relations.ARTIFACT_TYPE(int(value))


def argument_to_artifact(value): return storage.artifacts.get(int(value), None)


def argument_to_effect_type(value): return relations.ARTIFACT_EFFECT(int(value))


def argument_to_power_type(value): return relations.ARTIFACT_POWER_TYPE(int(value))


class ArtifactResourceBase(utils_resources.Resource):

    @old_views.validate_argument('artifact', argument_to_artifact, 'artifacts', 'Запись об артефакте не найдена')
    def initialize(self, artifact=None, *args, **kwargs):
        super(ArtifactResourceBase, self).initialize(*args, **kwargs)
        self.artifact = artifact

        self.can_create_artifact = self.account.has_perm('artifacts.create_artifactrecord')
        self.can_moderate_artifact = self.account.has_perm('artifacts.moderate_artifactrecord')


@old_views.validator(code='artifacts.artifact_disabled', message='артефакт находится вне игры', status_code=404)
def validate_artifact_disabled(resource, *args, **kwargs):
    return not resource.artifact.state.is_DISABLED or resource.can_create_artifact or resource.can_moderate_artifact


class GuideArtifactResource(ArtifactResourceBase):

    @old_views.validate_argument('state', lambda v: relations.ARTIFACT_RECORD_STATE.index_value[int(v)], 'artifacts', 'неверное состояние записи об артефакте')
    @old_views.validate_argument('type', argument_to_artifact_type, 'artifacts', 'неверный тип слота экипировки')
    @old_views.validate_argument('effect', argument_to_effect_type, 'artifacts', 'неверный тип эффекта')
    @old_views.validate_argument('power_type', argument_to_power_type, 'artifacts', 'неверный тип артефакта')
    @old_views.validate_argument('order_by', relations.INDEX_ORDER_TYPE, 'artifacts', 'неверный тип сортировки')
    @old_views.handler('', method='get')
    def index(self,
              state=relations.ARTIFACT_RECORD_STATE.ENABLED,
              effect=None,
              type=None,  # pylint: disable=W0622
              power_type=None,  # pylint: disable=W0622
              order_by=relations.INDEX_ORDER_TYPE.BY_NAME):

        artifacts = storage.artifacts.all()

        if not self.can_create_artifact and not self.can_moderate_artifact:
            artifacts = [artifact for artifact in artifacts if artifact.state.is_ENABLED]  # pylint: disable=W0110

        if state is not None:
            artifacts = [artifact for artifact in artifacts if artifact.state == state]  # pylint: disable=W0110

        if effect is not None:
            artifacts = [artifact for artifact in artifacts if artifact.rare_effect == effect or artifact.epic_effect == effect]  # pylint: disable=W0110

        if type is not None:
            artifacts = [artifact for artifact in artifacts if artifact.type == type]  # pylint: disable=W0110

        if power_type is not None:
            artifacts = [artifact for artifact in artifacts if artifact.power_type == power_type]  # pylint: disable=W0110

        if order_by.is_BY_NAME:
            artifacts = sorted(artifacts, key=lambda artifact: artifact.name)
        elif order_by.is_BY_LEVEL:
            artifacts = sorted(artifacts, key=lambda artifact: artifact.level)

        if self.can_create_artifact or self.can_moderate_artifact:
            IndexFilter = ModeratorIndexFilter
        else:
            IndexFilter = BaseIndexFilter

        url_builder = utils_urls.UrlBuilder(django_reverse('guide:artifacts:'), arguments={'state': state.value if state else None,
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
                              'TERRAIN': map_relations.TERRAIN,
                              'ARTIFACT_TYPE': relations.ARTIFACT_TYPE,
                              'state': state,
                              'type': type,
                              'order_by': order_by,
                              'index_filter': index_filter,
                              'section': 'artifacts',
                              'EFFECTS': sorted(list(effects.EFFECTS.values()), key=lambda v: v.TYPE.text)})

    @validate_artifact_disabled()
    @old_views.handler('#artifact', name='show', method='get')
    def show(self):
        return self.template('artifacts/show.html', {'artifact': self.artifact,
                                                     'artifact_meta_object': meta_relations.Artifact.create_from_object(self.artifact),
                                                     'section': 'artifacts',
                                                     'EFFECTS': effects.EFFECTS})

    @validate_artifact_disabled()
    @old_views.handler('#artifact', 'info', method='get')
    def show_dialog(self):
        return self.template('artifacts/info.html', {'artifact': self.artifact,
                                                     'artifact_meta_object': meta_relations.Artifact.create_from_object(self.artifact),
                                                     'EFFECTS': effects.EFFECTS})


@old_views.validator(code='artifacts.create_artifact_rights_required', message='Вы не можете создавать артефакты')
def validate_create_rights(resource, *args, **kwargs): return resource.can_create_artifact


@old_views.validator(code='artifacts.moderate_artifact_rights_required', message='Вы не можете принимать артефакты в игру')
def validate_moderate_rights(resource, *args, **kwargs): return resource.can_moderate_artifact


@old_views.validator(code='artifacts.disabled_state_required', message='Для проведения этой операции артефакт должен быть убран из игры')
def validate_disabled_state(resource, *args, **kwargs): return resource.artifact.state.is_DISABLED


class GameArtifactResource(ArtifactResourceBase):

    @utils_decorators.login_required
    @validate_create_rights()
    @old_views.handler('new', method='get')
    def new(self):
        form = forms.ArtifactRecordForm(initial={'rare_effect': relations.ARTIFACT_EFFECT.NO_EFFECT,
                                                 'epic_effect': relations.ARTIFACT_EFFECT.NO_EFFECT,
                                                 'special_effect': relations.ARTIFACT_EFFECT.NO_EFFECT})
        return self.template('artifacts/new.html', {'form': form})

    @utils_decorators.login_required
    @validate_create_rights()
    @old_views.handler('create', method='post')
    def create(self):

        form = forms.ArtifactRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('artifacts.create.form_errors', form.errors)

        artifact = logic.create_artifact_record(uuid=uuid.uuid4().hex,
                                                level=form.c.level,
                                                utg_name=form.c.name,
                                                description=form.c.description,
                                                type=form.c.type,
                                                editor=self.account,
                                                state=relations.ARTIFACT_RECORD_STATE.DISABLED,
                                                power_type=form.c.power_type,
                                                rare_effect=form.c.rare_effect,
                                                epic_effect=form.c.epic_effect,
                                                special_effect=form.c.special_effect,
                                                weapon_type=form.c.weapon_type,
                                                material=form.c.material,
                                                mob=form.c.mob)

        return self.json_ok(data={'next_url': django_reverse('guide:artifacts:show', args=[artifact.id])})

    @utils_decorators.login_required
    @validate_disabled_state()
    @validate_create_rights()
    @old_views.handler('#artifact', 'edit', name='edit', method='get')
    def edit(self):
        form = forms.ArtifactRecordForm(initial=forms.ArtifactRecordForm.get_initials(self.artifact))

        return self.template('artifacts/edit.html', {'artifact': self.artifact,
                                                     'form': form})

    @utils_decorators.login_required
    @validate_disabled_state()
    @validate_create_rights()
    @old_views.handler('#artifact', 'update', name='update', method='post')
    def update(self):

        form = forms.ArtifactRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('artifacts.update.form_errors', form.errors)

        logic.update_by_creator(self.artifact, form, editor=self.account)

        return self.json_ok(data={'next_url': django_reverse('guide:artifacts:show', args=[self.artifact.id])})

    @utils_decorators.login_required
    @validate_moderate_rights()
    @old_views.handler('#artifact', 'moderate', name='moderate', method='get')
    def moderation_page(self):
        form = forms.ModerateArtifactRecordForm(initial=forms.ModerateArtifactRecordForm.get_initials(self.artifact))

        return self.template('artifacts/moderate.html', {'artifact': self.artifact,
                                                         'form': form})

    @utils_decorators.login_required
    @validate_moderate_rights()
    @old_views.handler('#artifact', 'moderate', name='moderate', method='post')
    def moderate(self):
        form = forms.ModerateArtifactRecordForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('artifacts.moderate.form_errors', form.errors)

        logic.update_by_moderator(self.artifact, form, editor=self.account)

        return self.json_ok(data={'next_url': django_reverse('guide:artifacts:show', args=[self.artifact.id])})
