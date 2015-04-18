# coding: utf-8

from dext.common.utils import views as dext_views

from the_tale.common.utils import views as utils_views
from the_tale.common.utils import api

from the_tale.accounts import views as accounts_views

from the_tale.game import relations as game_relations

from the_tale.game.persons import storage as persons_storage
from the_tale.game.persons import relations as persons_relations

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.map.places import storage
from the_tale.game.map.places import conf
from the_tale.game.map.places import logic

########################################
# processors definition
########################################

class PlaceProcessor(dext_views.ArgumentProcessor):

    def parse(self, context, raw_value):
        try:
            place_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format(context=context)

        place = storage.places_storage.get(place_id)

        if not place:
            self.raise_wrong_value(context=context)

        return place


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='places')
resource.add_processor(accounts_views.current_account_processor)
resource.add_processor(utils_views.fake_resource_processor)

########################################
# views
########################################

@api.Processor.handler(versions=(conf.places_settings.API_LIST_VERSION,))
@resource.handler('api', 'list', name='api-list')
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
          "position": { "x": <целое число>,    // координаты города на карте (могут меняться при изменении размера карты!)
                        "y": <целое число> },
          "size": <целое число>,               // размер города
          "specialization": <целое число>|null // идентификатор специализации, если есть (перечень идентифкаторов можно найти в описании API)
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


@api.Processor.handler(versions=(conf.places_settings.API_SHOW_VERSION,))
@PlaceProcessor.handler(error_message=u'Город не найден', url_name='place', context_name='place')
@resource.handler('#place', 'api', 'show', name='api-show')
def api_show(context):
    u'''
Подробная информация о конкретном городе

- **адрес:** /game/map/places/&lt;place&gt;/api/show
- **http-метод:** GET
- **версии:** 1.0
- **параметры:**
    * URL place — идентификатор города
- **возможные ошибки**: нет

При завершении операции возвращается следующая информация:

    {
    }
    '''

    return dext_views.AjaxOk(content=logic.place_info(context.place))


@PlaceProcessor.handler(error_message=u'Город не найден', url_name='place', context_name='place')
@resource.handler('#place', name='show')
def show(context):
    place_info = logic.place_info(context.place)
    return dext_views.Page('places/show.html',
                           content={'place_info': place_info,
                                    'RACE': game_relations.RACE,
                                    'GENDER': game_relations.GENDER,
                                    'PERSON_TYPE': persons_relations.PERSON_TYPE,
                                    'CONNECTION_TYPE': persons_relations.SOCIAL_CONNECTION_TYPE,
                                    'hero': HeroPrototype.get_by_account_id(context.account.id) if context.account else None,
                                    'persons_storage': persons_storage.persons_storage,
                                    'resource': context.resource} )
