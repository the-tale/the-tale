# coding: utf-8

class HeroStatistics(object):

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
    @property
    def money_earned(self): return (self.money_earned_from_loot +
                                    self.money_earned_from_artifacts +
                                    self.money_earned_from_quests)

    @property
    def money_spend(self): return (self.money_spend_for_heal +
                                   self.money_spend_for_impact +
                                   self.money_spend_for_useless +
                                   self.money_spend_for_artifacts +
                                   self.money_spend_for_sharpening)

    @property
    def money_earned_from_loot(self): return self.hero_model.stat_money_earned_from_loot
    def change_money_earned_from_loot(self, value): self.hero_model.stat_money_earned_from_loot += value

    @property
    def money_earned_from_artifacts(self): return self.hero_model.stat_money_earned_from_artifacts
    def change_money_earned_from_artifacts(self, value): self.hero_model.stat_money_earned_from_artifacts += value

    @property
    def money_earned_from_quests(self): return self.hero_model.stat_money_earned_from_quests
    def change_money_earned_from_quests(self, value): self.hero_model.stat_money_earned_from_quests += value

    @property
    def money_spend_for_heal(self): return self.hero_model.stat_money_spend_for_heal
    def change_money_spend_for_heal(self, value): self.hero_model.stat_money_spend_for_heal += value

    @property
    def money_spend_for_artifacts(self): return self.hero_model.stat_money_spend_for_artifacts
    def change_money_spend_for_artifacts(self, value): self.hero_model.stat_money_spend_for_artifacts += value

    @property
    def money_spend_for_sharpening(self): return self.hero_model.stat_money_spend_for_sharpening
    def change_money_spend_for_sharpening(self, value): self.hero_model.stat_money_spend_for_sharpening += value

    @property
    def money_spend_for_useless(self): return self.hero_model.stat_money_spend_for_useless
    def change_money_spend_for_useless(self, value): self.hero_model.stat_money_spend_for_useless += value

    @property
    def money_spend_for_impact(self): return self.hero_model.stat_money_spend_for_impact
    def change_money_spend_for_impact(self, value): self.hero_model.stat_money_spend_for_impact += value

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
                 self.artifacts_had == other.artifacts_had and
                 self.loot_had == other.loot_had and
                 self.quests_done == other.quests_done )
