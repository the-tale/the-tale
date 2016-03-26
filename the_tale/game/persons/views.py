# coding: utf-8

from dext.common.utils import views as dext_views

from the_tale.common.utils import api
from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views

from the_tale.game import relations as game_relations

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.places import storage as places_storage

from the_tale.game import short_info as game_short_info

from . import conf
from . import logic
from . import storage
from . import relations
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
      "name": "строка",           // имя Мастера
      "place_id": <целое число>,  // идентификатор города в котором живёт
      "updated_at": <timestamp>,  // время последнего обновления информации

      "politic_power": <politic_power>,     // информация о политическом влиянии Мастера

      "race": <целое число>,                // раса
      "gender": <целое число>,              // пол
      "professioon": <целое число>,         // профессия

      "personality": {
        "cosmetic": <целое число>,          // идентификатор косметической особенности характера
        "practical":  <целое число>         // идентификатор практической особенности характера
      },

      "building": <целое число>|null,       // идентификатор здания, если оно есть

      "connections": [(<целое число>, <целое число>),…], // список социальных связей советника в виде <тип связи, идентификатор второго советника>

      "keepers": <keepers_info>,                   // игроки, связанные с Мастером

      "chronicle": <chronicle_info>,               // последние записи в летописи
      "accounts": <accounts_info>,                 // краткая дополнительная информация об игроках, связанных с Мастером
      "clans": <clans_info>                        // краткая дополнительная информация о кланах, связанных с Мастером
    }

    <keepers_info> = {
      "friends": [<целое число>, …], // список идентификаторов игроков, чьи герои помогают Мастеру
      "enemies": [<целое число>, …]  // список идентификаторов игроков, чьи герои вредят Мастеру
    }


    <chronicle_info> = [("строка", "строка", "строка"), …] // последние записи из летописи о городе в формате ("короткая дата", "длинная дата", "текст")

    <accounts_info> = {
      "<целое число>": {            // идентификатор игрока
        'id': <целое число>,        // идентификатор игрока
        'name': "строка",           // ник
        'hero': {                   // краткая информация о герое
          'id': <целое число>,      // идентификатор
          'name': "строка",         // имя
          'race': <целое число>,    // раса
          'gender': <целое число>,  // пол
          'level': <целое число> }, // уровень
        'clan': <целое число>|null  // идентификатор клана
      },
      …
    }

    <clans_info> = {
     "<целое число>": {     // идентификатор клана
       'id': <целое число>, // идентификатор клана
       'abbr': "строка",    // аббревиатура
       'name': "строка"},   // полное название
     …
    }

    '''

    return dext_views.AjaxOk(content=logic.place_info(context.place))


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
