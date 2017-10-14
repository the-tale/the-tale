# coding: utf-8

from dext.common.utils import views as dext_views

from the_tale.common.utils import views as utils_views
from the_tale.common.utils import api

from the_tale.accounts import views as accounts_views

from the_tale.game.heroes import logic as heroes_logic
from the_tale.game.chronicle import prototypes as chronicle_prototypes

from the_tale.game import relations as game_relations
from the_tale.game import short_info as game_short_info



from . import storage
from . import conf
from . import meta_relations
from . import info

########################################
# processors definition
########################################

class PlaceProcessor(dext_views.ArgumentProcessor):
    def parse(self, context, raw_value):
        try:
            place_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        place = storage.places.get(place_id)

        if not place:
            self.raise_wrong_value()

        return place


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='places')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())

########################################
# views
########################################

@api.Processor(versions=(conf.settings.API_LIST_VERSION,))
@resource('api', 'list', name='api-list')
def api_list(context):
    '''
Получить перечень всех городов с их основными параметрами

- **адрес:** /game/places/api/list
- **http-метод:** GET
- **версии:** 1.1
- **параметры:** нет
- **возможные ошибки**: нет

При завершении операции возвращается следующая информация:

    {
      "places": {                 // перечень всех городов
        "<целое число>": {        // идентификатор города: информация о нём
          "id": <целое число>,    // идентификатор города
          "name": "строка",       // название города
          "frontier": true|false, // находится ли город на фронтире
          "position": { "x": <целое число>,   // координаты города на карте
                        "y": <целое число> }, // (могут меняться при изменении размера карты!)
          "size": <целое число>,              // размер города
          "specialization": <целое число>     // идентификатор специализации
        }
      }
    }
    '''
    data = {'places': {}}

    for place in storage.places.all():
        place_data = { 'name': place.name,
                       'id': place.id,
                       'frontier': place.is_frontier,
                       'position': {'x': place.x,
                                    'y': place.y},
                       'size': place.attrs.size,
                       'specialization': place._modifier.value}
        data['places'][place.id] = place_data

    return dext_views.AjaxOk(content=data)


@api.Processor(versions=(conf.settings.API_SHOW_VERSION))
@PlaceProcessor(error_message='Город не найден', url_name='place', context_name='place')
@resource('#place', 'api', 'show', name='api-show')
def api_show(context):
    '''
Подробная информация о конкретном городе

- **адрес:** /game/places/&lt;place&gt;/api/show
- **http-метод:** GET
- **версии:** 2.0
- **параметры:**
    * URL place — идентификатор города
- **возможные ошибки**: нет

**Это экспериментальный метод, при появлении новой версии не гарантируется работоспособность предыдущей!**

При завершении операции возвращается следующая информация:

    {
      "id": <целое число>,        // идентификатор города
      "name": "строка",           // название города
      "frontier": true|false,     // является ли город фронтиром
      "new_for": <timestamp>,     // время, до которого город считается новым
      "updated_at": <timestamp>,  // время последнего обновления информации
      "description": "строка",    // описание города

      "position": {"x": <целое число>, "y": <целое число>},   // координаты города

      "politic_power": <politic_power>,     // политическое влияние города
      "persons": <persons_info>,            // Мастера
      "attributes": <attributes_info>,      // все параметры города
      "demographics": <demographics_info>,  // расовый состав
      "bills": <bills_info>,                // действующие записи в книге судеб
      "habits": <habits_info>,              // черты города
      "chronicle": <chronicle_info>,        // последние записи в летописи
      "job": <job_info>,                    // информация о проекте
      "accounts": <accounts_info>,          // краткая дополнительная информация об игроках, связанных с городом
      "clans": <clans_info>                 // краткая дополнительная информация о кланах, связанных с городом
    }

    <politic_power> = {
        "power": {
            "inner": { "value": <дробное число>,            // суммарное влияние ближнего круга
                       "fraction": <дробное число> },       // доля среди остальных городов
                                                            // (Фронтир и Ядро считаются отдельно)

            "outer": { "value": <дробное число>,            // суммарное влияние «толпы»
                       "fraction": <дробное число> },       // доля среди остальных городов
                                                            // (Фронтир и Ядро считаются отдельно)

            "fraction": <дробное число>                     // доля общего влияния среди остальных городов
                                                            //(Фронтир и Ядро считаются отдельно)
        },
        "heroes": {                                         // влияющие на город герои (ближний круг и кандидаты в него)
            "positive": {"<целое число>": <дробное число>}, // позитивное влияние <идентификатор героя, принесённое влияние>
            "negative": {"<целое число>": <дробное число>}, // негативное влияние <идентификатор героя, принесённое влияние>
        }
    }

    <persons_info> = [
       { "id": <целое число>,                       // идентификатор Мастера
         "name": "строка",                          // имя
         "gender": <целое число>,                   // пол
         "race": <целое число>,                     // раса
         "type": <целое число>,                     // профессия
         "next_move_available_in": <дробное число>, // количество секунда до момента, когда Мастер может переехать в другой город
         "politic_power_fraction": <дробное число>, // доля влияния в городе
         "building": {                              // информация о здании, если оно есть
             "id": <целое число>,                   // идентификатор
             "position": {"x": <целое число>,       // позиция
                          "y": <целое число>},      //
             "type": <целое число>,                 // тип, значения перечислены на странице API
             "integrity": <дробное число>,          // целостность здания от 0.0 до 1.0
             "created_at_turn": <целое число>,      // номер хода на котором создано
         } | null,
         "personality": {                           // характер
             "cosmetic": <целое число>,             // идентификатор косметической особенности характера
             "practical": <целое число>             // идентификатор практической особенности характера
         }
       },
       …
    ]

    <attributes_info> = {                                // информация о всех параметрах города
        "effects": [                                     // эффекты, действующие на город
            { "name": "<строка>",                        // название эффекта
              "attribute": <целое число>,                // на какой аттрибут влияет
              "value": <целое>|<дробное>|"<строка>"|null // значение, null, если значение комплексное и пока не сериализуется в API
            },
            ...
        ],
        "attributes": [                                  // итоговые значения аттрибутов
            { "id": <целое число>,                       // идентификатор аттрибута
              "value": <целое>|<дробное>|"<строка>"|null // значение, null, если значение комплексное и пока не сериализуется в API
            }
        ]
    }

    <demographics_info> = [
      { "race": <целое число>,       // раса
        "percents": <дробное число>, // текущая доля (от 0 до 1)
        "delta": <дробное число>,    // изменение в день
        "persons": <дробное число>}, // влияние Мастеров (от 0 до 1)
      …
    ]

    <bills_info> = [
      { "id": <целое число>,           // идентификатор записи
        "caption": "строка",           // название записи
        "properties": ["строка", …] }, // перечень описаний эффектов
      …
    ]

    <habits_info> = {  // информация о каждой черте города в формате "идентификатор черты": {информация о черте}
      "<целое число>": {"interval": <целое число>,             // идентификатор текущего «уровня» черты
                        "value": <дробное число>,              // текущее абсолютное значенеи черты
                        "delta": <дробное число>,              // величина изменения черты за один час
                        "positive_points": <дробное число>,    // суммарное позитивное влияние героев на черту города
                        "negative_points": <дробное число> },  // суммарное негативное влияние героев на черту города
      …
    }

    <chronicle_info> = [("строка", "строка", "строка"), …] // последние записи из летописи о городе в формате ("короткая дата", "длинная дата", "текст")

    <accounts_info> = {
      "<целое число>": {            // идентификатор игрока
        "id": <целое число>,        // идентификатор игрока
        "name": "строка",           // ник
        "hero": {                   // краткая информация о герое
          "id": <целое число>,      // идентификатор
          "name": "строка",         // имя
          "race": <целое число>,    // раса
          "gender": <целое число>,  // пол
          "level": <целое число> }, // уровень
        "clan": <целое число>|null  // идентификатор клана
      },
      …
    }

    <clans_info> = {
     "<целое число>": {     // идентификатор клана
       "id": <целое число>, // идентификатор клана
       "abbr": "строка",    // аббревиатура
       "name": "строка"},   // полное название
     …
    }

    <job_info> = {
      "name": "строка",                 // название проекта
      "effect": <целое число>,          // тип эффекта по завершению проекта
      "positive_power": <целое число>,  // накопленное положительное влияние
      "negative_power": <целое число>,  // накопленное отрицательное влияние
      "power_required": <целое число>   // требуемое влияние
    }

    '''

    return dext_views.AjaxOk(content=info.place_info(context.place, full_building_info=context.api_version!='2.0'))


@PlaceProcessor(error_message='Город не найден', url_name='place', context_name='place')
@resource('#place', name='show')
def show(context):
    accounts_short_infos = game_short_info.get_accounts_accounts_info(list(context.place.politic_power.inner_accounts_ids()))

    return dext_views.Page('places/show.html',
                           content={'place': context.place,
                                    'place_bills': info.place_info_bills(context.place),
                                    'place_chronicle': chronicle_prototypes.chronicle_info(context.place, conf.settings.CHRONICLE_RECORDS_NUMBER),
                                    'accounts_short_infos': accounts_short_infos,
                                    'HABIT_TYPE': game_relations.HABIT_TYPE,
                                    'place_meta_object': meta_relations.Place.create_from_object(context.place),
                                    'hero': heroes_logic.load_hero(account_id=context.account.id) if context.account else None,
                                    'resource': context.resource} )
