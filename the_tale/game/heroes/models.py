# coding: utf-8
import datetime

from django.db import models

from dext.common.utils import s11n

from rels.django import RelationIntegerField

from the_tale.game.relations import GENDER, RACE

from the_tale.game import relations as game_relations

from the_tale.game.heroes import relations


class Hero(models.Model):

    MAX_NAME_LENGTH = 32

    created_at_turn = models.IntegerField(null=False, default=0)
    saved_at_turn = models.IntegerField(null=False, default=0)
    last_rare_operation_at_turn = models.IntegerField(null=False, default=0)

    saved_at = models.DateTimeField(auto_now=True)

    account = models.ForeignKey('accounts.Account', related_name='heroes', default=None, null=True, blank=True, on_delete=models.CASCADE)

    is_fast = models.BooleanField(default=True, db_index=True) # copy from account.is_fast
    is_bot = models.BooleanField(default=False)

    is_alive = models.BooleanField(default=True)

    active_state_end_at = models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))
    premium_state_end_at = models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))
    ban_state_end_at = models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))

    # time when ui caching and model saving has started
    ui_caching_started_at = models.DateTimeField(auto_now_add=True)

    #base
    gender = RelationIntegerField(relation=GENDER, relation_column='value')
    race = RelationIntegerField(relation=RACE, relation_column='value')

    level = models.IntegerField(null=False, default=1)
    experience = models.IntegerField(null=False, default=0)

    health = models.IntegerField(null=False, default=0.0)

    raw_power_magic = models.BigIntegerField(null=False, default=0) # special field for ratings
    raw_power_physic = models.BigIntegerField(null=False, default=0) # special field for ratings

    money = models.BigIntegerField(null=False, default=0)

    data = models.TextField(null=False, default='{}')

    equipment = models.TextField(null=False, default='{}')
    bag = models.TextField(null=False, default='{}')

    abilities = models.TextField(null=False, default='', blank=True)

    places_history = models.TextField(null=False, default='{}')
    cards = models.TextField(null=False, default='{}')

    messages = models.TextField(null=False, default='[]')
    diary = models.TextField(null=False, default='[]')

    actions = models.TextField(null=False, default='{}')

    quests = models.TextField(null=False, default='{}')
    quest_created_time = models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))

    settings_approved = models.BooleanField(null=False, default=True, blank=True)

    pvp = models.TextField(null=False, default='{}')

    next_spending = RelationIntegerField(relation=relations.ITEMS_OF_EXPENDITURE, relation_column='value')

    energy = models.IntegerField(null=False, default=0)
    last_energy_regeneration_at_turn = models.IntegerField(null=False, default=0)
    energy_bonus = models.BigIntegerField(default=0)

    might = models.FloatField(null=False, default=0.0)
    actual_bills = models.TextField(default='[]')

    #position
    pos_previous_place = models.ForeignKey('places.Place', related_name='+', null=True, default=None, blank=True, on_delete=models.PROTECT)
    pos_place = models.ForeignKey('places.Place', related_name='+', null=True, default=None, blank=True, on_delete=models.PROTECT)
    pos_road = models.ForeignKey('roads.Road', related_name='+', null=True, default=None, blank=True, on_delete=models.PROTECT)
    pos_percents = models.FloatField(null=True, default=None, blank=True)
    pos_invert_direction = models.NullBooleanField(default=False, null=True, blank=True)
    pos_from_x = models.IntegerField(null=True, blank=True, default=None)
    pos_from_y = models.IntegerField(null=True, blank=True, default=None)
    pos_to_x = models.IntegerField(null=True, blank=True, default=None)
    pos_to_y = models.IntegerField(null=True, blank=True, default=None)

    preferences = models.TextField(null=False, default='{}')

    habit_honor = models.FloatField(default=0)
    habit_peacefulness = models.FloatField(default=0)

    #statistics
    stat_pve_deaths = models.BigIntegerField(default=0, null=False)
    stat_pve_kills = models.BigIntegerField(default=0, null=False)

    stat_money_earned_from_loot = models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_artifacts = models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_quests = models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_help = models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_habits = models.BigIntegerField(default=0, null=False)
    stat_money_earned_from_companions = models.BigIntegerField(default=0, null=False)

    stat_money_spend_for_heal = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_artifacts = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_sharpening = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_useless = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_impact = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_experience = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_repairing = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_tax = models.BigIntegerField(default=0, null=False)
    stat_money_spend_for_companions = models.BigIntegerField(default=0, null=False)

    stat_artifacts_had = models.BigIntegerField(default=0, null=False)
    stat_loot_had = models.BigIntegerField(default=0, null=False)

    stat_help_count = models.BigIntegerField(default=0, null=False)

    stat_quests_done = models.BigIntegerField(default=0, null=False)

    stat_companions_count = models.BigIntegerField(default=0, null=False)

    stat_pvp_battles_1x1_number = models.BigIntegerField(default=0, null=False)
    stat_pvp_battles_1x1_victories = models.BigIntegerField(default=0, null=False)
    stat_pvp_battles_1x1_draws = models.BigIntegerField(default=0, null=False)

    stat_cards_used = models.BigIntegerField(default=0, null=False)
    stat_cards_combined = models.BigIntegerField(default=0, null=False)

    stat_gifts_returned = models.BigIntegerField(default=0, null=False)

    stat_politics_multiplier = models.FloatField(default=0, null=False) # for ratings


    def __unicode__(self): return u'hero[%s] — %s' % (self.id, s11n.from_json(self.data)['name']['forms'][0])


# just copy for collection statistics
class HeroPreferences(models.Model):

    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)

    energy_regeneration_type = RelationIntegerField(null=False, relation=relations.ENERGY_REGENERATION)
    mob = models.ForeignKey('mobs.MobRecord', null=True, default=None, blank=True, on_delete=models.PROTECT)
    place = models.ForeignKey('places.Place', null=True, default=None, related_name='+', blank=True, on_delete=models.PROTECT)
    friend = models.ForeignKey('persons.Person', null=True, default=None, related_name='+', blank=True, on_delete=models.PROTECT)
    enemy = models.ForeignKey('persons.Person', null=True, default=None, related_name='+', blank=True, on_delete=models.PROTECT)
    equipment_slot = RelationIntegerField(relation=relations.EQUIPMENT_SLOT, null=True, default=None, blank=True)
    risk_level = RelationIntegerField(relation=relations.RISK_LEVEL)
    favorite_item = RelationIntegerField(relation=relations.EQUIPMENT_SLOT, null=True, default=None, blank=True)
    archetype = RelationIntegerField(relation=game_relations.ARCHETYPE, null=True, default=None, blank=True)
    companion_dedication = RelationIntegerField(relation=relations.COMPANION_DEDICATION, null=True, default=None, blank=True)
    companion_empathy = RelationIntegerField(relation=relations.COMPANION_EMPATHY, null=True, default=None, blank=True)

    @classmethod
    def create(cls, hero, energy_regeneration_type, risk_level, archetype, companion_dedication, companion_empathy):
        return cls.objects.create(hero_id=hero.id,
                                  energy_regeneration_type=energy_regeneration_type,
                                  risk_level=risk_level,
                                  archetype=archetype,
                                  companion_dedication=companion_dedication,
                                  companion_empathy=companion_empathy)

    @classmethod
    def update(cls, hero_id, field, value):
        cls.objects.filter(hero_id=hero_id).update(**{field: value})
