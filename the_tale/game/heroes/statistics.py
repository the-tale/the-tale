# coding: utf-8

from the_tale.game.heroes.exceptions import HeroException

class MONEY_SOURCE:

    EARNED_FROM_LOOT = 0
    EARNED_FROM_ARTIFACTS = 1
    EARNED_FROM_QUESTS = 2
    EARNED_FROM_HELP = 3

    SPEND_FOR_HEAL = 1000
    SPEND_FOR_ARTIFACTS = 1001
    SPEND_FOR_SHARPENING = 1002
    SPEND_FOR_USELESS = 1003
    SPEND_FOR_IMPACT = 1004
    SPEND_FOR_EXPERIENCE = 1005


class HeroStatistics(object):

    __slots__ = ('hero_model', )

    def __init__(self, hero_model):
        self.hero_model = hero_model

    #########################################
    # kills
    #########################################

    @property
    def pve_deaths(self): return self.hero_model.stat_pve_deaths
    def change_pve_deaths(self, value): self.hero_model.stat_pve_deaths += value

    @property
    def pve_kills(self): return self.hero_model.stat_pve_kills
    def change_pve_kills(self, value): self.hero_model.stat_pve_kills += value


    #########################################
    # money
    #########################################

    def change_money(self, source, value):

        if source == MONEY_SOURCE.EARNED_FROM_LOOT:
            self.hero_model.stat_money_earned_from_loot += value
        elif source == MONEY_SOURCE.EARNED_FROM_ARTIFACTS:
            self.hero_model.stat_money_earned_from_artifacts += value
        elif source == MONEY_SOURCE.EARNED_FROM_QUESTS:
            self.hero_model.stat_money_earned_from_quests += value
        elif source == MONEY_SOURCE.EARNED_FROM_HELP:
            self.hero_model.stat_money_earned_from_help += value

        elif source == MONEY_SOURCE.SPEND_FOR_HEAL:
            self.hero_model.stat_money_spend_for_heal += value
        elif source == MONEY_SOURCE.SPEND_FOR_ARTIFACTS:
            self.hero_model.stat_money_spend_for_artifacts += value
        elif source == MONEY_SOURCE.SPEND_FOR_SHARPENING:
            self.hero_model.stat_money_spend_for_sharpening += value
        elif source == MONEY_SOURCE.SPEND_FOR_USELESS:
            self.hero_model.stat_money_spend_for_useless += value
        elif source == MONEY_SOURCE.SPEND_FOR_IMPACT:
            self.hero_model.stat_money_spend_for_impact += value
        elif source == MONEY_SOURCE.SPEND_FOR_EXPERIENCE:
            self.hero_model.stat_money_spend_for_experience += value

        else:
            raise HeroException('unknown money source: %s' % source)


    @property
    def money_earned(self): return (self.money_earned_from_loot +
                                    self.money_earned_from_artifacts +
                                    self.money_earned_from_quests +
                                    self.money_earned_from_help)

    @property
    def money_spend(self): return (self.money_spend_for_heal +
                                   self.money_spend_for_impact +
                                   self.money_spend_for_useless +
                                   self.money_spend_for_artifacts +
                                   self.money_spend_for_sharpening +
                                   self.money_spend_for_experience)

    @property
    def money_earned_from_loot(self): return self.hero_model.stat_money_earned_from_loot

    @property
    def money_earned_from_artifacts(self): return self.hero_model.stat_money_earned_from_artifacts

    @property
    def money_earned_from_quests(self): return self.hero_model.stat_money_earned_from_quests

    @property
    def money_earned_from_help(self): return self.hero_model.stat_money_earned_from_help


    @property
    def money_spend_for_heal(self): return self.hero_model.stat_money_spend_for_heal

    @property
    def money_spend_for_artifacts(self): return self.hero_model.stat_money_spend_for_artifacts

    @property
    def money_spend_for_sharpening(self): return self.hero_model.stat_money_spend_for_sharpening

    @property
    def money_spend_for_useless(self): return self.hero_model.stat_money_spend_for_useless

    @property
    def money_spend_for_impact(self): return self.hero_model.stat_money_spend_for_impact

    @property
    def money_spend_for_experience(self): return self.hero_model.stat_money_spend_for_experience

    #########################################
    # different values
    #########################################

    @property
    def artifacts_had(self): return self.hero_model.stat_artifacts_had
    def change_artifacts_had(self, value): self.hero_model.stat_artifacts_had += value

    @property
    def loot_had(self): return self.hero_model.stat_loot_had
    def change_loot_had(self, value): self.hero_model.stat_loot_had += value

    @property
    def quests_done(self): return self.hero_model.stat_quests_done
    def change_quests_done(self, value): self.hero_model.stat_quests_done += value

    #########################################
    # pvp
    #########################################

    @property
    def pvp_battles_1x1_number(self): return self.hero_model.stat_pvp_battles_1x1_number
    def change_pvp_battles_1x1_number(self, value): self.hero_model.stat_pvp_battles_1x1_number += value

    @property
    def pvp_battles_1x1_victories(self): return self.hero_model.stat_pvp_battles_1x1_victories
    def change_pvp_battles_1x1_victories(self, value): self.hero_model.stat_pvp_battles_1x1_victories += value

    @property
    def pvp_battles_1x1_draws(self): return self.hero_model.stat_pvp_battles_1x1_draws
    def change_pvp_battles_1x1_draws(self, value): self.hero_model.stat_pvp_battles_1x1_draws += value

    @property
    def pvp_battles_1x1_defeats(self): return self.pvp_battles_1x1_number - self.pvp_battles_1x1_draws - self.pvp_battles_1x1_victories


    def __eq__(self, other):
        return ( self.pve_deaths == other.pve_deaths and
                 self.pve_kills == other.pve_kills and
                 self.money_earned_from_loot == other.money_earned_from_loot and
                 self.money_earned_from_artifacts == other.money_earned_from_artifacts and
                 self.money_earned_from_quests == other.money_earned_from_quests and
                 self.money_spend_for_heal == other.money_spend_for_heal and
                 self.money_spend_for_artifacts == other.money_spend_for_artifacts and
                 self.money_spend_for_sharpening == other.money_spend_for_sharpening and
                 self.money_spend_for_useless == other.money_spend_for_useless and
                 self.money_spend_for_impact == other.money_spend_for_impact and
                 self.money_spend_for_experience == other.money_spend_for_experience and
                 self.artifacts_had == other.artifacts_had and
                 self.loot_had == other.loot_had and
                 self.quests_done == other.quests_done )
