
from dext.common.utils import views as dext_views

from the_tale.common.utils import api
from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views

from the_tale.game.heroes import logic as heroes_logic
from the_tale.game.chronicle import prototypes as chronicle_prototypes

from the_tale.game.politic_power import logic as politic_power_logic
from the_tale.game.politic_power import storage as politic_power_storage

from the_tale.game import short_info as game_short_info

from . import conf
from . import info
from . import storage
from . import meta_relations


########################################
# processors definition
########################################

class PersonProcessor(dext_views.ArgumentProcessor):
    def parse(self, context, raw_value):
        try:
            id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        if id not in storage.persons:
            self.raise_wrong_value()

        return storage.persons.get(id)

########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='companions')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())


@api.Processor(versions=(conf.settings.API_SHOW_VERSION,))
@PersonProcessor(error_message='Мастер не найден', url_name='person', context_name='person')
@resource('#person', 'api', 'show', name='api-show')
def api_show(context):
    return dext_views.AjaxOk(content=info.person_info(context.person))


@PersonProcessor(error_message='Мастер не найден', url_name='person', context_name='person')
@resource('#person', name='show')
def show(context):

    inner_circle = politic_power_logic.get_inner_circle(person_id=context.person.id)

    accounts_short_infos = game_short_info.get_accounts_accounts_info(inner_circle.heroes_ids())

    job_power = politic_power_logic.get_job_power(person_id=context.person.id)

    return dext_views.Page('persons/show.html',
                           content={'person': context.person,
                                    'person_meta_object': meta_relations.Person.create_from_object(context.person),
                                    'accounts_short_infos': accounts_short_infos,
                                    'hero': heroes_logic.load_hero(account_id=context.account.id) if context.account else None,
                                    'social_connections': storage.social_connections.get_connected_persons(context.person),
                                    'master_chronicle': chronicle_prototypes.RecordPrototype.get_last_actor_records(context.person, conf.settings.CHRONICLE_RECORDS_NUMBER),
                                    'inner_circle': inner_circle,
                                    'persons_power_storage': politic_power_storage.persons,
                                    'job_power': job_power,
                                    'resource': context.resource})
