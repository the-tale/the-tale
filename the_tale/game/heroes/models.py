# coding: utf-8
import datetime

from django.db import models

from game.angels.models import Angel

from game.game_info import RACE, RACE_CHOICES, GENDER, GENDER_CHOICES

from game.balance import constants as c

ANGEL_ENERGY_REGENERATION_TYPES_CHOICES = ( (c.ANGEL_ENERGY_REGENERATION_TYPES.PRAY, u'молитва'),
                                            (c.ANGEL_ENERGY_REGENERATION_TYPES.SACRIFICE, u'жертвоприношение'),
                                            (c.ANGEL_ENERGY_REGENERATION_TYPES.INCENSE, u'благовония'),
                                            (c.ANGEL_ENERGY_REGENERATION_TYPES.SYMBOLS, u'символы'),
                                            (c.ANGEL_ENERGY_REGENERATION_TYPES.MEDITATION, u'медитация')  )

ANGEL_ENERGY_REGENERATION_TYPES_DICT  = dict(ANGEL_ENERGY_REGENERATION_TYPES_CHOICES)

class Hero(models.Model):

    created_at_turn = models.IntegerField(null=False, default=0)

    angel = models.ForeignKey(Angel, related_name='heroes', default=None, null=True, blank=True)

    is_fast = models.BooleanField(default=True, db_index=True) # copy from account.is_fast

    alive = models.BooleanField(default=True)

    active_state_end_at = models.BigIntegerField(default=0)

    #base
    name = models.CharField(max_length=150, null=False)

    gender = models.IntegerField(null=False, default=GENDER.MASCULINE, choices=GENDER_CHOICES)

    race = models.IntegerField(choices=RACE_CHOICES, default=RACE.HUMAN)

    level = models.IntegerField(null=False, default=1)
    experience = models.FloatField(null=False, default=0)
    destiny_points = models.IntegerField(null=False, default=1)
    destiny_points_spend = models.IntegerField(null=False, default=0) # for random.seed

    health = models.FloatField(null=False, default=0.0)

    money = models.BigIntegerField(null=False, default=0)

    equipment = models.TextField(null=False, default='{}')
    bag = models.TextField(null=False, default='{}')

    abilities = models.TextField(null=False, default='[]')

    messages = models.TextField(null=False, default='[]')
    diary = models.TextField(null=False, default='[]')
    actions_descriptions = models.TextField(null=False, default='[]')

    last_action_percents = models.FloatField(null=False, default=0)

    next_spending = models.IntegerField(null=False, default=c.ITEMS_OF_EXPENDITURE.USELESS)

    #position
    pos_place = models.ForeignKey('places.Place', related_name='+', null=True, default=None, blank=True)
    pos_road = models.ForeignKey('roads.Road', related_name='+', null=True, default=None, blank=True)
    pos_percents = models.FloatField(null=True, default=None, blank=True)
    pos_invert_direction = models.NullBooleanField(default=False, null=True, blank=True)
    pos_from_x = models.IntegerField(null=True, blank=True, default=None)
    pos_from_y = models.IntegerField(null=True, blank=True, default=None)
    pos_to_x = models.IntegerField(null=True, blank=True, default=None)
    pos_to_y = models.IntegerField(null=True, blank=True, default=None)

    #character
    pref_energy_regeneration_type = models.IntegerField(null=False, default=c.ANGEL_ENERGY_REGENERATION_TYPES.PRAY, choices=ANGEL_ENERGY_REGENERATION_TYPES_CHOICES)
    pref_energy_regeneration_type_changed_at = models.DateTimeField(default=datetime.datetime(2000, 1, 1))

    pref_mob_id = models.CharField(max_length=32, null=True, default=None)
    pref_mob_changed_at = models.DateTimeField(default=datetime.datetime(2000, 1, 1))

    pref_place = models.ForeignKey('places.Place', null=True, default=None, related_name='+')
    pref_place_changed_at = models.DateTimeField(default=datetime.datetime(2000, 1, 1))

    pref_friend = models.ForeignKey('persons.Person', null=True, default=None, related_name='+')
    pref_friend_changed_at = models.DateTimeField(default=datetime.datetime(2000, 1, 1))

    pref_enemy = models.ForeignKey('persons.Person', null=True, default=None, related_name='+')
    pref_enemy_changed_at = models.DateTimeField(default=datetime.datetime(2000, 1, 1))

    #statistics
    stat_pve_deaths = models.BigIntegerField(default=0, null=False)
    stat_pve_kills = models.BigIntegerField(default=0, null=False)

    stat_money_earned_from_loot = models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_artifacts = models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_quests = models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_help = models.BigIntegerField(default=0, null=False)

    stat_money_spend_for_heal = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_artifacts = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_sharpening = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_useless = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_impact = models.BigIntegerField(default=0, null=False)

    stat_artifacts_had = models.BigIntegerField(default=0, null=False)
    stat_loot_had = models.BigIntegerField(default=0, null=False)

    stat_quests_done = models.BigIntegerField(default=0, null=False)

    @classmethod
    def get_related_query(cls):
        return cls.objects.select_related('pos_place', 'pos_road')

    def __unicode__(self):
        return u'hero[%d] - %s' % (self.id, self.name)


class CHOOSE_ABILITY_STATE:
    WAITING = 0
    PROCESSED = 1
    UNPROCESSED = 2
    RESET = 3
    ERROR = 4

CHOOSE_ABILITY_STATE_CHOICES = [(CHOOSE_ABILITY_STATE.WAITING, u'в очереди'),
                                (CHOOSE_ABILITY_STATE.PROCESSED, u'обработана'),
                                (CHOOSE_ABILITY_STATE.UNPROCESSED, u'нельзя выбрать'),
                                (CHOOSE_ABILITY_STATE.RESET, u'сброшена'),
                                (CHOOSE_ABILITY_STATE.ERROR, u'ошибка')]

class ChooseAbilityTask(models.Model):

    state = models.IntegerField(default=CHOOSE_ABILITY_STATE.WAITING, choices=CHOOSE_ABILITY_STATE_CHOICES)

    hero = models.ForeignKey(Hero,  related_name='+')

    ability_id = models.CharField(max_length=64)

    comment = models.CharField(max_length=256, blank=True, null=False, default=True)


class CHOOSE_PREFERENCES_STATE:
    WAITING = 0
    PROCESSED = 1
    TIMEOUT = 2
    RESET = 3
    ERROR = 4
    COOLDOWN = 5

CHOOSE_PREFERENCES_STATE_CHOICES = [(CHOOSE_PREFERENCES_STATE.WAITING, u'в очереди'),
                                    (CHOOSE_PREFERENCES_STATE.PROCESSED, u'обработана'),
                                    (CHOOSE_PREFERENCES_STATE.TIMEOUT, u'таймаут'),
                                    (CHOOSE_PREFERENCES_STATE.RESET, u'сброшена'),
                                    (CHOOSE_PREFERENCES_STATE.ERROR, u'ошибка'),
                                    (CHOOSE_PREFERENCES_STATE.COOLDOWN, u'заблокирована по времени') ]

class PREFERENCE_TYPE:
    MOB = 0
    PLACE = 1
    FRIEND = 2
    ENEMY = 3
    ENERGY_REGENERATION_TYPE = 4

PREFERENCE_TYPE_CHOICES = [ (PREFERENCE_TYPE.MOB, u'любимая добыча'),
                            (PREFERENCE_TYPE.PLACE, u'родной город'),
                            (PREFERENCE_TYPE.FRIEND, u'соратник'),
                            (PREFERENCE_TYPE.ENEMY, u'враг'),
                            (PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, u'религиозность')]


class ChoosePreferencesTask(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    state = models.IntegerField(default=CHOOSE_PREFERENCES_STATE.WAITING, choices=CHOOSE_PREFERENCES_STATE_CHOICES, db_index=True)

    hero = models.ForeignKey(Hero,  related_name='+')

    preference_type = models.IntegerField(choices=PREFERENCE_TYPE_CHOICES, db_index=True)
    preference_id = models.CharField(default=None, max_length=32, null=True) # id can be either number nor strong

    comment = models.CharField(max_length=256, blank=True, null=False, default=True)
