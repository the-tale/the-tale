# coding: utf-8

from dext.common.utils import views as dext_views
from dext.common.utils.urls import url

from the_tale.amqp_environment import environment

from the_tale.common.utils import api
from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views
from the_tale.accounts.clans.prototypes import ClanPrototype

from the_tale.game.heroes import views as heroes_views
from the_tale.game.heroes.relations import EQUIPMENT_SLOT

from the_tale.game.map.conf import map_settings
from the_tale.game.map.storage import map_info_storage

from the_tale.game.conf import game_settings
from the_tale.game.pvp.prototypes import Battle1x1Prototype
from the_tale.game import logic as game_logic

from the_tale.game.cards.effects import EFFECTS

########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='game')
resource.add_processor(accounts_views.current_account_processor)
resource.add_processor(utils_views.fake_resource_processor)
resource.add_processor(heroes_views.current_hero_processor)

########################################
# views
########################################

@accounts_views.LoginRequiredProcessor.handler()
@resource.handler('')
def game_page(context):

    battle = Battle1x1Prototype.get_by_account_id(context.account.id)

    if battle and battle.state.is_PROCESSING:
        return dext_views.Redirect(url('game:pvp:'))

    clan = None
    if context.account.clan_id is not None:
        clan = ClanPrototype.get_by_id(context.account.clan_id)

    cards = sorted(EFFECTS.values(), key=lambda x: (x.TYPE.rarity.value, x.TYPE.text))

    return dext_views.Page('game/game_page.html',
                           content={'map_settings': map_settings,
                                    'game_settings': game_settings,
                                    'EQUIPMENT_SLOT': EQUIPMENT_SLOT,
                                    'current_map_version': map_info_storage.version,
                                    'clan': clan,
                                    'CARDS': cards,
                                    'resource': context.resource,
                                    'hero': context.account_hero} )

@api.Processor.handler(versions=(game_settings.INFO_API_VERSION, '1.1', '1.0'))
@dext_views.IntsArgumentProcessor.handler(error_message=u'Неверный формат номера хода', get_name='client_turns', context_name='client_turns', default_value=None)
@accounts_views.AccountProcessor.handler(error_message=u'Запрашиваемый Вами аккаунт не найден', get_name='account', context_name='requested_account', default_value=None)
@resource.handler('api', 'info', name='api-info')
def api_info(context):
    u'''
Информация о текущем ходе и герое

- **адрес:** /game/api/info
- **http-метод:** GET
- **версии:** 1.2
- **параметры:**
    * GET: account — идентификатор аккаунта
    * GET: client_turns — номера ходов, по отношению к которым можно вернуть сокращённую информацию о герое (только изменённые с этого времени поля).
- **возможные ошибки**: нет

Если параметр account не будет указан, то вернётся информация об игре текущего пользователя, а на запрос от неавторизованного пользователя — общая информация об игре (без информации об аккаунте и герое).

Часть информации в ответе является личной и доступна только залогиненному игроку, для остальных на её месте будет валидная с точки зрения формата заглушка. Такая информация обозначена следующим образом: **[личная информация]**.

Полный ответ имеет большой размер, поэтому реализован следующий механизм его сжатия:

- в параметре client_turns можно передать список номеров ходов (через запятую), для которых на клиенте есть полная информация;
- если сервер сможет, в ответе он вернёт только изменившуюся информацию о герое;
- сокращению подвергается только информация в &lt;hero_info&gt;;
- сокращение происходит удалением неизменившихся полей <hero_info> (только на верхнем уровне, без рекурсии);
- чтобы получить полную информацию, скопируйте недостаующие поля из закэшированной на стороне клиента информации для хода, указанного в .account.hero.patch_turn;
- сервер не гарантирует, что вернёт сокращённую информацию;
- сервер может вернуть патч для любого из переданных в client_turns ходов;
- имеет смысл в параметре client_turns передавать последние 2-3 хода;
- обратите внимание, сжатие ответа применяется и к информации о противнике в PvP! Поэтому первый запрос при PvP всегда должен требовать полную информацию.

Формат данных в ответе:

    {
      "mode": "pve"|"pvp",             // режим героя
      "turn": {                        // информация о номере хода
        "number": <целое число>,       // номер хода
        "verbose_date": "строка",      // дата для игроков (в мире Сказки)
        "verbose_time": "строка"       // время для игроков (в мире Сказки)
      },
      "game_state": <целое число>,     // состояние игры (остановлена/запущена, см. в описании API)
      "map_version": "строка",         // версия актуальной карты игры
      "account": <account_info>|null,  // информация о запрашиваемом аккаунте и герое
      "enemy": <account_info>|null     // информация о противнике, если идёт pvp сражение
    }

    <account_info> = {
      "new_messages": <целое число>, // количество личных сообщений
      "id": <целое число>,           // идентификатор аккаунта
      "last_visit": <timestamp>,     // примерное время последнего посещения игры
      "is_own": true|false,          // информация о собственном герое или о чужом
      "is_old": true|false,          // информация устаревшая или нет
      "hero": <hero_info>,           // информация о герое
      "in_pvp_queue": true|false     // находится ли герой в очереди на арену
    }

    <hero_info> = {
      "patch_turn": null|<целое число>,  // номер хода, для которого возвращается патч или null, если информация полная
      "order": <целое число>,            // порядковый номер информации о герое, отданной на этом ходу, чем больше, тем более актуальна информация
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

      "energy":{                      // энергия игрока [личная информация]
            "bonus": <целое число>,   // дополнительная энергия
            "max": <целое число>,     // максимальное количество
            "value": <целое число>,   // текущее количество
            "discount": <целое число> // скидка энергии при её трате (например, от использования артефактов)
      },

      "equipment":{                      // экипировка героя, словарь <идентификатор типа экипировки, информация об артефакте>
        "<целое число>": <artifact_info> // идентификатор типа экипировки: информация об артефакте
      },

      "cards":{                          // карты судьбы [личная информация]
        "cards": [                       // список карт
          <card_info>                    // информация о карте
        ],
        "help_count": <целое число>,     // сколько помощи накоплено для получения новой карты
        "help_barrier": <целое число>    // сколько всего помощи надо накопить для новой карты
      },

      "companion": <companion_info>|null,// информация о спутнике

      "bag":{                            // содержимое рюкзака, словарь <внутренний идентификатор предмета, описание> ()
        "<целое число>": <artifact_info> // идентификатор слота: информация об артефакте
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
        "money": <целое число>,               // количество денег у героя
        "alive": true|false,                  // жив герой или мёртв
      },

      "secondary":{                              // второстепенные параметры
        "max_bag_size": <целое число>,           // максимальный размер рюкзака
        "power": [<целое число>, <целое число>], // физическая сила, магическая сила
        "move_speed": <дробное число>,           // скорость движения
        "loot_items_count": <целое число>,       // количество лута в рюкзаке
        "initiative": <дробное число>            // инициатива героя
      },

      "diary":[        // список последних сообщений в дневнике
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

      "habits": { // черты
        "строка": {              // идентификатор черты
          "verbose": "строка",   // текущее текстовое значение черты для игрока (название характера)
          "raw": <дробное число> // текущее числовое значение черты
        }
      },

      "quests": {     // информация о заданиях
        "quests": [   // список глобальных заданий
          {
            "line": [ // список «базовых» заданий (цепочка последовательных заданий)
               {
                 "type": "строка",            // тип задания
                 "uid":  "строка",            // уникальный идентификатор задания
                 "name": "строка",            // название задания
                 "action": "строка",          // описание текущего действия героя в задании
                 "choice": "строка"|null,     // текущий выбор героя в задании
                 "choice_alternatives": [     // альтернативные выборы
                   [
                     "строка",                // уникальный идентификатор выбора
                     "строка"                 // текстовое описание выбора
                   ]
                 ],
                 "experience": <целое число>, // количество опыта за задание
                 "power": <целое число>,      // количество влияния за задание
                 "actors": [                  // список «актёров», участвующих в задании
                   [
                     "строка",                // название актёра
                     <целое число>",                // тип актёра (список типов приведён в описании API)
                     <quest_actor_info>       // данные, специфичные для конкретного типа актёра
                   ]
                 ]
               }
            ]
          }
        ]
      },

      "action":{                     // текущее действие
        "percents": <дробное число>, // процент выполнения
        "description": "строка",     // описание
        "info_link": "url"|null      // ссылка на доп. информацию
        "type": <целое число>        // идентификатор типа действия
      },

      "position":{                      // позиция героя на клеточной карте
        "x": <дробное число>,           // координата x
        "y": <дробное число>,           // координата y
        "dx": <дробное число>,          // направление взгляда по x
        "dy": <дробное число>,          // направленеи взгляда по y
      },

      "permissions": {                        // права на выполнение различных операций [личная информация]
        "can_participate_in_pvp": true|false, // может ли участвовать в pvp
        "can_repair_building": true|false,    // может ли чинить здания
      },

      "might": {                                   // могущество игрока
        "value": <дробное число>,                  // величина
        "crit_chance": <дробное число>,            // вероятность критического срабатывания помощи
        "pvp_effectiveness_bonus": <дробное число> // бонус к эффективности в pvp от могущества
      },

      "id": <целое число>,                             // идентификатор
      "actual_on_turn": <целое число>,                 // данные на какой ход предоставлены

      "sprite": <целое число>  // идентификатор спрайта, которым отображается герой
      }

    <quest_actor_info> = <quest_actor_place_info>|<quest_actor_person_info>|<quest_actor_spending_info>

    <quest_actor_place_info> = { // информация о городе
      "id": <целое числое>,      // идентификатор
      "name": "строка"           // название города
    }

    <quest_actor_person_info> = {     // информация о жителе города
        "id": <целое числое>          // идентификатор
        "name": "строка",             // имя
        "race": <целое числое>,       // раса
        "gender": <целое числое>,     // пол
        "profession": <целое числое>, // профессия
        "mastery_verbose": "строка",  // профессия
        "place": <целое числое>       // идентификатор города
    }

    <quest_actor_spending_info> = { // информация о целях накопления
      "goal": "строка"              // описание цели накопления
    }

    <artifact_info> = {                              // информация об артефакте
        "name": "строка",                            // название
        "power": [<целое число>, <целое число>],     // сила [физическая, магическая]
        "type": <целое число>,                       // тип
        "integrity": [<целое число>, <целое число>], // целостность [текущая, максимальная]
        "rarity": <целое число>,                     // редкость
        "effect": <целое число>,                     // тип эффекта на артефакте
        "special_effect": <целое число>,             // тип особого свойства артефакта (эффекта, который действует независимо от редкости)
        "preference_rating": <дробное число>,        // «полезность» артефакта с точки зрения героя
        "equipped": true|false,                      // может ли быть экипирован
        "id": <целое число>                          // уникальный идентификатор рода артефакта
    }

    <card_info> = {                              // информация о карте в колоде игрока
        "name": "строка",                        // название
        "type": <целое число>,                   // тип
        "rarity": <целое число>,                 // редкость карты
        "uid": <целое число>,                    // уникальный идентификатор в колоде игрока
        "auction": true|false                    // может быть продана на рынке
    }

    <companion_info> = {                         // информация о спутнике героя
        "type": <целое число>,                   // тип спутника
        "name": "строка",                        // название/имя спутника
        "health": <целое число>,                 // текущее здоровье
        "max_health": <целое число>,             // максимальное здоровье
        "experience": <целое число>,             // текущий опыт слаженности
        "experience_to_level": <целое число>,    // опыта до следующего уровня слаженности
        "coherence": <целое число>,              // текущая слаженность
        "real_coherence": <целое число>          // полная слаженность (без учёта ограничений на максимум слаженности)
    }

примечания:

- если информация о герое устаревшая (is_old == true), то следует повторить запрос через несколько секунд (но лучше не злоупотреблять)

    '''
    account = context.requested_account

    if account is None and context.account.is_authenticated():
        account = context.account

    data = game_logic.form_game_info(account=account,
                                     is_own=False if account is None else (context.account.id == account.id),
                                     client_turns=context.client_turns)

    if context.api_version in ('1.1', '1.0'):
        data = game_logic.game_info_from_1_2_to_1_1(data)

    if context.api_version == '1.0':
        data = game_logic.game_info_from_1_1_to_1_0(data)

    return dext_views.AjaxOk(content=data)


@dext_views.DebugProcessor.handler(required=True)
@accounts_views.LoginRequiredProcessor.handler()
@accounts_views.SuperuserProcessor.handler(required=True)
@resource.handler('next-turn', method='POST')
def next_turn(context):
    environment.workers.supervisor.cmd_next_turn()
    return dext_views.AjaxOk()
