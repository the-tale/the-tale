# coding: utf-8

from dext.common.utils import views as dext_views

from the_tale.common.utils import api
from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views

from the_tale.game.heroes import logic as heroes_logic

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
@PersonProcessor(error_message=u'Мастер не найден', url_name='person', context_name='person')
@resource('#person', 'api', 'show', name='api-show')
def api_show(context):
    u'''
Подробная информация о конкретном Мастере

- **адрес:** /game/persons/&lt;person&gt;/api/show
- **http-метод:** GET
- **версии:** 1.0
- **параметры:**
    * URL person — идентификатор Мастера
- **возможные ошибки**: нет

**Это экспериментальный метод, при появлении новой версии не гарантируется работоспособность предыдущей!**

При завершении операции возвращается следующая информация:

    {
      "id": <целое число>,        // идентификатор Мастера
      "name": "строка",           // имя
      "updated_at": <timestamp>,  // время последнего обновления информации

      "place": {                           // краткая информация о городе
          "id": <целое число>,             // идентификатор
          "name": "<строка>",              // название
          "size": <целое число>,           // размер
          "specialization": <целое число>, // специализация
          "position": {                    // координаты
              "x": <целое число>,
              "y": <целое число> }
      },

      // формат следующих параметров такой же, как в методе получения информации о городе

      "politic_power": <politic_power>,    // политическое влияние
      "attributes": <attributes_info>,     // все параметры Мастера
      "chronicle": <chronicle_info>,       // последние записи в летописи
      "accounts": <accounts_info>,         // краткая дополнительная информация об игроках, связанных с Мастером
      "clans": <clans_info>                // краткая дополнительная информация о кланах, связанных с Мастером
    }
    '''

    return dext_views.AjaxOk(content=info.person_info(context.person))


@PersonProcessor(error_message=u'Мастер не найден', url_name='person', context_name='person')
@resource('#person', name='show')
def show(context):

    accounts_short_infos = game_short_info.get_accounts_accounts_info(list(context.person.politic_power.inner_accounts_ids()))

    return dext_views.Page('persons/show.html',
                           content={'person': context.person,
                                    'person_meta_object': meta_relations.Person.create_from_object(context.person),
                                    'accounts_short_infos': accounts_short_infos,
                                    'hero': heroes_logic.load_hero(account_id=context.account.id) if context.account else None,
                                    'resource': context.resource})
