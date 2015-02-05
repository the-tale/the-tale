# coding: utf-8

from the_tale.accounts.achievements.storage import achievements_storage
from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE


from the_tale.game.heroes import exceptions


class HeroStatistics(object):

    __slots__ = ('hero', )

    def __init__(self, hero):
        self.hero = hero

    #########################################
    # kills
    #########################################

    @property
    def pve_deaths(self): return self.hero._model.stat_pve_deaths
    def change_pve_deaths(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.DEATHS, object=self.hero):
            self.hero._model.stat_pve_deaths += value

    @property
    def pve_kills(self): return self.hero._model.stat_pve_kills
    def change_pve_kills(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.MOBS, object=self.hero):
            self.hero._model.stat_pve_kills += value


    #########################################
    # money
    #########################################

    def change_money(self, source, value):

        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.MONEY, object=self.hero):
            if source.is_EARNED_FROM_LOOT:
                self.hero._model.stat_money_earned_from_loot += value
            elif source.is_EARNED_FROM_ARTIFACTS:
                self.hero._model.stat_money_earned_from_artifacts += value
            elif source.is_EARNED_FROM_QUESTS:
                self.hero._model.stat_money_earned_from_quests += value
            elif source.is_EARNED_FROM_HELP:
                self.hero._model.stat_money_earned_from_help += value
            elif source.is_EARNED_FROM_HABITS:
                self.hero._model.stat_money_earned_from_habits += value
            elif source.is_EARNED_FROM_COMPANIONS:
                self.hero._model.stat_money_earned_from_companions += value

            elif source.is_SPEND_FOR_HEAL:
                self.hero._model.stat_money_spend_for_heal += value
            elif source.is_SPEND_FOR_ARTIFACTS:
                self.hero._model.stat_money_spend_for_artifacts += value
            elif source.is_SPEND_FOR_SHARPENING:
                self.hero._model.stat_money_spend_for_sharpening += value
            elif source.is_SPEND_FOR_USELESS:
                self.hero._model.stat_money_spend_for_useless += value
            elif source.is_SPEND_FOR_IMPACT:
                self.hero._model.stat_money_spend_for_impact += value
            elif source.is_SPEND_FOR_EXPERIENCE:
                self.hero._model.stat_money_spend_for_experience += value
            elif source.is_SPEND_FOR_REPAIRING:
                self.hero._model.stat_money_spend_for_repairing += value
            elif source.is_SPEND_FOR_TAX:
                self.hero._model.stat_money_spend_for_tax += value
            elif source.is_SPEND_FOR_COMPANIONS:
                self.hero._model.stat_money_spend_for_companions += value

            else:
                raise exceptions.UnknownMoneySourceError(source=source)


    @property
    def money_earned(self): return (self.money_earned_from_loot +
                                    self.money_earned_from_artifacts +
                                    self.money_earned_from_quests +
                                    self.money_earned_from_help +
                                    self.money_earned_from_habits +
                                    self.money_earned_from_companions)

    @property
    def money_spend(self): return (self.money_spend_for_heal +
                                   self.money_spend_for_impact +
                                   self.money_spend_for_useless +
                                   self.money_spend_for_artifacts +
                                   self.money_spend_for_sharpening +
                                   self.money_spend_for_experience +
                                   self.money_spend_for_repairing +
                                   self.money_spend_for_tax +
                                   self.money_spend_for_companions)

    @property
    def money_earned_from_loot(self): return self.hero._model.stat_money_earned_from_loot

    @property
    def money_earned_from_artifacts(self): return self.hero._model.stat_money_earned_from_artifacts

    @property
    def money_earned_from_quests(self): return self.hero._model.stat_money_earned_from_quests

    @property
    def money_earned_from_help(self): return self.hero._model.stat_money_earned_from_help

    @property
    def money_earned_from_habits(self): return self.hero._model.stat_money_earned_from_habits

    @property
    def money_earned_from_companions(self): return self.hero._model.stat_money_earned_from_companions


    @property
    def money_spend_for_heal(self): return self.hero._model.stat_money_spend_for_heal

    @property
    def money_spend_for_artifacts(self): return self.hero._model.stat_money_spend_for_artifacts

    @property
    def money_spend_for_sharpening(self): return self.hero._model.stat_money_spend_for_sharpening

    @property
    def money_spend_for_useless(self): return self.hero._model.stat_money_spend_for_useless

    @property
    def money_spend_for_impact(self): return self.hero._model.stat_money_spend_for_impact

    @property
    def money_spend_for_experience(self): return self.hero._model.stat_money_spend_for_experience

    @property
    def money_spend_for_repairing(self): return self.hero._model.stat_money_spend_for_repairing

    @property
    def money_spend_for_tax(self): return self.hero._model.stat_money_spend_for_tax

    @property
    def money_spend_for_companions(self): return self.hero._model.stat_money_spend_for_companions

    #########################################
    # different values
    #########################################

    @property
    def artifacts_had(self): return self.hero._model.stat_artifacts_had
    def change_artifacts_had(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.ARTIFACTS, object=self.hero):
            self.hero._model.stat_artifacts_had += value

    @property
    def loot_had(self): return self.hero._model.stat_loot_had
    def change_loot_had(self, value): self.hero._model.stat_loot_had += value

    @property
    def help_count(self): return self.hero._model.stat_help_count
    def change_help_count(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.KEEPER_HELP_COUNT, object=self.hero):
            self.hero._model.stat_help_count += value

    @property
    def cards_used(self): return self.hero._model.stat_cards_used
    def change_cards_used(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.KEEPER_CARDS_USED, object=self.hero):
            self.hero._model.stat_cards_used += value

    @property
    def cards_combined(self): return self.hero._model.stat_cards_combined
    def change_cards_combined(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.KEEPER_CARDS_COMBINED, object=self.hero):
            self.hero._model.stat_cards_combined += value

    @property
    def quests_done(self): return self.hero._model.stat_quests_done
    def change_quests_done(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.QUESTS, object=self.hero):
            self.hero._model.stat_quests_done += value

    @property
    def gifts_returned(self): return self.hero._model.stat_gifts_returned
    def change_gifts_returned(self, value):
        self.hero._model.stat_gifts_returned += value

    #########################################
    # pvp
    #########################################

    @property
    def pvp_battles_1x1_number(self): return self.hero._model.stat_pvp_battles_1x1_number

    @property
    def pvp_battles_1x1_victories(self): return self.hero._model.stat_pvp_battles_1x1_victories
    def change_pvp_battles_1x1_victories(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.PVP_BATTLES_1X1, object=self.hero):
            with achievements_storage.verify(type=ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1, object=self.hero):
                self.hero._model.stat_pvp_battles_1x1_number += value
                self.hero._model.stat_pvp_battles_1x1_victories += value

    @property
    def pvp_battles_1x1_draws(self): return self.hero._model.stat_pvp_battles_1x1_draws
    def change_pvp_battles_1x1_draws(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.PVP_BATTLES_1X1, object=self.hero):
            self.hero._model.stat_pvp_battles_1x1_number += value
            self.hero._model.stat_pvp_battles_1x1_draws += value

    @property
    def pvp_battles_1x1_defeats(self): return self.pvp_battles_1x1_number - self.pvp_battles_1x1_draws - self.pvp_battles_1x1_victories
    def change_pvp_battles_1x1_defeats(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.PVP_BATTLES_1X1, object=self.hero):
            self.hero._model.stat_pvp_battles_1x1_number += value

    def __eq__(self, other):
        return ( self.pve_deaths == other.pve_deaths and
                 self.pve_kills == other.pve_kills and
                 self.money_earned_from_loot == other.money_earned_from_loot and
                 self.money_earned_from_artifacts == other.money_earned_from_artifacts and
                 self.money_earned_from_quests == other.money_earned_from_quests and
                 self.money_earned_from_help == other.money_earned_from_help and
                 self.money_earned_from_habits == other.money_earned_from_habits and
                 self.money_earned_from_companions == other.money_earned_from_companions and
                 self.money_spend_for_heal == other.money_spend_for_heal and
                 self.money_spend_for_artifacts == other.money_spend_for_artifacts and
                 self.money_spend_for_sharpening == other.money_spend_for_sharpening and
                 self.money_spend_for_useless == other.money_spend_for_useless and
                 self.money_spend_for_impact == other.money_spend_for_impact and
                 self.money_spend_for_experience == other.money_spend_for_experience and
                 self.money_spend_for_repairing == other.money_spend_for_repairing and
                 self.money_spend_for_tax == other.money_spend_for_tax and
                 self.money_spend_for_companions == other.money_spend_for_companions and
                 self.artifacts_had == other.artifacts_had and
                 self.loot_had == other.loot_had and
                 self.quests_done == other.quests_done )
