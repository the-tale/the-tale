# coding: utf-8

import markdown

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument
from dext.utils.urls import UrlBuilder, full_url

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import lazy_property

from the_tale.game.heroes.habilities import ABILITIES, ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY
from the_tale.game.heroes.conf import heroes_settings
from the_tale.game.heroes.relations import PREFERENCE_TYPE, HABIT_TYPE

from the_tale.game.map.places.conf import places_settings
from the_tale.game.persons.conf import persons_settings
from the_tale.game.pvp.conf import pvp_settings
from the_tale.game.pvp import abilities as pvp_abilities

from the_tale.accounts.clans.conf import clans_settings
from the_tale.accounts.conf import accounts_settings

from the_tale.guide.conf import guide_settings


class APIReference(object):

    def __init__(self, id_, name, method):
        self.id = id_
        self.name = name
        self.documentation = markdown.markdown(method.__doc__)

class TypeReference(object):

    def __init__(self, id_, name, relation, filter=lambda record: True, fields=((u'значение', 'value'), (u'описание', 'text'))):
        self.id = id_
        self.name = name
        self.relation = relation
        self.fields = fields
        self.filter = filter

    @lazy_property
    def records(self):
        records = []
        for record in self.relation.records:
            if not self.filter(record):
                continue
            records.append([getattr(record, field_id) for field_name, field_id in self.fields])
        return records


def get_api_methods():
    from the_tale.portal.views import PortalResource
    from the_tale.accounts.views import AuthResource
    from the_tale.game.views import GameResource
    from the_tale.game.abilities.views import AbilitiesResource
    from the_tale.game.quests.views import QuestsResource
    return [APIReference('portal_info', u'Базовая информация', PortalResource.api_info),
            APIReference('login', u'Вход в игру', AuthResource.api_login),
            APIReference('logout', u'Выход из игры', AuthResource.api_logout),
            APIReference('game_info', u'Информация об игре/герое', GameResource.api_info),
            APIReference('game_abilities', u'Использование способности', AbilitiesResource.use),
            APIReference('game_quests', u'Выбор в задании', QuestsResource.api_choose)]


def get_api_types():
    from the_tale.game.relations import GENDER, RACE
    from the_tale.game.artifacts.relations import ARTIFACT_TYPE
    from the_tale.game.heroes.relations import EQUIPMENT_SLOT
    from the_tale.game.persons.relations import PERSON_TYPE
    from the_tale.game.abilities.relations import ABILITY_TYPE as ANGEL_ABILITY_TYPE
    from the_tale.game.actions.relations import ACTION_TYPE

    return [TypeReference('gender', u'Пол', GENDER),
            TypeReference('race', u'Раса', RACE),
            TypeReference('artifact_type', u'Тип артефакта', ARTIFACT_TYPE),
            TypeReference('equipment_slot', u'Тип экипировки', EQUIPMENT_SLOT),
            TypeReference('person_profession', u'Профессия жителя', PERSON_TYPE),
            TypeReference('ability_type', u'Тип способности игрока', ANGEL_ABILITY_TYPE,
                         fields=((u'значение', 'value'), (u'описание', 'text'), (u'атрибуты запроса', 'request_attributes'))),
            TypeReference('action_type', u'Тип действия героя', ACTION_TYPE, filter=lambda record: not record.technical),]

API_METHODS = get_api_methods()
API_TYPES = get_api_types()


class GuideResource(Resource):

    def initialize(self, *args, **kwargs):
        super(GuideResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def index(self):
        return self.redirect(reverse('guide:game'))

    @handler('registration', method='get')
    def registration(self):
        return self.template('guide/registration.html', {'section': 'registration'})

    @handler('user-agreement', method='get')
    def user_agreement(self):
        return self.template('guide/user-agreement.html', {'section': 'user-agreement'})

    @handler('account-types', method='get')
    def account_types(self):
        return self.template('guide/account_types.html', {'section': 'account-types'})

    @handler('payments', method='get')
    def payments(self):
        return self.template('guide/payments.html', {'section': 'payments'})

    @handler('behavior-rules', method='get')
    def behavior_rules(self):
        return self.template('guide/behavior_rules.html', {'section': 'behavior-rules'})

    @handler('game', method='get')
    def game(self):
        return self.template('guide/game.html', {'section': 'game'})

    @handler('keepers', method='get')
    def keepers(self):
        return self.template('guide/keepers.html', {'section': 'keepers'})

    @handler('quests', method='get')
    def quests(self):
        return self.template('guide/quests.html', {'section': 'quests'})

    @handler('persons', method='get')
    def persons(self):
        from the_tale.game.persons.prototypes import MASTERY_VERBOSE
        from the_tale.game.persons.relations import PERSON_TYPE
        return self.template('guide/persons.html', {'section': 'persons',
                                                    'persons_settings': persons_settings,
                                                    'MASTERY_LEVELS': [mastery[1] for mastery in MASTERY_VERBOSE],
                                                    'PERSON_TYPES': sorted(PERSON_TYPE.records, key=lambda r: r.text) })

    @handler('cities', method='get')
    def cities(self):
        from the_tale.game.map.places.modifiers import MODIFIERS
        from the_tale.game.map.places.prototypes import PlaceParametersDescription
        return self.template('guide/cities.html', {'section': 'cities',
                                                   'places_settings': places_settings,
                                                   'PlaceParametersDescription': PlaceParametersDescription,
                                                   'MODIFIERS': sorted(MODIFIERS.values(), key=lambda modifier: modifier.NAME) })

    @handler('politics', method='get')
    def politics(self):
        from the_tale.game.bills.conf import bills_settings
        from the_tale.game.bills.bills import BILLS_BY_ID
        return self.template('guide/politics.html', {'section': 'politics',
                                                     'bills_settings': bills_settings,
                                                     'heroes_settings': heroes_settings,
                                                     'BILLS_BY_ID': BILLS_BY_ID})

    @handler('clans', method='get')
    def clans(self):
        return self.template('guide/clans.html',
                             {'section': 'clans',
                              'clans_settings': clans_settings })

    @handler('map', method='get')
    def map(self):
        return self.template('guide/map.html', {'section': 'map'})

    @handler('pvp', method='get')
    def pvp(self):
        return self.template('guide/pvp.html', {'section': 'pvp',
                                                'pvp_settings': pvp_settings,
                                                'pvp_abilities': pvp_abilities})

    @handler('api', method='get')
    def api(self):
        return self.template('guide/api.html', {'section': 'api',
                                                'api_forum_thread':  guide_settings.API_FORUM_THREAD,
                                                'methods': API_METHODS,
                                                'types': API_TYPES})

    @validate_argument('ability_type', lambda x: ABILITY_TYPE(int(x)), 'guide.hero_abilities', u'Неверный формат типа способности')
    @validate_argument('activation_type', lambda x: ABILITY_ACTIVATION_TYPE(int(x)), 'guide.hero_abilities', u'Неверный формат типа активации')
    @validate_argument('availability', lambda x: ABILITY_AVAILABILITY(int(x)), 'guide.hero_abilities', u'Неверный формат типа доступности')
    @handler('hero-abilities', method='get')
    def hero_abilities(self, ability_type=None, activation_type=None, availability=ABILITY_AVAILABILITY.FOR_ALL):

        abilities = ABILITIES.values()

        is_filtering = False

        if ability_type is not None:
            is_filtering = True
            abilities = [ability for ability in abilities if ability.TYPE == ability_type]

        if activation_type is not None:
            is_filtering = True
            abilities = [ability for ability in abilities if ability.ACTIVATION_TYPE == activation_type]

        if availability is not ABILITY_AVAILABILITY.FOR_ALL:
            if availability is not ABILITY_AVAILABILITY.FOR_ALL:
                is_filtering = True
            abilities = [ability for ability in abilities if ability.AVAILABILITY == availability]

        abilities = [ability(level=ability.MAX_LEVEL) for ability in sorted(abilities, key=lambda x: x.NAME)]

        url_builder = UrlBuilder(reverse('guide:hero-abilities'), arguments={'ability_type': ability_type.value if ability_type is not None else None,
                                                                             'activation_type': activation_type.value if activation_type is not None else None,
                                                                             'availability': availability.value})

        return self.template('guide/hero-abilities.html', {'section': 'hero-abilities',
                                                           'url_builder': url_builder,
                                                           'abilities': abilities,
                                                           'is_filtering': is_filtering,
                                                           'ability_type': ability_type,
                                                           'activation_type': activation_type,
                                                           'availability': availability,
                                                           'ABILITY_ACTIVATION_TYPE': ABILITY_ACTIVATION_TYPE,
                                                           'ABILITY_TYPE': ABILITY_TYPE,
                                                           'ABILITY_AVAILABILITY': ABILITY_AVAILABILITY})

    @handler('hero-preferences', method='get')
    def hero_preferences(self):
        return self.template('guide/hero-preferences.html', {'section': 'hero-preferences',
                                                             'PREFERENCE_TYPE': PREFERENCE_TYPE})

    @handler('referrals', method='get')
    def referrals(self):
        return self.template('guide/referrals.html', {'section': 'referrals',
                                                      'account': self.account,
                                                      'accounts_settings': accounts_settings,
                                                      'referral_link': full_url('http', 'portal:',
                                                                                **{accounts_settings.REFERRAL_URL_ARGUMENT: self.account.id if self.account else None})})

    @handler('zero-player-game', name='zpg', method='get')
    def zpg(self):
        return self.template('guide/zpg.html', {'section': 'zpg'})

    @handler('hero-habits', method='get')
    def habits(self):
        return self.template('guide/hero-habits.html', {'section': 'hero-habits',
                                                'HABIT_TYPE': HABIT_TYPE})

    @validate_argument('habit', lambda x: HABIT_TYPE(int(x)), 'guide.hero_habit_info', u'Неверный тип черты')
    @handler('hero-habit-info', method='get')
    def habit_info(self, habit):
        return self.template('guide/hero-habit-info.html', {'habit': habit,
                                                            'HABIT_TYPE': HABIT_TYPE})
