
import smart_imports

smart_imports.all()


class APIReference(object):

    def __init__(self, id_, name, method):
        self.id = id_
        self.name = name
        self.documentation = markdown.markdown(method.__doc__)


class TypeReference(object):

    def __init__(self, id_, name, relation, filter=lambda record: True, fields=(('значение', 'value'), ('описание', 'text'))):
        self.id = id_
        self.name = name
        self.relation = relation
        self.fields = fields
        self.filter = filter

    @utils_decorators.lazy_property
    def records(self):
        records = []
        for record in self.relation.records:
            if not self.filter(record):
                continue
            records.append([getattr(record, field_id) for field_name, field_id in self.fields])
        return records


def get_api_types():
    return [TypeReference('artifact_rarity', 'Артефакты: редкость', artifacts_relations.RARITY),
            TypeReference('artifact_type', 'Артефакты: типы', artifacts_relations.ARTIFACT_TYPE),
            TypeReference('equipment_slot', 'Артефакты: типы экипировки', heroes_relations.EQUIPMENT_SLOT),
            TypeReference('artifact_effect', 'Артефакты: эффекты', artifacts_relations.ARTIFACT_EFFECT),

            TypeReference('cards_types', 'Карты: типы', cards_types.CARD),
            TypeReference('card_rarity', 'Карты: редкость', cards_relations.RARITY),

            TypeReference('action_type', 'Герои: тип действия', actions_relations.ACTION_TYPE),

            TypeReference('places_modifiers', 'Города: специализация', places_modifiers.CITY_MODIFIERS),
            TypeReference('places_attributes', 'Города: аттрибуты', places_relations.ATTRIBUTE),

            TypeReference('actor_types', 'Задания: типы актёров', quests_relations.ACTOR_TYPE),
            TypeReference('buildings_types', 'Здания: типы', places_relations.BUILDING_TYPE),

            TypeReference('ability_type', 'Игрок: тип способности', abilities_relations.ABILITY_TYPE,
                          fields=(('значение', 'value'), ('описание', 'text'), ('атрибуты запроса', 'request_attributes'))),

            TypeReference('gender', 'Общее: пол', game_relations.GENDER),
            TypeReference('race', 'Общее: раса', game_relations.RACE),
            TypeReference('habits', 'Общее: черты', game_relations.HABIT_TYPE,
                          fields=(('значение целое', 'value'), ('значение строковое', 'verbose_value'), ('описание', 'text'))),
            TypeReference('habits', 'Общее: честь', game_relations.HABIT_HONOR_INTERVAL,
                          fields=(('значение', 'value'), ('для героя', 'text'), ('для города', 'place_text'))),
            TypeReference('habits', 'Общее: миролюбие', game_relations.HABIT_PEACEFULNESS_INTERVAL,
                          fields=(('значение', 'value'), ('для героя', 'text'), ('для города', 'place_text'))),

            TypeReference('authorisation_state', 'Прочее: состояние авторизации', third_party_relations.AUTHORISATION_STATE),
            TypeReference('game_state', 'Прочее: состояние игры', game_relations.GAME_STATE),

            TypeReference('person_profession', 'Мастер: профессия', persons_relations.PERSON_TYPE),
            TypeReference('person_social', 'Мастер: тип социальной связи', persons_relations.SOCIAL_CONNECTION_TYPE),
            TypeReference('person_personality_cosmetic', 'Мастер: косметические особенности характера', persons_relations.PERSONALITY_COSMETIC),
            TypeReference('person_personality_practival', 'Мастер: практические особенности характера', persons_relations.PERSONALITY_PRACTICAL),

            TypeReference('job_effect', 'Проекты: типы эфектов', jobs_effects.EFFECT),

            TypeReference('matchmaker_type', 'PvP: тип битвы', pvp_relations.MATCHMAKER_TYPE)]


API_TYPES = get_api_types()


class GuideResource(utils_resources.Resource):

    def initialize(self, *args, **kwargs):
        super(GuideResource, self).initialize(*args, **kwargs)

    @old_views.handler('', method='get')
    def index(self):
        return self.redirect(django_reverse('guide:game'))

    @old_views.handler('registration', method='get')
    def registration(self):
        return self.template('guide/registration.html', {'section': 'registration'})

    @old_views.handler('user-agreement', method='get')
    def user_agreement(self):
        return self.template('guide/user-agreement.html', {'section': 'user-agreement'})

    @old_views.handler('privacy-policy', method='get')
    def privacy_policy(self):
        return self.template('guide/privacy-policy.html', {'section': 'privacy-policy'})

    @old_views.handler('account-types', method='get')
    def account_types(self):
        return self.template('guide/account_types.html', {'section': 'account-types'})

    @old_views.handler('payments', method='get')
    def payments(self):
        return self.template('guide/payments.html', {'section': 'payments'})

    @old_views.handler('behavior-rules', method='get')
    def behavior_rules(self):
        return self.template('guide/behavior_rules.html', {'section': 'behavior-rules'})

    @old_views.handler('game', method='get')
    def game(self):
        return self.template('guide/game.html', {'section': 'game'})

    @old_views.handler('keepers', method='get')
    def keepers(self):
        return self.template('guide/keepers.html', {'section': 'keepers'})

    @old_views.handler('quests', method='get')
    def quests(self):
        return self.template('guide/quests.html', {'section': 'quests'})

    @old_views.handler('persons', method='get')
    def persons(self):
        return self.template('guide/persons.html', {'section': 'persons',
                                                    'persons_settings': persons_conf.settings,
                                                    'BASE_ATTRIBUTES': persons_economic.BASE_ATTRIBUTES,
                                                    'INNER_CIRCLE_SIZE': politic_power_conf.settings.PERSON_INNER_CIRCLE_SIZE,
                                                    'JOBS_EFFECTS': jobs_effects.EFFECT,
                                                    'PERSON_TYPES': sorted(persons_relations.PERSON_TYPE.records, key=lambda r: r.text),
                                                    'PERSONALITY_COSMETIC': sorted(persons_relations.PERSONALITY_COSMETIC.records, key=lambda r: r.text),
                                                    'PERSONALITY_PRACTICAL': sorted(persons_relations.PERSONALITY_PRACTICAL.records, key=lambda r: r.text)})

    @old_views.handler('cities', method='get')
    def cities(self):
        return self.template('guide/cities.html', {'section': 'cities',
                                                   'places_settings': places_conf.settings,
                                                   'ATTRIBUTES': sorted(places_relations.ATTRIBUTE.records, key=lambda modifier: modifier.text),
                                                   'MODIFIERS': sorted(places_modifiers.CITY_MODIFIERS.records, key=lambda modifier: modifier.text)})

    @old_views.handler('politics', method='get')
    def politics(self):
        return self.template('guide/politics.html', {'section': 'politics',
                                                     'bills_settings': bills_conf.settings,
                                                     'heroes_settings': heroes_conf.settings,
                                                     'BILLS_BY_ID': bills_bills.BILLS_BY_ID})

    @old_views.handler('clans', method='get')
    def clans(self):
        return self.template('guide/clans.html',
                             {'section': 'clans',
                              'clans_settings': clans_conf.settings})

    @old_views.handler('map', method='get')
    def map(self):
        return self.template('guide/map.html', {'section': 'map'})

    @old_views.handler('pvp', method='get')
    def pvp(self):
        return self.template('guide/pvp.html', {'section': 'pvp',
                                                'pvp_settings': pvp_conf.settings,
                                                'pvp_abilities': pvp_abilities})

    @old_views.handler('api', method='get')
    def api(self):
        return self.template('guide/api.html', {'section': 'api',
                                                'types': API_TYPES})

    @old_views.validate_argument('ability_type', lambda x: heroes_abilities_relations.ABILITY_TYPE(int(x)), 'guide.hero_abilities', 'Неверный формат типа способности')
    @old_views.validate_argument('activation_type', lambda x: heroes_abilities_relations.ABILITY_ACTIVATION_TYPE(int(x)), 'guide.hero_abilities', 'Неверный формат типа активации')
    @old_views.validate_argument('availability', lambda x: heroes_abilities_relations.ABILITY_AVAILABILITY(int(x)), 'guide.hero_abilities', 'Неверный формат типа доступности')
    @old_views.handler('hero-abilities', method='get')
    def hero_abilities(self, ability_type=None, activation_type=None, availability=heroes_abilities_relations.ABILITY_AVAILABILITY.FOR_ALL):

        abilities = list(heroes_abilities.ABILITIES.values())

        is_filtering = False

        if ability_type is not None:
            is_filtering = True
            abilities = [ability for ability in abilities if ability.TYPE == ability_type]

        if activation_type is not None:
            is_filtering = True
            abilities = [ability for ability in abilities if ability.ACTIVATION_TYPE == activation_type]

        if availability is not heroes_abilities_relations.ABILITY_AVAILABILITY.FOR_ALL:
            if availability is not heroes_abilities_relations.ABILITY_AVAILABILITY.FOR_ALL:
                is_filtering = True
            abilities = [ability for ability in abilities if ability.AVAILABILITY == availability]

        abilities = [ability(level=ability.MAX_LEVEL) for ability in sorted(abilities, key=lambda x: x.NAME)]

        url_builder = utils_urls.UrlBuilder(django_reverse('guide:hero-abilities'), arguments={'ability_type': ability_type.value if ability_type is not None else None,
                                                                                               'activation_type': activation_type.value if activation_type is not None else None,
                                                                                               'availability': availability.value})

        return self.template('guide/hero-abilities.html', {'section': 'hero-abilities',
                                                           'url_builder': url_builder,
                                                           'abilities': abilities,
                                                           'is_filtering': is_filtering,
                                                           'ability_type': ability_type,
                                                           'activation_type': activation_type,
                                                           'availability': availability,
                                                           'ABILITY_ACTIVATION_TYPE': heroes_abilities_relations.ABILITY_ACTIVATION_TYPE,
                                                           'ABILITY_TYPE': heroes_abilities_relations.ABILITY_TYPE,
                                                           'ABILITY_AVAILABILITY': heroes_abilities_relations.ABILITY_AVAILABILITY})

    @old_views.handler('hero-preferences', method='get')
    def hero_preferences(self):
        return self.template('guide/hero-preferences.html', {'section': 'hero-preferences',
                                                             'change_preferences_card': cards_types.CARD.CHANGE_PREFERENCE,
                                                             'PREFERENCE_TYPE': heroes_relations.PREFERENCE_TYPE})

    @old_views.handler('referrals', method='get')
    def referrals(self):
        return self.template('guide/referrals.html', {'section': 'referrals',
                                                      'account': self.account,
                                                      'accounts_settings': accounts_conf.settings,
                                                      'referral_link': utils_urls.full_url('https', 'portal:',
                                                                                           **{accounts_conf.settings.REFERRAL_URL_ARGUMENT: self.account.id if self.account else None})})

    @old_views.handler('zero-player-game', name='zpg', method='get')
    def zpg(self):
        return self.template('guide/zpg.html', {'section': 'zpg'})

    @old_views.handler('hero-habits', method='get')
    def habits(self):
        habit_cards = sorted(cards_types.HABIT_POINTS_CARDS, key=lambda x: (x.rarity.value, x.text))
        return self.template('guide/hero-habits.html', {'section': 'hero-habits',
                                                        'HABIT_TYPE': game_relations.HABIT_TYPE,
                                                        'HABIT_POINTS_CARDS': habit_cards})

    @old_views.validate_argument('habit', lambda x: game_relations.HABIT_TYPE(int(x)), 'guide.hero_habit_info', 'Неверный тип черты')
    @old_views.handler('hero-habit-info', method='get')
    def habit_info(self, habit=game_relations.HABIT_TYPE.HONOR):
        return self.template('guide/hero-habit-info.html', {'habit': habit,
                                                            'HABIT_TYPE': game_relations.HABIT_TYPE})

    @old_views.handler('press-kit', name='press-kit')
    def press_kit(self):
        return self.template('guide/press_kit.html',
                             {'section': 'press-kit',
                              'mob': random.choice(mobs_storage.mobs.get_all_mobs_for_level(level=666))})

    @old_views.handler('world')
    def world(self):
        return self.template('guide/world.html', {'section': 'world'})

    @old_views.handler('how-to-help')
    def how_to_help(self):
        return self.template('guide/how_to_help.html', {'section': 'how-to-help'})

    @old_views.handler('game-resources')
    def game_resources(self):
        return self.template('guide/game_resources.html', {'section': 'game-resources'})

    @old_views.handler('movement')
    def movement(self):
        return self.template('guide/movement.html', {'section': 'movement'})

    @old_views.handler('emissaries')
    def emissaries(self):
        return self.template('guide/emissaries.html', {'section': 'emissaries'})

    @old_views.handler('creativity-recommendations')
    def creativity_recommendations(self):
        return self.template('guide/creativity-recommendations.html', {'section': 'creativity-recommendations',
                                                                       'MINIMUM_CANON_POST': blogs_conf.settings.MINIMUM_CANON_POST,
                                                                       'FORUM_TAGS_THREAD': blogs_conf.settings.FORUM_TAGS_THREAD})
