# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument_with_resource
from dext.utils.decorators import debug_required

from common.utils.decorators import staff_required, login_required
from common.utils.resources import Resource
from common.utils import api

from accounts.clans.prototypes import ClanPrototype

from game.heroes.relations import EQUIPMENT_SLOT

from game.map.conf import map_settings
from game.map.storage import map_info_storage

from game.conf import game_settings
from game.pvp.prototypes import Battle1x1Prototype
from game import logic as game_logic

class GameResource(Resource):

    def initialize(self, *args, **kwargs):
        super(GameResource, self).initialize(*args, **kwargs)

    @login_required
    @handler('', method='get')
    def game_page(self):

        battle = Battle1x1Prototype.get_by_account_id(self.account.id)

        if battle and battle.state._is_PROCESSING:
            return self.redirect(reverse('game:pvp:'))

        clan = None
        if self.account.clan_id is not None:
            clan = ClanPrototype.get_by_id(self.account.clan_id)

        return self.template('game/game_page.html',
                             {'map_settings': map_settings,
                              'game_settings': game_settings,
                              'EQUIPMENT_SLOT': EQUIPMENT_SLOT,
                              'current_map_version': map_info_storage.version,
                              'clan': clan} )

    @api.handler(versions=('1.0',))
    @validate_argument_with_resource('account', Resource.validate_account_argument, 'game.info', u'неверный идентификатор аккаунта', raw=True)
    @handler('api', 'info', name='api-info', method='get')
    def api_info(self, api_version=None, account=None):
        u'''
Информация об текущем ходе и герое

- **адрес:** /game/api/info
- **http-метод:** GET
- **версии:** 1.0
- **параметры:**
    * GET: account — идентификатор аккаунта
- **возможные ошибки**: нет

формат данных в ответе:

    {
      "mode": "pve"|"pvp",        // режим героя
      "turn": {                   // информация о номере хода
        "number": <целое число>,  // номер хода
        "verbose_date": "строка", // дата для игроков (в мире Сказки)
        "verbose_time": "строка"  // время для игроков (в мире Сказки)
      },
      "map_version": "строка",    // версия актуальной карты игры
      "account": <account_info>|null,  // информация об запрашиваемом аккаунте и герое
      "enemy": <account_info>|null     // информация о противнике, если идёт pvp сражение
    }

    <account_info> = {
      "new_messages": <целое число>, // количество личных сообщений
      "id": <целое число>,           // идентификатор аккаунта
      "is_own": true|false,          // информация о собственном герое или о чужом
      "is_old": true|false,          // информация устаревшая или нет
      "hero": <hero_info>,           // информация о герое
      "in_pvp_queue": true|false     // находится ли герой в очереди на арену
    }

    <hero_info> = {
      "pvp":{                            // данные относящиеся к pvp
         "advantage": <целое число>,     // преимущество героя
         "effectiveness": <целое число>, // эффективность героя
         "probabilities": {              // вероятности успешного применения способностей
           "ice": <дробное число>,       // льда
           "blood": <дробное число>,     // крови
           "flame": <дробное число>,     // пламени
         },
         "energy": <целое число>,        // текущая энергия
         "energy_speed": <целое число>   // прирост энергии
      },

      "energy":{                      // энергия игрока
            "charges": <целое число>, // свободных зарядов
            "max": <целое число>,     // максимальное количество
            "value": <целое число>    // текущее количество
      },

      "equipment":{                // экипировка героя, словарь <идентификато слота, информация об артефакте>
        "<целое число>":{          // идентификатор слота
           "name": "строка",       // название
           "power": <целое число>, // сила
           "type": <целое число>,  // тип 0 — хлам, 1,2.. — все остальные
         }
      },

      "bag":{ // содержимое рюкзака, словарь <внутренний идентификатор предмета, описание> ()
        "<целое число>":{          // идентификатор слота
           "name": "строка",       // название
           "power": <целое число>, // сила
           "type": <целое число>,  // тип 0 — хлам, 1,2.. — все остальные
         }
      },

      "base":{                                // базовые параметры героя
        "experience": <целое число>,          // текущий опыт
        "race": <целое число>,                // раса
        "health": <целое число>,              // здоровье
        "name": "строка",                     // имя героя
        "level": <целое число>,               // уровень героя
        "gender": <целое число>,              // пол
        "experience_to_level": <целое число>, // абсолютное количество опыта до следующего уровня
        "max_health": <целое число>,          // максимальное количество здоровья
        "destiny_points": <целое число>       // сколько способностей сейчас может выбрать
      },

      "secondary":{                        // второстепенные параметры
        "max_bag_size": <целое число>,     // максимальный размер рюкзака
        "power": <целое число>,            // сила
        "move_speed": <дробное число>,     // скорость движения
        "loot_items_count": <целое число>, // количество лута в рюкзаке
        "initiative": <дробное число>      // инициатива героя
      },

      "diary":[        // список последних сообщений в денвнике
        [              // запись в дневнике
          <timestamp>, // timestamp создания сообщения
          "строка",    // текстовое описание времени в игре
          "строка",    // текст
          "строка"     // текстовое описание даты в игре
        ]
      ],

      "messages":[ // сообщения из журнала
        [              // запись в задании
          <timestamp>, // timestamp создания сообщения
          "строка",    // текстовое описание времени в игре
          "строка",    // текст
        ]
      ],

      "quests": <quests_info>|null,  // список заданий, для анонимных запросов не отдаётся

      "action":{                     // текущее действие
        "percents": <дробное число>, // процент выполнения
        "description": "строка",     // описание
        "info_link": "url"|null      // ссылка на доп. информацию
      },

      "position":{                      // позиция героя
        "invert_direction": true|false, // если идёт по дороге, то в прямом направлении или в обратном
        "place_id": <целое число>|null, // в каком городе находится, если в городе
        "road_id": <целое число>|null,  // идентификатор дороги, по которой двигается
        "coordinates":{                 // координаты, если двигается не по дороге
          "to":{                        // точка окончания движения
            "y": <целое число>|null,    // x
            "x": <целое число>|null     // y
          },
          "from":{                      // точка начала движения
            "y": <целое число>|null,    // x
            "x": <целое число>|null     // y
          }
        },
        "percents": <дробное число>     // на сколько продвинулся по дороге или между точками
      },

      "next_spending": "строка"                        // идентификатор следующей цели трат героя (impact, artifact, sharpening, useless, experience)
      "money": <целое число>,                          // количество денег у героя
      "alive": true|false,                             // жив герой или мёртв
      "id": <целое число>,                             // идентификатор
      "can_participate_in_pvp": true|false,            // может ли участвовать в pvp
      "might": <целое число>,                          // могущество игрока
      "might_crit_chance": <дробное число>,            // вероятность критического срабатывания помощи
      "can_repair_building": true|false,               // может ли чинить здания
      "saved_at_turn": <целое число>,                  // данные на какой ход предоставлены
      "saved_at": <timestamp>,                         // данные на какое время предоставлены
      "might_pvp_effectiveness_bonus": <дробное число> // бонус к эффективности в pvp от могущества
      }

примечания:

- если информация о героя устаревшая (is_old == true), то следует повторить запрос через несколько секунда (но лучше не злоупотреблять)


        '''

        if account is None and self.account.is_authenticated():
            account = self.account

        data = game_logic.form_game_info(account=account)

        return self.ok(data=data)

    @debug_required
    @staff_required()
    @handler('next-turn', method=['post'])
    def next_turn(self):

        from .workers.environment import workers_environment
        workers_environment.supervisor.cmd_next_turn()

        return self.json(status='ok')
