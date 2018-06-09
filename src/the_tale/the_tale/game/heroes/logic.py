
import random
import datetime

from utg import words as utg_words

from django.db import models as django_models

from dext.common.utils import s11n

from tt_logic.beings import relations as beings_relations

from the_tale.game import turn
from the_tale.game import relations as game_relations
from the_tale.game import names

from the_tale.game.balance import formulas as f
from the_tale.game.balance import power

from the_tale.game.actions import container as actions_container
from the_tale.game.quests import container as quests_container


from the_tale.game.artifacts import storage as artifacts_storage
from the_tale.game.places import storage as places_storage

from the_tale.game.companions import objects as companions_objects

from . import models
from . import objects
from . import position
from . import statistics
from . import preferences
from . import relations
from . import messages
from . import habilities
from . import bag
from . import habits


def live_query():
    return models.Hero.objects.filter(is_fast=False, is_bot=False)


def get_minimum_created_time_of_active_quests():
    created_at = models.Hero.objects.all().aggregate(django_models.Min('quest_created_time'))['quest_created_time__min']
    return created_at if created_at is not None else datetime.datetime.now()


def hero_position_from_model(hero_model):
    return position.Position(last_place_visited_turn=turn.number(), # TODO: get from model
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
                                 money_earned_from_masters=hero_model.stat_money_earned_from_masters,

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

    data = hero_model.data

    companion_data = data.get('companion')
    companion = companions_objects.Companion.deserialize(companion_data) if companion_data else None

    return objects.Hero(id=hero_model.id,
                        account_id=hero_model.account_id,
                        health=hero_model.health,
                        level=hero_model.level,
                        experience=hero_model.experience,
                        money=hero_model.money,
                        next_spending=hero_model.next_spending,
                        habit_honor=habits.Honor(raw_value=hero_model.habit_honor),
                        habit_peacefulness=habits.Peacefulness(raw_value=hero_model.habit_peacefulness),
                        position=hero_position_from_model(hero_model),
                        statistics=hero_statistics_from_model(hero_model),
                        preferences=preferences.HeroPreferences.deserialize(data=s11n.from_json(hero_model.preferences)),
                        actions=actions_container.ActionsContainer.deserialize(s11n.from_json(hero_model.actions)),
                        companion=companion,
                        journal=messages.JournalContainer(),  # we are not storrings journal in database, since messages in it replaced very fast
                        quests=quests_container.QuestsContainer.deserialize(data.get('quests', {})),
                        abilities=habilities.AbilitiesPrototype.deserialize(s11n.from_json(hero_model.abilities)),
                        bag=bag.Bag.deserialize(data['bag']),
                        equipment=bag.Equipment.deserialize(data['equipment']),
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
                        actual_bills=data['actual_bills'],
                        upbringing=beings_relations.UPBRINGING(data.get('upbringing', beings_relations.UPBRINGING.PHILISTINE.value)),
                        death_age=beings_relations.AGE(data.get('death_age', beings_relations.AGE.MATURE.value)),
                        first_death=beings_relations.FIRST_DEATH(data.get('first_death', beings_relations.FIRST_DEATH.FROM_THE_MONSTER_FANGS.value)),
                        utg_name=utg_words.Word.deserialize(data['name']))


def save_hero(hero, new=False):
    data = {'companion': hero.companion.serialize() if hero.companion else None,
            'name': hero.utg_name.serialize(),
            'quests': hero.quests.serialize(),
            'equipment': hero.equipment.serialize(),
            'bag': hero.bag.serialize(),
            'actual_bills': hero.actual_bills,
            'death_age': hero.death_age.value,
            'upbringing': hero.upbringing.value,
            'first_death': hero.first_death.value}

    arguments = dict(saved_at_turn=turn.number(),
                     saved_at=datetime.datetime.now(),
                     data=data,
                     abilities=s11n.to_json(hero.abilities.serialize()),
                     actions=s11n.to_json(hero.actions.serialize()),
                     raw_power_physic=hero.power.physic,
                     raw_power_magic=hero.power.magic,
                     quest_created_time=hero.quests.min_quest_created_time,
                     preferences=s11n.to_json(hero.preferences.serialize()),
                     stat_politics_multiplier=hero.politics_power_multiplier() if hero.can_change_all_powers() else 0,

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
                     stat_money_earned_from_masters=hero.statistics.money_earned_from_masters,

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

    hero.saved_at_turn = arguments['saved_at_turn']
    hero.saved_at = arguments['saved_at']


def dress_new_hero(hero):
    for equipment_slot in relations.EQUIPMENT_SLOT.records:
        if equipment_slot.default:
            hero.equipment.equip(equipment_slot, artifacts_storage.artifacts.get_by_uuid(equipment_slot.default).create_artifact(level=1, power=power.Power(1, 1)))


def preferences_for_new_hero(hero):
    if hero.preferences.energy_regeneration_type is None:
        hero.preferences.set(relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, hero.race.energy_regeneration)
    if hero.preferences.risk_level is None:
        hero.preferences.set(relations.PREFERENCE_TYPE.RISK_LEVEL, relations.RISK_LEVEL.NORMAL)
    if hero.preferences.archetype is None:
        hero.preferences.set(relations.PREFERENCE_TYPE.ARCHETYPE, game_relations.ARCHETYPE.NEUTRAL)
    if hero.preferences.companion_dedication is None:
        hero.preferences.set(relations.PREFERENCE_TYPE.COMPANION_DEDICATION, relations.COMPANION_DEDICATION.NORMAL)
    if hero.preferences.companion_empathy is None:
        hero.preferences.set(relations.PREFERENCE_TYPE.COMPANION_EMPATHY, relations.COMPANION_EMPATHY.ORDINAL)


def cards_for_new_hero(hero):
    from the_tale.game.cards import tt_api
    from the_tale.game.cards import cards

    tt_api.change_cards(hero.account_id,
                        operation_type='new-hero-gift',
                        to_add=[cards.CARD.CHANGE_HERO_SPENDINGS.effect.create_card(available_for_auction=False,
                                                                                    type=cards.CARD.CHANGE_HERO_SPENDINGS,
                                                                                    item=relations.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT),
                                cards.CARD.HEAL_COMPANION_COMMON.effect.create_card(available_for_auction=False,
                                                                                    type=cards.CARD.HEAL_COMPANION_COMMON),
                                cards.CARD.ADD_EXPERIENCE_COMMON.effect.create_card(available_for_auction=False,
                                                                                    type=cards.CARD.ADD_EXPERIENCE_COMMON),
                                cards.CARD.CHANGE_ABILITIES_CHOICES.effect.create_card(available_for_auction=False,
                                                                                       type=cards.CARD.CHANGE_ABILITIES_CHOICES),
                                cards.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                                type=cards.CARD.CHANGE_PREFERENCE,
                                                                                preference=relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE),
                                cards.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                                type=cards.CARD.CHANGE_PREFERENCE,
                                                                                preference=relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE),
                                cards.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                                type=cards.CARD.CHANGE_PREFERENCE,
                                                                                preference=relations.PREFERENCE_TYPE.PLACE),
                                cards.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                                type=cards.CARD.CHANGE_PREFERENCE,
                                                                                preference=relations.PREFERENCE_TYPE.ARCHETYPE),
                                cards.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                                type=cards.CARD.CHANGE_PREFERENCE,
                                                                                preference=relations.PREFERENCE_TYPE.FRIEND),
                                cards.CARD.ADD_BONUS_ENERGY_RARE.effect.create_card(available_for_auction=False,
                                                                                type=cards.CARD.ADD_BONUS_ENERGY_RARE)])


def create_hero(account, full_create=True):
    from the_tale.game.relations import GENDER, RACE

    start_place = places_storage.places.random_place()

    race = random.choice(RACE.records)

    gender = random.choice((GENDER.MALE, GENDER.FEMALE))

    current_turn_number = turn.number()

    utg_name = names.generator().get_name(race, gender)

    hero_position = position.Position.create(place_id=start_place.id, road_id=None)

    hero = objects.Hero(id=account.id,
                        account_id=account.id,
                        health=f.hp_on_lvl(1),
                        level=1,
                        experience=0,
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
                        quests=quests_container.QuestsContainer(),
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
                        last_energy_regeneration_at_turn=turn.number(),
                        might=account.might,
                        ui_caching_started_at=datetime.datetime.now(),
                        active_state_end_at=account.active_end_at,
                        premium_state_end_at=account.premium_end_at,
                        ban_state_end_at=account.ban_game_end_at,
                        last_rare_operation_at_turn=turn.number(),
                        settings_approved=False,
                        actual_bills=[],
                        upbringing=beings_relations.UPBRINGING.PHILISTINE,
                        death_age=beings_relations.AGE.MATURE,
                        first_death=beings_relations.FIRST_DEATH.FROM_THE_MONSTER_FANGS,
                        utg_name=utg_name)

    dress_new_hero(hero)
    preferences_for_new_hero(hero)

    if full_create:
        cards_for_new_hero(hero)

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


def get_heroes_to_accounts_map(heroes_ids):
    return dict(models.Hero.objects.filter(id__in=heroes_ids).values_list('id', 'account_id'))
