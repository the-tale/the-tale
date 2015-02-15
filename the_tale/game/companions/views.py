# coding: utf-8

from rels.django import DjangoEnum

from dext.common.utils import views as dext_views
from dext.common.utils.urls import UrlBuilder, url

from the_tale.common.utils import list_filter
from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views

from the_tale.game.companions import relations
from the_tale.game.companions import forms
from the_tale.game.companions import logic
from the_tale.game.companions import storage

from the_tale.game.companions.abilities import effects as abilities_effects
from the_tale.game.companions.abilities import relations as abilities_relations

########################################
# processors definition
########################################

create_companion_processor = dext_views.PermissionProcessor(permission='companions.create_companionrecord', context_name='companions_can_edit')
moderate_companion_processor = dext_views.PermissionProcessor(permission='companions.moderate_companionrecord', context_name='companions_can_moderate')


class EditorAccessProcessor(dext_views.AccessProcessor):
    ERROR_CODE = u'companions.no_edit_rights'
    ERROR_MESSAGE = u'Вы не можете редактировать спутников'

    def check(self, context): return context.companions_can_edit


class ModeratorAccessProcessor(dext_views.AccessProcessor):
    ERROR_CODE = u'companions.no_moderate_rights'
    ERROR_MESSAGE = u'Вы не можете модерировать спутников'

    def check(self, context): return context.companions_can_moderate


class CompanionProcessor(dext_views.ArgumentProcessor):

    def parse(self, context, raw_value):
        try:
            id = int(raw_value)
        except ValueError:
            self.raise_wrong_format(context=context)

        return storage.companions.get(id)

# TODO: sync semantics of CompanionProcessor and CompanionProcessor.handler
companion_processor = CompanionProcessor.handler(error_message=u'Спутник не найден', url_name='companion', context_name='companion')

########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='companions')
resource.add_processor(accounts_views.account_processor)
resource.add_processor(utils_views.fake_resource_processor)
resource.add_processor(create_companion_processor)
resource.add_processor(moderate_companion_processor)

########################################
# filters
########################################

INDEX_TYPE = list_filter.filter_relation(relations.TYPE)
INDEX_DEDICATION = list_filter.filter_relation(relations.DEDICATION)
INDEX_ABILITIES = list_filter.filter_relation(abilities_effects.ABILITIES, sort_key=lambda r: r.text)

class INDEX_ORDER(DjangoEnum):
    records = ( ('RARITY', 0, u'по редкости'),
                ('NAME', 1, u'по имени') )

BASE_INDEX_FILTERS = [list_filter.reset_element(),
                      list_filter.choice_element(u'тип:',
                                                 attribute='type',
                                                 default_value=INDEX_TYPE.FILTER_ALL.value,
                                                 choices=INDEX_TYPE.filter_choices()),
                      list_filter.choice_element(u'самоотверженность:',
                                                 attribute='dedication',
                                                 default_value=INDEX_DEDICATION.FILTER_ALL.value,
                                                 choices=INDEX_DEDICATION.filter_choices()),
                      list_filter.choice_element(u'особенность:',
                                                 attribute='ability',
                                                 default_value=INDEX_ABILITIES.FILTER_ALL.value,
                                                 choices=INDEX_ABILITIES.filter_choices()),
                       list_filter.choice_element(u'сортировка:',
                                                  attribute='order_by',
                                                  choices=list(INDEX_ORDER.select('value', 'text')),
                                                  default_value=INDEX_ORDER.RARITY.value) ]

MODERATOR_INDEX_FILTERS = BASE_INDEX_FILTERS + [list_filter.choice_element(u'состояние:',
                                                                           attribute='state',
                                                                           default_value=relations.STATE.ENABLED.value,
                                                                           choices=relations.STATE.select('value', 'text'))]


class NormalIndexFilter(list_filter.ListFilter):
    ELEMENTS = BASE_INDEX_FILTERS

class ModeratorIndexFilter(list_filter.ListFilter):
    ELEMENTS = MODERATOR_INDEX_FILTERS


########################################
# views
########################################

@dext_views.RelationArgumentProcessor.handler(relation=relations.STATE, default_value=relations.STATE.ENABLED,
                                              error_message=u'неверное состояние записи о спутнике',
                                              context_name='companions_state', get_name='state')
@dext_views.RelationArgumentProcessor.handler(relation=INDEX_TYPE, default_value=INDEX_TYPE.FILTER_ALL,
                                              error_message=u'неверный тип спутника',
                                              context_name='companions_type', get_name='type')
@dext_views.RelationArgumentProcessor.handler(relation=INDEX_DEDICATION, default_value=INDEX_DEDICATION.FILTER_ALL,
                                              error_message=u'неверный тип самоотверженности спутника',
                                              context_name='companions_dedication', get_name='dedication')
@dext_views.RelationArgumentProcessor.handler(relation=INDEX_ABILITIES, default_value=INDEX_ABILITIES.FILTER_ALL,
                                              error_message=u'неверный тип особенности спутника',
                                              context_name='companions_ability', get_name='ability')
@dext_views.RelationArgumentProcessor.handler(relation=INDEX_ORDER, default_value=INDEX_ORDER.RARITY,
                                              error_message=u'неверный тип сортировки',
                                              context_name='order_by', get_name='order_by')
@resource.handler('')
def index(context):

    companions = storage.companions.all()

    if context.companions_type.original_relation is not None:
        companions = [companion for companion in companions if companion.type == context.companions_type.original_relation]

    if context.companions_dedication.original_relation is not None:
        companions = [companion for companion in companions if companion.dedication == context.companions_dedication.original_relation]

    if context.companions_ability.original_relation is not None:
        companions = [companion for companion in companions if companion.abilities.has(context.companions_ability.original_relation)]

    if not context.companions_can_edit and not context.companions_can_moderate:
        companions = filter(lambda companion: companion.state.is_ENABLED, companions) # pylint: disable=W0110

    if context.order_by.is_RARITY:
        companions = sorted(companions, key=lambda c: (c.rarity, c.name))
    elif context.order_by.is_NAME:
        companions = sorted(companions, key=lambda c: c.name)

    companions = filter(lambda companion: companion.state == context.companions_state, companions) # pylint: disable=W0110

    url_builder = UrlBuilder(url('guide:companions:'), arguments={ 'state': context.companions_state.value if context.companions_state is not None else None,
                                                                   'type': context.companions_type.value,
                                                                   'dedication': context.companions_dedication.value,
                                                                   'ability': context.companions_ability.value,
                                                                   'order_by': context.order_by.value})

    IndexFilter = ModeratorIndexFilter if context.companions_can_edit or context.companions_can_moderate else NormalIndexFilter #pylint: disable=C0103

    index_filter = IndexFilter(url_builder=url_builder, values={'state': context.companions_state.value if context.companions_state is not None else None,
                                                                'type': context.companions_type.value,
                                                                'dedication': context.companions_dedication.value,
                                                                'ability': context.companions_ability.value,
                                                                'order_by': context.order_by.value})

    return dext_views.Page('companions/index.html',
                           content={'context': context,
                                    'resource': context.resource,
                                    'companions': companions,
                                    'section': 'companions',
                                    'ABILITIES': abilities_effects.ABILITIES,
                                    'METATYPE': abilities_relations.METATYPE,
                                    'DEDICATION': relations.DEDICATION,
                                    'index_filter': index_filter})


@companion_processor
@resource.handler('#companion', name='show')
def show(context):

    if context.companion.state.is_DISABLED and not (context.companions_can_edit or context.companions_can_moderate):
        raise dext_views.exceptions.ViewError(code='companions.show.no_rights', message=u'Вы не можете просматривать информацию по данному спутнику.')

    template_restriction, ingame_companion_phrases = logic.required_templates_count(context.companion)

    return dext_views.Page('companions/show.html',
                           content={'context': context,
                                    'resource': context.resource,
                                    'companion': context.companion,
                                    'ingame_companion_phrases': ingame_companion_phrases,
                                    'template_restriction': template_restriction,
                                    'section': 'companions'})


@companion_processor
@resource.handler('#companion', 'info', name='info')
def show_dialog(context):

    if context.companion.state.is_DISABLED and not (context.companions_can_edit or context.companions_can_moderate):
        raise dext_views.exceptions.ViewError(code='companions.info.no_rights', message=u'Вы не можете просматривать информацию по данному спутнику.')

    return dext_views.Page('companions/info.html',
                           content={'companion': context.companion,
                                    'resource': context.resource})


@accounts_views.LoginRequiredProcessor.handler()
@EditorAccessProcessor.handler()
@resource.handler('new')
def new(context):
    form = forms.CompanionRecordForm()
    return dext_views.Page('companions/new.html',
                           content={'context': context,
                                    'resource': context.resource,
                                    'section': 'companions',
                                    'form': form})


@accounts_views.LoginRequiredProcessor.handler()
@EditorAccessProcessor.handler()
@dext_views.FormProcessor.handler(form_class=forms.CompanionRecordForm)
@resource.handler('create', method='POST')
def create(context):
    companion_record = logic.create_companion_record(utg_name=context.form.c.name,
                                                     description=context.form.c.description,
                                                     type=context.form.c.type,
                                                     max_health=context.form.c.max_health,
                                                     dedication=context.form.c.dedication,
                                                     mode=context.form.c.mode,
                                                     archetype=context.form.c.archetype,
                                                     abilities=context.form.c.abilities)
    return dext_views.AjaxOk(content={'next_url': url('guide:companions:show', companion_record.id)})


@accounts_views.LoginRequiredProcessor.handler()
@EditorAccessProcessor.handler()
@companion_processor
@resource.handler('#companion', 'edit')
def edit(context):
    form = forms.CompanionRecordForm(initial=forms.CompanionRecordForm.get_initials(context.companion))
    return dext_views.Page('companions/edit.html',
                           content={'context': context,
                                    'resource': context.resource,
                                    'companion': context.companion,
                                    'section': 'companions',
                                    'form': form})


@accounts_views.LoginRequiredProcessor.handler()
@EditorAccessProcessor.handler()
@companion_processor
@dext_views.FormProcessor.handler(form_class=forms.CompanionRecordForm)
@resource.handler('#companion', 'update', method='POST')
def update(context):
    logic.update_companion_record(companion=context.companion,
                                  utg_name=context.form.c.name,
                                  description=context.form.c.description,
                                  type=context.form.c.type,
                                  max_health=context.form.c.max_health,
                                  dedication=context.form.c.dedication,
                                  mode=context.form.c.mode,
                                  archetype=context.form.c.archetype,
                                  abilities=context.form.c.abilities)
    return dext_views.AjaxOk(content={'next_url': url('guide:companions:show', context.companion.id)})


@accounts_views.LoginRequiredProcessor.handler()
@ModeratorAccessProcessor.handler()
@companion_processor
@resource.handler('#companion', 'enable', method='POST')
def enable(context):
    logic.enable_companion_record(context.companion)
    return dext_views.AjaxOk()
