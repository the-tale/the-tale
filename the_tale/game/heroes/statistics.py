# coding: utf-8

from the_tale.accounts.achievements.storage import achievements_storage
from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE


from the_tale.game.heroes import exceptions


class Statistics(object):

    __slots__ = ('hero',
                 'pve_deaths',
                 'pve_kills',

                 'money_earned_from_loot',
                 'money_earned_from_artifacts',
                 'money_earned_from_quests',
                 'money_earned_from_help',
                 'money_earned_from_habits',
                 'money_earned_from_companions',

                 'money_spend_for_heal',
                 'money_spend_for_artifacts',
                 'money_spend_for_sharpening',
                 'money_spend_for_useless',
                 'money_spend_for_impact',
                 'money_spend_for_experience',
                 'money_spend_for_repairing',
                 'money_spend_for_tax',
                 'money_spend_for_companions',

                 'artifacts_had',
                 'loot_had',

                 'help_count',

                 'quests_done',

                 'companions_count',

                 'pvp_battles_1x1_number',
                 'pvp_battles_1x1_victories',
                 'pvp_battles_1x1_draws',

                 'cards_used',
                 'cards_combined',

                 'gifts_returned')

    def __init__(self,
                 pve_deaths,
                 pve_kills,

                 money_earned_from_loot,
                 money_earned_from_artifacts,
                 money_earned_from_quests,
                 money_earned_from_help,
                 money_earned_from_habits,
                 money_earned_from_companions,

                 money_spend_for_heal,
                 money_spend_for_artifacts,
                 money_spend_for_sharpening,
                 money_spend_for_useless,
                 money_spend_for_impact,
                 money_spend_for_experience,
                 money_spend_for_repairing,
                 money_spend_for_tax,
                 money_spend_for_companions,

                 artifacts_had,
                 loot_had,

                 help_count,

                 quests_done,

                 companions_count,

                 pvp_battles_1x1_number,
                 pvp_battles_1x1_victories,
                 pvp_battles_1x1_draws,

                 cards_used,
                 cards_combined,

                 gifts_returned):

        self.hero = None

        self.pve_deaths = pve_deaths
        self.pve_kills = pve_kills

        self.money_earned_from_loot = money_earned_from_loot
        self.money_earned_from_artifacts = money_earned_from_artifacts
        self.money_earned_from_quests = money_earned_from_quests
        self.money_earned_from_help = money_earned_from_help
        self.money_earned_from_habits = money_earned_from_habits
        self.money_earned_from_companions = money_earned_from_companions

        self.money_spend_for_heal = money_spend_for_heal
        self.money_spend_for_artifacts = money_spend_for_artifacts
        self.money_spend_for_sharpening = money_spend_for_sharpening
        self.money_spend_for_useless = money_spend_for_useless
        self.money_spend_for_impact = money_spend_for_impact
        self.money_spend_for_experience = money_spend_for_experience
        self.money_spend_for_repairing = money_spend_for_repairing
        self.money_spend_for_tax = money_spend_for_tax
        self.money_spend_for_companions = money_spend_for_companions

        self.artifacts_had = artifacts_had
        self.loot_had = loot_had

        self.help_count = help_count

        self.quests_done = quests_done

        self.companions_count = companions_count

        self.pvp_battles_1x1_number = pvp_battles_1x1_number
        self.pvp_battles_1x1_victories = pvp_battles_1x1_victories
        self.pvp_battles_1x1_draws = pvp_battles_1x1_draws

        self.cards_used = cards_used
        self.cards_combined = cards_combined

        self.gifts_returned = gifts_returned


    @classmethod
    def create(cls):
        return cls(pve_deaths=0,
                   pve_kills=0,

                   money_earned_from_loot=0,
                   money_earned_from_artifacts=0,
                   money_earned_from_quests=0,
                   money_earned_from_help=0,
                   money_earned_from_habits=0,
                   money_earned_from_companions=0,

                   money_spend_for_heal=0,
                   money_spend_for_artifacts=0,
                   money_spend_for_sharpening=0,
                   money_spend_for_useless=0,
                   money_spend_for_impact=0,
                   money_spend_for_experience=0,
                   money_spend_for_repairing=0,
                   money_spend_for_tax=0,
                   money_spend_for_companions=0,

                   artifacts_had=0,
                   loot_had=0,

                   help_count=0,

                   quests_done=0,

                   companions_count=0,

                   pvp_battles_1x1_number=0,
                   pvp_battles_1x1_victories=0,
                   pvp_battles_1x1_draws=0,

                   cards_used=0,
                   cards_combined=0,

                   gifts_returned=0)


    #########################################
    # kills
    #########################################

    def change_pve_deaths(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.DEATHS, object=self.hero):
            self.pve_deaths += value

    def change_pve_kills(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.MOBS, object=self.hero):
            self.pve_kills += value


    #########################################
    # money
    #########################################

    def change_money(self, source, value):

        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.MONEY, object=self.hero):
            if source.is_EARNED_FROM_LOOT:
                self.money_earned_from_loot += value
            elif source.is_EARNED_FROM_ARTIFACTS:
                self.money_earned_from_artifacts += value
            elif source.is_EARNED_FROM_QUESTS:
                self.money_earned_from_quests += value
            elif source.is_EARNED_FROM_HELP:
                self.money_earned_from_help += value
            elif source.is_EARNED_FROM_HABITS:
                self.money_earned_from_habits += value
            elif source.is_EARNED_FROM_COMPANIONS:
                self.money_earned_from_companions += value

            elif source.is_SPEND_FOR_HEAL:
                self.money_spend_for_heal += value
            elif source.is_SPEND_FOR_ARTIFACTS:
                self.money_spend_for_artifacts += value
            elif source.is_SPEND_FOR_SHARPENING:
                self.money_spend_for_sharpening += value
            elif source.is_SPEND_FOR_USELESS:
                self.money_spend_for_useless += value
            elif source.is_SPEND_FOR_IMPACT:
                self.money_spend_for_impact += value
            elif source.is_SPEND_FOR_EXPERIENCE:
                self.money_spend_for_experience += value
            elif source.is_SPEND_FOR_REPAIRING:
                self.money_spend_for_repairing += value
            elif source.is_SPEND_FOR_TAX:
                self.money_spend_for_tax += value
            elif source.is_SPEND_FOR_COMPANIONS:
                self.money_spend_for_companions += value

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

    #########################################
    # different values
    #########################################

    def change_artifacts_had(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.ARTIFACTS, object=self.hero):
            self.artifacts_had += value

    def change_loot_had(self, value): self.loot_had += value

    def change_help_count(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.KEEPER_HELP_COUNT, object=self.hero):
            self.help_count += value

    def change_companions_count(self, value):
        self.companions_count += value

    def change_cards_used(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.KEEPER_CARDS_USED, object=self.hero):
            self.cards_used += value

    def change_cards_combined(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.KEEPER_CARDS_COMBINED, object=self.hero):
            self.cards_combined += value

    def change_quests_done(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.QUESTS, object=self.hero):
            self.quests_done += value

    def change_gifts_returned(self, value):
        self.gifts_returned += value

    #########################################
    # pvp
    #########################################

    def change_pvp_battles_1x1_victories(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.PVP_BATTLES_1X1, object=self.hero):
            with achievements_storage.verify(type=ACHIEVEMENT_TYPE.PVP_VICTORIES_1X1, object=self.hero):
                self.pvp_battles_1x1_number += value
                self.pvp_battles_1x1_victories += value

    def change_pvp_battles_1x1_draws(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.PVP_BATTLES_1X1, object=self.hero):
            self.pvp_battles_1x1_number += value
            self.pvp_battles_1x1_draws += value

    @property
    def pvp_battles_1x1_defeats(self): return self.pvp_battles_1x1_number - self.pvp_battles_1x1_draws - self.pvp_battles_1x1_victories
    def change_pvp_battles_1x1_defeats(self, value):
        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.PVP_BATTLES_1X1, object=self.hero):
            self.pvp_battles_1x1_number += value

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
                 self.quests_done == other.quests_done and
                 self.help_count == other.help_count and
                 self.companions_count == other.companions_count)
