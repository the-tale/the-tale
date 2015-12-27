# coding: utf-8

from dext.common.utils import views as dext_views

from the_tale.common.utils import views as utils_views
from the_tale.common.utils import api

from the_tale.accounts import views as accounts_views

from the_tale.game import relations as game_relations

from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons import relations as persons_relations

from the_tale.game.heroes import logic as heroes_logic


from . import storage
from . import conf
from . import logic
from . import meta_relations

########################################
# processors definition
########################################

class PlaceProcessor(dext_views.ArgumentProcessor):
    def parse(self, context, raw_value):
        try:
            place_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        place = storage.places_storage.get(place_id)

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

@api.Processor(versions=(conf.places_settings.API_LIST_VERSION,))
@resource('api', 'list', name='api-list')
def api_list(context):
    u'''
Получить перечень всех городов с их основными параметрами

- **адрес:** /game/map/places/api/list
- **http-метод:** GET
- **версии:** 1.0
- **параметры:** нет
- **возможные ошибки**: нет

При завершении операции возвращается следующая информация:

    {
      "places": {                 // перечень всех городов
        "<целое число>": {        // идентификатор города: информация о нём
          "id": <целое число>,    // идентификатор города
          "name": "строка",       // название города
          "frontier": true|false, // находится ли город на фронтире
          "position": { "x": <целое число>,    // координаты города на карте
                        "y": <целое число> },  // (могут меняться при изменении размера карты!)
          "size": <целое число>,               // размер города
          "specialization": <целое число>|null // идентификатор специализации, если есть
        }
      }
    }
    '''
    data = {'places': {}}

    for place in storage.places_storage.all():
        place_data = { 'name': place.name,
                       'id': place.id,
                       'frontier': place.is_frontier,
                       'position': {'x': place.x,
                                    'y': place.y},
                       'size': place.size,
                       'specialization': place.modifier.TYPE.value if place.modifier else None}
        data['places'][place.id] = place_data

    return dext_views.AjaxOk(content=data)


@api.Processor(versions=(conf.places_settings.API_SHOW_VERSION,))
@PlaceProcessor(error_message=u'Город не найден', url_name='place', context_name='place')
@resource('#place', 'api', 'show', name='api-show')
def api_show(context):
    u'''
Подробная информация о конкретном городе

- **адрес:** /game/map/places/&lt;place&gt;/api/show
- **http-метод:** GET
- **версии:** 1.0
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

      "position": {"x": <целое число>, "y": <целое число>},  // координаты города
      "power": { "positive_bonus": <дробное число>,          // бонус к положительному влиянию
                 "negative_bonus": <дробное число> },        // бонус к отрицательному влиянию

      "persons": <persons_info>,                   // советники
      "keepers": <keepers_info>,                   // игроки, связанные с городом
      "parameters": <parameters_info>,             // параметры города
      "demographics": <demographics_info>,         // расовый состав
      "bills": <bills_info>,                       // действующие законы
      "specializations": <specializations_info>,   // специализации
      "habits": <habits_info>,                     // черты города
      "chronicle": <chronicle_info>,               // последние записи в летописи
      "accounts": <accounts_info>,                 // краткая дополнительная информация об игроках, связанных с городом
      "clans": <clans_info>                        // краткая дополнительная информация о кланах, связанных с городом
    }

    <persons_info> = [
       { "id": <целое число>,                  // идентификатор советника
         "name": "строка",                     // имя
         "gender": <целое число>,              // пол
         "race": <целое число>,                // раса
         "type": <целое число>,                // профессия
         "unfreeze_in": <дробное число>,       // количество секунда до момента, когда советник может сам покинуть город
         "building": <целое число>|null,       // идентификатор здания советника, если оно есть
         "keepers": <keepers_info>             // информация об игроках, связанных с советником
         "mastery": {"value": <дробное число>, // числовое значение мастерства советника
                     "name": "строка"},        // название уровня мастерства советника
         "power": { "percents": <дробное число>,            // доля влияния советника (от 0 до 1)
                    "positive_bonus": <дробное число>,      // бонус к положительному влиянию
                    "negative_bonus": <дробное число> },    // бонус к отрицательному влиянию
         "connections": [(<целое число>, <целое число>),…], // список социальных связей советника в виде <тип связи, идентификатор второго советника>
       },
       …
    ]

    <keepers_info> = {
      "friends": [<целое число>, …], // список идентификаторов игроков, чьи герои помогают советника / городу
      "enemies": [<целое число>, …]  // список идентификаторов игроков, чьи герои вредят советника / городу
    }

    <parameters_info> = {
        // информация обо всех параметрах города, по следующим ключам:
        // size — размер
        // economic — уровень экономики
        // politic_radius — радиус владений
        // terrain_radius — радиус изменений
        // stability — стабильность
        // production — производство
        // goods — текущие товары
        // keepers_goods — дары Хранителей
        // safety — безопасность
        // transport — транспорт
        // freedom — свобода
        // tax — пошлина
        "строка": {"value": <целое число>|<дробное число>,              // текущее значение параметра
                   "modifiers": null|[("строка", <дробное число>), …] } // если есть, список всех модификаторов параметрв в виде <название модификатора, значение>
    }

    <demographics_info> = [
      { "race": <целое число>,       // раса
        "percents": <дробное число>, // текущая доля (от 0 до 1)
        "delta": <дробное число>,    // изменение в день
        "persons": <дробное число>}, // влияние советников (от 0 до 1)
      …
    ]

    <bills_info> = [
      { "id": <целое число>,           // идентификатор закона
        "caption": "строка",           // название закона
        "properties": ["строка", …] }, // перечень описаний эффектов закона на город
      …
    ]

    <specializations_info> = {
      "current": <целое число>|null,                     // идентификатор текущей специализации
      "all": [
        {"value": <дробное число>,                       // идентификатор специализации
         "power": <дробное число>,                       // текущее значение (развитие)
         "modifiers": [("строка", <дробное число>), …] } // список всех модификаторов специализации в виде <название модификатора, значение>
         "size_modifier": <дробное число>}               // модификатор от размера города
      ]
    }

    <habits_info> = {  // информация о каждой черте города в формате "идентификатор черты": {информация о черте}
      "<целое число>": {'interval': <целое число>,             // идентификатор текущего «уровня» черты
                        'value': <дробное число>,              // текущее абсолютное значенеи черты
                        'delta': <дробное число>,              // величина изменения черты за один час
                        'positive_points': <дробное число>,    // суммарное позитивное влияние героев на черту города
                        'negative_points': <дробное число> },  // суммарное негативное влияние героев на черту города
      …
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


@PlaceProcessor(error_message=u'Город не найден', url_name='place', context_name='place')
@resource('#place', name='show')
def show(context):
    place_info = logic.place_info(context.place)
    return dext_views.Page('places/show.html',
                           content={'place_info': place_info,
                                    'place_meta_object': meta_relations.Place.create_from_object(context.place),
                                    'RACE': game_relations.RACE,
                                    'GENDER': game_relations.GENDER,
                                    'PERSON_TYPE': persons_relations.PERSON_TYPE,
                                    'CONNECTION_TYPE': persons_relations.SOCIAL_CONNECTION_TYPE,
                                    'hero': heroes_logic.load_hero(account_id=context.account.id) if context.account else None,
                                    'persons_storage': persons_storage.persons_storage,
                                    'resource': context.resource} )
