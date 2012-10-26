# -*- coding: utf-8 -*-

from dext.utils import s11n
from dext.utils import database

from game.heroes.prototypes import HeroPrototype

from game.balance import constants as c
from game.prototypes import TimePrototype
from game.angels.models import Angel


class AngelPrototype(object):

    def __init__(self, model=None):
        self.model = model
        self.updated = False

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(model=Angel.objects.get(id=id_))
        except Angel.DoesNotExist:
            return None

    @classmethod
    def get_by_account_id(cls, account_id):
        return cls(model=Angel.objects.get(account_id=account_id))

    def get_account(self):
        from accounts.prototypes import AccountPrototype
        return AccountPrototype.get_by_id(self.model.account_id)

    @property
    def account_id(self): return self.model.account_id

    @property
    def id(self): return self.model.id

    @property
    def energy_maximum(self): return c.ANGEL_ENERGY_MAX

    @property
    def energy(self): return self.model.energy

    def change_energy(self, value):
        old_energy = self.model.energy

        self.model.energy += value
        if self.model.energy < 0:
            self.model.energy = 0
        elif self.model.energy > self.energy_maximum:
            self.model.energy = self.energy_maximum

        if self.model.energy != old_energy:
            self.updated = True

        return self.model.energy - old_energy

    def get_might(self): return self.model.might
    def set_might(self, value):
        if self.model.might != value:
            self.model.might = value
            self.updated = True
    might = property(get_might, set_might)

    def get_might_updated_time(self): return self.model.might_updated_time
    def set_might_updated_time(self, value): self.model.might_updated_time = value
    might_updated_time = property(get_might_updated_time, set_might_updated_time)

    def get_hero(self):
        #TODO: now this code only works on bundle init phase
        #      using it from another places is dangerouse becouse of
        #      desinchronization between workers and database
        return HeroPrototype.get_by_angel_id(self.id)

    def load_abilities(self):
        from ..abilities.prototypes import AbilityPrototype
        from ..abilities.deck import ABILITIES
        data = s11n.from_json(self.model.abilities)
        abilities = {}
        for ability_dict in data.values():
            ability = AbilityPrototype.deserialize(ability_dict)
            if ability is None:
                continue
            abilities[ability.get_type()] = ability

        for ability_type, ability in ABILITIES.items():
            if ability_type not in abilities:
                abilities[ability_type] = ability()

        self._abilities = abilities

    def save_abilities(self):
        data = {}
        for ability in self.abilities.values():
            data[ability.get_type()] = ability.serialize()
        self.model.abilities = s11n.to_json(data)

    @property
    def abilities(self):
        if not hasattr(self, '_abilities'):
            self.load_abilities()
        return self._abilities

    ###########################################
    # Object operations
    ###########################################

    def remove(self):
        self.get_hero().remove()
        self.model.delete()

    def save(self):
        self.save_abilities()
        database.raw_save(self.model)
        # self.model.save(force_update=True)
        self.updated = False

    def ui_info(self, turn_number, ignore_actions=False, ignore_quests=False):
        return {'id': self.id,
                'energy': { 'max': self.energy_maximum,
                            'value': self.energy },
                'might': self.might,
                'abilities': [ability.ui_info() for ability_type, ability in self.abilities.items()]
                }

    @classmethod
    def create(cls, account):
        # from ..abilities import deck
        # TODO: rewrite from create-change-save to save
        angel_model = Angel.objects.create(account=account.model, energy=c.ANGEL_ENERGY_MAX)
        angel = AngelPrototype(model=angel_model)
        # angel.abilities.update({deck.Help.get_type(): deck.Help()})
        # angel.save()

        return angel


    ###########################################
    # Next turn operations
    ###########################################

    def process_turn(self):
        return TimePrototype.get_current_turn_number() + 1

    def __eq__(self, other):
        return (self.id == other.id and
                self.model.energy == other.model.energy and
                self.abilities == other.abilities)


    def calculate_might(self):
        from accounts.models import Award, AWARD_TYPE
        from forum.models import Post, Thread, POST_STATE
        from game.bills.models import Bill, Vote, BILL_STATE

        MIGHT_FOR_FORUM_POST = 0.3
        MIGHT_FOR_FORUM_THREAD = 3
        MIGHT_FOR_BILL_VOTE = 1
        MIGHT_FOR_BILL_ACCEPTED = 33

        MIGHT_FOR_AWARD = { AWARD_TYPE.BUG_MINOR: 111,
                            AWARD_TYPE.BUG_NORMAL: 222,
                            AWARD_TYPE.BUG_MAJOR: 333,
                            AWARD_TYPE.CONTEST_1_PLACE: 1000,
                            AWARD_TYPE.CONTEST_2_PLACE: 666,
                            AWARD_TYPE.CONTEST_3_PLACE: 333,
                            AWARD_TYPE.STANDARD_MINOR: 333,
                            AWARD_TYPE.STANDARD_NORMAL: 666,
                            AWARD_TYPE.STANDARD_MAJOR: 1000 }


        might = 0

        might += Post.objects.filter(author_id=self.account_id, state=POST_STATE.DEFAULT).count() * MIGHT_FOR_FORUM_POST
        might += Thread.objects.filter(author_id=self.account_id).count() * MIGHT_FOR_FORUM_THREAD

        might += Vote.objects.filter(owner_id=self.account_id).count() * MIGHT_FOR_BILL_VOTE
        might += Bill.objects.filter(owner_id=self.account_id, state=BILL_STATE.ACCEPTED).count() * MIGHT_FOR_BILL_ACCEPTED

        for award_state, might_cooficient in MIGHT_FOR_AWARD.items():
            might += Award.objects.filter(account_id=self.account_id).count() * might_cooficient

        return might
