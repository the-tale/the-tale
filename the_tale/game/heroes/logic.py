# coding: utf-8
import random
import datetime

from utg import words as utg_words

from dext.common.utils import s11n

from django.db import models as django_models

from the_tale.game.prototypes import TimePrototype
from the_tale.game import relations as game_relations
from the_tale.game import names

from the_tale.game.balance import constants as c
from the_tale.game.balance import formulas as f
from the_tale.game.balance import power

from the_tale.game.actions import container as actions_container
from the_tale.game.quests import container as quests_container
from the_tale.game.cards import container as cards_container

from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.map.places.storage import places_storage

from the_tale.game.companions import objects as companions_objects

from . import models
from . import objects
from . import position
from . import statistics
from . import preferences
from . import relations
from . import messages
from . import places_help_statistics
from . import pvp
from . import habilities
from . import bag
from . import conf
from . import habits


def live_query():
    return models.Hero.objects.filter(is_fast=False, is_bot=False)


def get_minimum_created_time_of_active_quests():
    created_at = models.Hero.objects.all().aggregate(django_models.Min('quest_created_time'))['quest_created_time__min']
    return created_at if created_at is not None else datetime.datetime.now()


def hero_position_from_model(hero_model):
    return position.Position(last_place_visited_turn=TimePrototype.get_current_turn_number(), # TODO: get from model
                             moved_out_place=False, # TODO: get from model
                             place_id=hero_model.pos_place_id,
                             road_id=hero_model.pos_road_id,
                             previous_place_id=hero_model.pos_previous_place_id,
                             invert_direction=hero_model.pos_invert_direction,
                             percents=hero_model.pos_percents,
                             from_x=hero_model.pos_from_x,
                             from_y=hero_model.pos_from_y,
                             to_x=hero_model.pos_to_x,
                             to_y=hero_model.pos_to_y)

def hero_statistics_from_model(hero_model):
    return statistics.Statistics(pve_deaths=hero_model.stat_pve_deaths,
                                 pve_kills=hero_model.stat_pve_kills,

                                 money_earned_from_loot=hero_model.stat_money_earned_from_loot,
                                 money_earned_from_artifacts=hero_model.stat_money_earned_from_artifacts,
                                 money_earned_from_quests=hero_model.stat_money_earned_from_quests,
                                 money_earned_from_help=hero_model.stat_money_earned_from_help,
                                 money_earned_from_habits=hero_model.stat_money_earned_from_habits,
                                 money_earned_from_companions=hero_model.stat_money_earned_from_companions,

                                 money_spend_for_heal=hero_model.stat_money_spend_for_heal,
                                 money_spend_for_artifacts=hero_model.stat_money_spend_for_artifacts,
                                 money_spend_for_sharpening=hero_model.stat_money_spend_for_sharpening,
                                 money_spend_for_useless=hero_model.stat_money_spend_for_useless,
                                 money_spend_for_impact=hero_model.stat_money_spend_for_impact,
                                 money_spend_for_experience=hero_model.stat_money_spend_for_experience,
                                 money_spend_for_repairing=hero_model.stat_money_spend_for_repairing,
                                 money_spend_for_tax=hero_model.stat_money_spend_for_tax,
                                 money_spend_for_companions=hero_model.stat_money_spend_for_companions,

                                 artifacts_had=hero_model.stat_artifacts_had,
                                 loot_had=hero_model.stat_loot_had,

                                 help_count=hero_model.stat_help_count,

                                 quests_done=hero_model.stat_quests_done,

                                 companions_count=hero_model.stat_companions_count,

                                 pvp_battles_1x1_number=hero_model.stat_pvp_battles_1x1_number,
                                 pvp_battles_1x1_victories=hero_model.stat_pvp_battles_1x1_victories,
                                 pvp_battles_1x1_draws=hero_model.stat_pvp_battles_1x1_draws,

                                 cards_used=hero_model.stat_cards_used,
                                 cards_combined=hero_model.stat_cards_combined,

                                 gifts_returned=hero_model.stat_gifts_returned)


def load_heroes_by_account_ids(account_ids):
    heroes_models = models.Hero.objects.filter(account_id__in=account_ids)
    return [load_hero(hero_model=model) for model in heroes_models]

def load_hero(hero_id=None, account_id=None, hero_model=None):

    # TODO: get values instead model
    # TODO: check that load_hero everywhere called with correct arguments
    try:
        if hero_id is not None:
            hero_model = models.Hero.objects.get(id=hero_id)
        elif account_id is not None:
            hero_model = models.Hero.objects.get(account_id=account_id)
        elif hero_model is None:
            return None
    except models.Hero.DoesNotExist:
        return None

    data = s11n.from_json(hero_model.data)

    companion_data = data.get('companion')
    companion = companions_objects.Companion.deserialize(companion_data) if companion_data else None

    return objects.Hero(id=hero_model.id,
                        account_id=hero_model.account_id,
                        health=hero_model.health,
                        level=hero_model.level,
                        experience=hero_model.experience,
                        energy=hero_model.energy,
                        energy_bonus=hero_model.energy_bonus,
                        money=hero_model.money,
                        next_spending=hero_model.next_spending,
                        habit_honor=habits.Honor(raw_value=hero_model.habit_honor),
                        habit_peacefulness=habits.Peacefulness(raw_value=hero_model.habit_peacefulness),
                        position=hero_position_from_model(hero_model),
                        statistics=hero_statistics_from_model(hero_model),
                        preferences=preferences.HeroPreferences.deserialize(data=s11n.from_json(hero_model.preferences)),
                        actions=actions_container.ActionsContainer.deserialize(s11n.from_json(hero_model.actions)),
                        companion=companion,
                        journal=messages.JournalContainer.deserialize(s11n.from_json(hero_model.messages)),
                        diary=messages.DiaryContainer.deserialize(s11n.from_json(hero_model.diary)),
                        quests=quests_container.QuestsContainer.deserialize(s11n.from_json(hero_model.quests)),
                        places_history=places_help_statistics.PlacesHelpStatistics.deserialize(s11n.from_json(hero_model.places_history)),
                        cards=cards_container.CardsContainer.deserialize(s11n.from_json(hero_model.cards)),
                        pvp=pvp.PvPData.deserialize(s11n.from_json(hero_model.pvp)),
                        abilities=habilities.AbilitiesPrototype.deserialize(s11n.from_json(hero_model.abilities)),
                        bag=bag.Bag.deserialize(s11n.from_json(hero_model.bag)),
                        equipment=bag.Equipment.deserialize(s11n.from_json(hero_model.equipment)),
                        created_at_turn=hero_model.created_at_turn,
                        saved_at_turn=hero_model.saved_at_turn,
                        saved_at=hero_model.saved_at,
                        is_bot=hero_model.is_bot,
                        is_alive=hero_model.is_alive,
                        is_fast=hero_model.is_fast,
                        gender=hero_model.gender,
                        race=hero_model.race,
                        last_energy_regeneration_at_turn=hero_model.last_energy_regeneration_at_turn,
                        might=hero_model.might,
                        ui_caching_started_at=hero_model.ui_caching_started_at,
                        active_state_end_at=hero_model.active_state_end_at,
                        premium_state_end_at=hero_model.premium_state_end_at,
                        ban_state_end_at=hero_model.ban_state_end_at,
                        last_rare_operation_at_turn=hero_model.last_rare_operation_at_turn,
                        settings_approved=hero_model.settings_approved,
                        actual_bills=s11n.from_json(hero_model.actual_bills),
                        utg_name=utg_words.Word.deserialize(data['name']))


def save_hero(hero, new=False):
    data = {'companion': hero.companion.serialize() if hero.companion else None,
            'name': hero.utg_name.serialize()}

    arguments = dict(saved_at_turn=TimePrototype.get_current_turn_number(),
                     saved_at=datetime.datetime.now(),
                     data=s11n.to_json(data),
                     bag=s11n.to_json(hero.bag.serialize()),
                     equipment=s11n.to_json(hero.equipment.serialize()),
                     abilities=s11n.to_json(hero.abilities.serialize()),
                     places_history=s11n.to_json(hero.places_history.serialize()),
                     cards=s11n.to_json(hero.cards.serialize()),
                     messages=s11n.to_json(hero.journal.serialize()),
                     diary=s11n.to_json(hero.diary.serialize()),
                     actions=s11n.to_json(hero.actions.serialize()),
                     raw_power_physic=hero.power.physic,
                     raw_power_magic=hero.power.magic,
                     quests=s11n.to_json(hero.quests.serialize()),
                     quest_created_time = hero.quests.min_quest_created_time,
                     pvp=s11n.to_json(hero.pvp.serialize()),
                     preferences=s11n.to_json(hero.preferences.serialize()),
                     stat_politics_multiplier=hero.politics_power_multiplier() if hero.can_change_all_powers() else 0,
                     actual_bills=s11n.to_json(hero.actual_bills),

                     pos_previous_place_id=hero.position.previous_place_id,
                     pos_place_id=hero.position.place_id,
                     pos_road_id=hero.position.road_id,
                     pos_percents=hero.position.percents,
                     pos_invert_direction=hero.position.invert_direction,
                     pos_from_x=hero.position.from_x,
                     pos_from_y=hero.position.from_y,
                     pos_to_x=hero.position.to_x,
                     pos_to_y=hero.position.to_y,

                     stat_pve_deaths=hero.statistics.pve_deaths,
                     stat_pve_kills=hero.statistics.pve_kills,

                     stat_money_earned_from_loot=hero.statistics.money_earned_from_loot,
                     stat_money_earned_from_artifacts=hero.statistics.money_earned_from_artifacts,
                     stat_money_earned_from_quests=hero.statistics.money_earned_from_quests,
                     stat_money_earned_from_help=hero.statistics.money_earned_from_help,
                     stat_money_earned_from_habits=hero.statistics.money_earned_from_habits,
                     stat_money_earned_from_companions=hero.statistics.money_earned_from_companions,

                     stat_money_spend_for_heal=hero.statistics.money_spend_for_heal,
                     stat_money_spend_for_artifacts=hero.statistics.money_spend_for_artifacts,
                     stat_money_spend_for_sharpening=hero.statistics.money_spend_for_sharpening,
                     stat_money_spend_for_useless=hero.statistics.money_spend_for_useless,
                     stat_money_spend_for_impact=hero.statistics.money_spend_for_impact,
                     stat_money_spend_for_experience=hero.statistics.money_spend_for_experience,
                     stat_money_spend_for_repairing=hero.statistics.money_spend_for_repairing,
                     stat_money_spend_for_tax=hero.statistics.money_spend_for_tax,
                     stat_money_spend_for_companions=hero.statistics.money_spend_for_companions,

                     stat_artifacts_had=hero.statistics.artifacts_had,
                     stat_loot_had=hero.statistics.loot_had,

                     stat_help_count=hero.statistics.help_count,

                     stat_quests_done=hero.statistics.quests_done,

                     stat_companions_count=hero.statistics.companions_count,

                     stat_pvp_battles_1x1_number=hero.statistics.pvp_battles_1x1_number,
                     stat_pvp_battles_1x1_victories=hero.statistics.pvp_battles_1x1_victories,
                     stat_pvp_battles_1x1_draws=hero.statistics.pvp_battles_1x1_draws,

                     stat_cards_used=hero.statistics.cards_used,
                     stat_cards_combined=hero.statistics.cards_combined,

                     stat_gifts_returned=hero.statistics.gifts_returned,

                     health=hero.health,
                     level=hero.level,
                     experience=hero.experience,
                     energy=hero.energy,
                     energy_bonus=hero.energy_bonus,
                     money=hero.money,
                     next_spending=hero.next_spending,
                     habit_honor=hero.habit_honor.raw_value,
                     habit_peacefulness=hero.habit_peacefulness.raw_value,
                     created_at_turn=hero.created_at_turn,
                     is_bot=hero.is_bot,
                     is_alive=hero.is_alive,
                     is_fast=hero.is_fast,
                     gender=hero.gender,
                     race=hero.race,
                     last_energy_regeneration_at_turn=hero.last_energy_regeneration_at_turn,
                     might=hero.might,
                     ui_caching_started_at=hero.ui_caching_started_at,
                     active_state_end_at=hero.active_state_end_at,
                     premium_state_end_at=hero.premium_state_end_at,
                     ban_state_end_at=hero.ban_state_end_at,
                     last_rare_operation_at_turn=hero.last_rare_operation_at_turn,
                     settings_approved=hero.settings_approved)

    if new:
        models.Hero.objects.create(id=hero.id,
                                   account_id=hero.account_id,
                                   **arguments)
    else:
        models.Hero.objects.filter(id=hero.id).update(**arguments)


    hero.journal.updated = False
    hero.actions.updated = False
    hero.preferences.updated = False

    hero.saved_at_turn = arguments['saved_at_turn']
    hero.saved_at = arguments['saved_at']


def dress_new_hero(hero):
    for equipment_slot in relations.EQUIPMENT_SLOT.records:
        if equipment_slot.default:
            hero.equipment.equip(equipment_slot, artifacts_storage.get_by_uuid(equipment_slot.default).create_artifact(level=1, power=power.Power(1, 1)))

def preferences_for_new_hero(hero):
    if hero.preferences.energy_regeneration_type is None:
        hero.preferences.set_energy_regeneration_type(hero.race.energy_regeneration, change_time=datetime.datetime.fromtimestamp(0))
    if hero.preferences.risk_level is None:
        hero.preferences.set_risk_level(relations.RISK_LEVEL.NORMAL, change_time=datetime.datetime.fromtimestamp(0))
    if hero.preferences.archetype is None:
        hero.preferences.set_archetype(game_relations.ARCHETYPE.NEUTRAL, change_time=datetime.datetime.fromtimestamp(0))
    if hero.preferences.companion_dedication is None:
        hero.preferences.set_companion_dedication(relations.COMPANION_DEDICATION.NORMAL, change_time=datetime.datetime.fromtimestamp(0))
    if hero.preferences.companion_empathy is None:
        hero.preferences.set_companion_empathy(relations.COMPANION_EMPATHY.ORDINAL, change_time=datetime.datetime.fromtimestamp(0))


def messages_for_new_hero(hero):
    hero.add_message('hero_common_diary_create', diary=True, journal=False, hero=hero)
    hero.add_message('hero_common_journal_create_1', hero=hero, turn_delta=-4)
    hero.add_message('hero_common_journal_create_2', hero=hero, turn_delta=-3)
    hero.add_message('hero_common_journal_create_3', hero=hero, turn_delta=-2)
    hero.add_message('hero_common_journal_create_4', hero=hero, turn_delta=-1)


def create_hero(account):
    from the_tale.game.relations import GENDER, RACE

    start_place = places_storage.random_place()

    race = random.choice(RACE.records)

    gender = random.choice((GENDER.MASCULINE, GENDER.FEMININE))

    current_turn_number = TimePrototype.get_current_turn_number()

    utg_name = names.generator.get_name(race, gender)

    hero_position = position.Position.create(place_id=start_place.id, road_id=None)

    hero = objects.Hero(id=account.id,
                        account_id=account.id,
                        health=f.hp_on_lvl(1),
                        level=1,
                        experience=0,
                        energy=c.ANGEL_ENERGY_MAX,
                        energy_bonus=conf.heroes_settings.START_ENERGY_BONUS,
                        money=0,
                        next_spending=relations.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT,
                        habit_honor=habits.Honor(raw_value=0),
                        habit_peacefulness=habits.Peacefulness(raw_value=0),
                        position=hero_position,
                        statistics=statistics.Statistics.create(),
                        preferences=preferences.HeroPreferences(),
                        actions=actions_container.ActionsContainer(),
                        companion=None,
                        journal=messages.JournalContainer(),
                        diary=messages.DiaryContainer(),
                        quests=quests_container.QuestsContainer(),
                        places_history=places_help_statistics.PlacesHelpStatistics(),
                        cards=cards_container.CardsContainer(),
                        pvp=pvp.PvPData(),
                        abilities=habilities.AbilitiesPrototype.create(),
                        bag=bag.Bag(),
                        equipment=bag.Equipment(),
                        created_at_turn=current_turn_number,
                        saved_at_turn=current_turn_number,
                        saved_at=None,
                        is_fast=account.is_fast,
                        is_bot=account.is_bot,
                        is_alive=True,
                        gender=gender,
                        race=race,
                        last_energy_regeneration_at_turn=TimePrototype.get_current_turn_number(),
                        might=account.might,
                        ui_caching_started_at=datetime.datetime.now(),
                        active_state_end_at=account.active_end_at,
                        premium_state_end_at=account.premium_end_at,
                        ban_state_end_at=account.ban_game_end_at,
                        last_rare_operation_at_turn=TimePrototype.get_current_turn_number(),
                        settings_approved=False,
                        actual_bills=[],
                        utg_name=utg_name)

    dress_new_hero(hero)
    preferences_for_new_hero(hero)
    messages_for_new_hero(hero)

    save_hero(hero, new=True)

    models.HeroPreferences.create(hero,
                                  energy_regeneration_type=hero.preferences.energy_regeneration_type,
                                  risk_level=relations.RISK_LEVEL.NORMAL,
                                  archetype=game_relations.ARCHETYPE.NEUTRAL,
                                  companion_dedication=relations.COMPANION_DEDICATION.NORMAL,
                                  companion_empathy=relations.COMPANION_EMPATHY.ORDINAL)

    return hero


def remove_hero(hero_id=None, account_id=None):
    if hero_id is not None:
        models.Hero.objects.filter(id=hero_id).delete()
    else:
        models.Hero.objects.filter(account_id=account_id).delete()
