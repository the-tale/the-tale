# coding: utf-8


from dext.common.utils import views as dext_views
from dext.common.utils.urls import UrlBuilder, url

from the_tale.common.utils import list_filter
from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views

from the_tale.game.companions import relations
from the_tale.game.companions import forms
from the_tale.game.companions import logic
from the_tale.game.companions import storage

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
    ERROR_CODE = u'companions.no_moderator_rights'
    ERROR_MESSAGE = u'Вы не можете модерировать спутников'


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
BASE_INDEX_FILTERS = [list_filter.reset_element()]

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
@resource.handler('')
def index(context):

    companions = storage.companions.all()

    if not context.companions_can_edit and not context.companions_can_moderate:
        companions = filter(lambda companion: companion.state.is_ENABLED, companions) # pylint: disable=W0110

    companions = filter(lambda companion: companion.state == context.companions_state, companions) # pylint: disable=W0110

    url_builder = UrlBuilder(url('guide:companions:'), arguments={ 'state': context.companions_state.value if context.companions_state is not None else None})

    IndexFilter = ModeratorIndexFilter if context.companions_can_edit or context.companions_can_moderate else NormalIndexFilter #pylint: disable=C0103

    index_filter = IndexFilter(url_builder=url_builder, values={'state': context.companions_state.value if context.companions_state is not None else None})

    return dext_views.Page('companions/index.html',
                           content={'context': context,
                                    'resource': context.resource,
                                    'companions': companions,
                                    'section': 'companions',
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
                                                     rarity=context.form.c.rarity)
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
                                  rarity=context.form.c.rarity)
    return dext_views.AjaxOk(content={'next_url': url('guide:companions:show', context.companion.id)})
