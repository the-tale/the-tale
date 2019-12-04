
import smart_imports

smart_imports.all()


########################################
# processors definition
########################################


class CreateCompanionProcessor(utils_views.PermissionProcessor):
    PERMISSION = 'companions.create_companionrecord'
    CONTEXT_NAME = 'companions_can_edit'


class ModerateCompanionProcessor(utils_views.PermissionProcessor):
    PERMISSION = 'companions.moderate_companionrecord'
    CONTEXT_NAME = 'companions_can_moderate'


class EditorAccessProcessor(utils_views.AccessProcessor):
    ERROR_CODE = 'companions.no_edit_rights'
    ERROR_MESSAGE = 'Вы не можете редактировать спутников'

    def check(self, context):
        return context.companions_can_edit


class ModeratorAccessProcessor(utils_views.AccessProcessor):
    ERROR_CODE = 'companions.no_moderate_rights'
    ERROR_MESSAGE = 'Вы не можете модерировать спутников'

    def check(self, context):
        return context.companions_can_moderate


class CompanionProcessor(utils_views.ArgumentProcessor):
    ERROR_MESSAGE = 'Спутник не найден'
    URL_NAME = 'companion'
    CONTEXT_NAME = 'companion'

    def parse(self, context, raw_value):
        try:
            id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        if id not in storage.companions:
            self.raise_wrong_value()

        return storage.companions.get(id)


########################################
# resource and global processors
########################################
resource = utils_views.Resource(name='companions')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(CreateCompanionProcessor())
resource.add_processor(ModerateCompanionProcessor())


########################################
# filters
########################################

INDEX_TYPE = utils_list_filter.filter_relation(tt_beings_relations.TYPE)
INDEX_DEDICATION = utils_list_filter.filter_relation(relations.DEDICATION)
INDEX_ABILITIES = utils_list_filter.filter_relation(companions_abilities_effects.ABILITIES, sort_key=lambda r: r.text)


class INDEX_ORDER(rels_django.DjangoEnum):
    records = (('RARITY', 0, 'по редкости'),
               ('NAME', 1, 'по имени'))


BASE_INDEX_FILTERS = [utils_list_filter.reset_element(),
                      utils_list_filter.choice_element('тип:',
                                                       attribute='type',
                                                       default_value=INDEX_TYPE.FILTER_ALL.value,
                                                       choices=INDEX_TYPE.filter_choices()),
                      utils_list_filter.choice_element('самоотверженность:',
                                                       attribute='dedication',
                                                       default_value=INDEX_DEDICATION.FILTER_ALL.value,
                                                       choices=INDEX_DEDICATION.filter_choices()),
                      utils_list_filter.choice_element('особенность:',
                                                       attribute='ability',
                                                       default_value=INDEX_ABILITIES.FILTER_ALL.value,
                                                       choices=INDEX_ABILITIES.filter_choices()),
                      utils_list_filter.choice_element('сортировка:',
                                                       attribute='order_by',
                                                       choices=list(INDEX_ORDER.select('value', 'text')),
                                                       default_value=INDEX_ORDER.RARITY.value)]

MODERATOR_INDEX_FILTERS = BASE_INDEX_FILTERS + [utils_list_filter.choice_element('состояние:',
                                                                                 attribute='state',
                                                                                 default_value=relations.STATE.ENABLED.value,
                                                                                 choices=relations.STATE.select('value', 'text'))]


class NormalIndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = BASE_INDEX_FILTERS


class ModeratorIndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = MODERATOR_INDEX_FILTERS


########################################
# views
########################################

@utils_views.RelationArgumentProcessor(relation=relations.STATE, default_value=relations.STATE.ENABLED,
                                       error_message='неверное состояние записи о спутнике',
                                       context_name='companions_state', get_name='state')
@utils_views.RelationArgumentProcessor(relation=INDEX_TYPE, default_value=INDEX_TYPE.FILTER_ALL,
                                       error_message='неверный тип спутника',
                                       context_name='companions_type', get_name='type')
@utils_views.RelationArgumentProcessor(relation=INDEX_DEDICATION, default_value=INDEX_DEDICATION.FILTER_ALL,
                                       error_message='неверный тип самоотверженности спутника',
                                       context_name='companions_dedication', get_name='dedication')
@utils_views.RelationArgumentProcessor(relation=INDEX_ABILITIES, default_value=INDEX_ABILITIES.FILTER_ALL,
                                       error_message='неверный тип особенности спутника',
                                       context_name='companions_ability', get_name='ability')
@utils_views.RelationArgumentProcessor(relation=INDEX_ORDER, default_value=INDEX_ORDER.RARITY,
                                       error_message='неверный тип сортировки',
                                       context_name='order_by', get_name='order_by')
@resource('')
def index(context):

    companions = storage.companions.all()

    if context.companions_type.original_relation is not None:
        companions = [companion for companion in companions if companion.type == context.companions_type.original_relation]

    if context.companions_dedication.original_relation is not None:
        companions = [companion for companion in companions if companion.dedication == context.companions_dedication.original_relation]

    if context.companions_ability.original_relation is not None:
        companions = [companion for companion in companions if companion.abilities.has(context.companions_ability.original_relation)]

    if not context.companions_can_edit and not context.companions_can_moderate:
        companions = [companion for companion in companions if companion.state.is_ENABLED]  # pylint: disable=W0110

    if context.order_by.is_RARITY:
        companions = sorted(companions, key=lambda c: (c.rarity.value, c.name))
    elif context.order_by.is_NAME:
        companions = sorted(companions, key=lambda c: c.name)

    companions = [companion for companion in companions if companion.state == context.companions_state]  # pylint: disable=W0110

    url_builder = utils_urls.UrlBuilder(utils_urls.url('guide:companions:'), arguments={'state': context.companions_state.value if context.companions_state is not None else None,
                                                                                      'type': context.companions_type.value,
                                                                                      'dedication': context.companions_dedication.value,
                                                                                      'ability': context.companions_ability.value,
                                                                                      'order_by': context.order_by.value})

    IndexFilter = ModeratorIndexFilter if context.companions_can_edit or context.companions_can_moderate else NormalIndexFilter  # pylint: disable=C0103

    index_filter = IndexFilter(url_builder=url_builder, values={'state': context.companions_state.value if context.companions_state is not None else None,
                                                                'type': context.companions_type.value,
                                                                'dedication': context.companions_dedication.value,
                                                                'ability': context.companions_ability.value,
                                                                'order_by': context.order_by.value})

    return utils_views.Page('companions/index.html',
                            content={'context': context,
                                     'resource': context.resource,
                                     'companions': companions,
                                     'section': 'companions',
                                     'ABILITIES': companions_abilities_effects.ABILITIES,
                                     'METATYPE': companions_abilities_relations.METATYPE,
                                     'DEDICATION': relations.DEDICATION,
                                     'index_filter': index_filter})


@CompanionProcessor()
@resource('#companion', name='show')
def show(context):

    if context.companion.state.is_DISABLED and not (context.companions_can_edit or context.companions_can_moderate):
        raise utils_views.ViewError(code='no_rights', message='Вы не можете просматривать информацию по данному спутнику.')

    template_restriction, ingame_companion_phrases = logic.required_templates_count(context.companion)

    return utils_views.Page('companions/show.html',
                            content={'context': context,
                                     'companion_meta_object': meta_relations.Companion.create_from_object(context.companion),
                                     'resource': context.resource,
                                     'companion': context.companion,
                                     'ingame_companion_phrases': ingame_companion_phrases,
                                     'template_restriction': template_restriction,
                                     'section': 'companions'})


@CompanionProcessor()
@resource('#companion', 'info', name='info')
def show_dialog(context):

    if context.companion.state.is_DISABLED and not (context.companions_can_edit or context.companions_can_moderate):
        raise utils_views.ViewError(code='no_rights', message='Вы не можете просматривать информацию по данному спутнику.')

    return utils_views.Page('companions/info.html',
                            content={'companion': context.companion,
                                     'companion_meta_object': meta_relations.Companion.create_from_object(context.companion),
                                     'resource': context.resource})


@accounts_views.LoginRequiredProcessor()
@EditorAccessProcessor()
@resource('new')
def new(context):
    form = forms.CompanionRecordForm()
    return utils_views.Page('companions/new.html',
                            content={'context': context,
                                     'resource': context.resource,
                                     'section': 'companions',
                                     'form': form})


@accounts_views.LoginRequiredProcessor()
@EditorAccessProcessor()
@utils_views.FormProcessor(form_class=forms.CompanionRecordForm)
@resource('create', method='POST')
def create(context):
    companion_record = logic.create_companion_record(utg_name=context.form.c.name,
                                                     description=context.form.c.description,
                                                     type=context.form.c.type,
                                                     max_health=context.form.c.max_health,
                                                     dedication=context.form.c.dedication,
                                                     mode=context.form.c.mode,
                                                     archetype=context.form.c.archetype,
                                                     abilities=context.form.c.abilities,
                                                     communication_verbal=context.form.c.communication_verbal,
                                                     communication_gestures=context.form.c.communication_gestures,
                                                     communication_telepathic=context.form.c.communication_telepathic,
                                                     intellect_level=context.form.c.intellect_level,
                                                     structure=context.form.c.structure,
                                                     features=context.form.c.features,
                                                     movement=context.form.c.movement,
                                                     body=context.form.c.body,
                                                     size=context.form.c.size,
                                                     orientation=context.form.c.orientation,
                                                     weapons=context.form.get_weapons())
    return utils_views.AjaxOk(content={'next_url': utils_urls.url('guide:companions:show', companion_record.id)})


@accounts_views.LoginRequiredProcessor()
@EditorAccessProcessor()
@CompanionProcessor()
@resource('#companion', 'edit')
def edit(context):
    form = forms.CompanionRecordForm(initial=forms.CompanionRecordForm.get_initials(context.companion))
    return utils_views.Page('companions/edit.html',
                            content={'context': context,
                                     'resource': context.resource,
                                     'companion': context.companion,
                                     'section': 'companions',
                                     'form': form})


@accounts_views.LoginRequiredProcessor()
@EditorAccessProcessor()
@CompanionProcessor()
@utils_views.FormProcessor(form_class=forms.CompanionRecordForm)
@resource('#companion', 'update', method='POST')
def update(context):
    logic.update_companion_record(companion=context.companion,
                                  utg_name=context.form.c.name,
                                  description=context.form.c.description,
                                  type=context.form.c.type,
                                  max_health=context.form.c.max_health,
                                  dedication=context.form.c.dedication,
                                  mode=context.form.c.mode,
                                  archetype=context.form.c.archetype,
                                  abilities=context.form.c.abilities,
                                  communication_verbal=context.form.c.communication_verbal,
                                  communication_gestures=context.form.c.communication_gestures,
                                  communication_telepathic=context.form.c.communication_telepathic,
                                  intellect_level=context.form.c.intellect_level,
                                  structure=context.form.c.structure,
                                  features=context.form.c.features,
                                  movement=context.form.c.movement,
                                  body=context.form.c.body,
                                  size=context.form.c.size,
                                  orientation=context.form.c.orientation,
                                  weapons=context.form.get_weapons())
    return utils_views.AjaxOk(content={'next_url': utils_urls.url('guide:companions:show', context.companion.id)})


@accounts_views.LoginRequiredProcessor()
@ModeratorAccessProcessor()
@CompanionProcessor()
@resource('#companion', 'enable', method='POST')
def enable(context):
    logic.enable_companion_record(context.companion)
    return utils_views.AjaxOk()
