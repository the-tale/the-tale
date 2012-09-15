# coding utf-8
from game.angels.prototypes import AngelPrototype

from game.models import Bundle, BundleMember, BUNDLE_TYPE

class BundleException(Exception): pass

class BundlePrototype(object):

    def __init__(self, model):
        self.model = model

        self.angels = {}
        self.heroes = {}
        self.actions = {}

        self.heroes_to_actions = {}

        self.load_data()

    @classmethod
    def get_by_id(cls, model_id):
        return cls(model=Bundle.objects.get(id=model_id))

    @classmethod
    def get_by_angel(cls, angel):
        member = BundleMember.objects.get(angel_id=angel.id)
        return cls(member.bundle)

    @property
    def id(self): return self.model.id

    @property
    def type(self): return self.model.type

    def get_owner(self): return self.model.owner
    def set_owner(self, value): self.model.owner = value
    owner = property(get_owner, set_owner)

    @property
    def is_single(self):
        if not hasattr(self, '_is_single'):
            self._is_single = self.model.members.all().count()
        return self._is_single

    def add_hero(self, hero):
        self.heroes[hero.id] = hero
        self.heroes_to_actions[hero.id] = []
        for action in hero.get_actions():
            self.add_action(action)

    def add_action(self, action):
        action.set_bundle(self)
        self.actions[action.id] = action
        self.heroes_to_actions[action.hero_id].append(action)

    def remove_action(self, action):
        del self.actions[action.id]
        action.set_bundle(None)
        last_action = self.heroes_to_actions[action.hero_id][-1]
        if last_action.id != action.id:
            raise BundleException('try to remove action (%d - %r) from the middle of actions list, last action id: (%d - %r). Actions list: %r' % (action.id, action, last_action.id, last_action, self.heroes_to_actions[action.hero_id]))
        self.heroes_to_actions[action.hero_id].pop()


    def current_hero_action(self, hero_id): return self.heroes_to_actions[hero_id][-1]

    def load_data(self):

        for member in self.model.members.all():
            angel = AngelPrototype.get_by_id(member.angel_id)
            self.angels[angel.id] = angel

            hero = angel.get_hero()

            if hero: # hero can be None if we at process of creating account
                self.add_hero(hero)

    def save_data(self):

        for angel in self.angels.values():
            if angel.updated:
                angel.save()

        for hero in self.heroes.values():
            hero.save()

        for action in self.actions.values():
            # print 'try save', action.__class__, action.updated, action.leader
            if action.updated:
                action.save()


    @classmethod
    def create(cls, angel):

        bundle = Bundle.objects.create(type=BUNDLE_TYPE.BASIC)
        BundleMember.objects.create(angel=angel.model, bundle=bundle)

        return BundlePrototype(model=bundle)

    def remove(self):
        self.model.delete() # must delete all members automaticaly

    def save(self):
        self.model.save()

    def process_turn(self):
        next_turn = None

        for angel in self.angels.values():
            next = angel.process_turn()
            if next_turn is None and next or next < next_turn:
                next_turn = next

        for hero in self.heroes.values():
            next = hero.process_turn()

            if next_turn is None and next or next < next_turn:
                next_turn = next

            leader_action = self.heroes_to_actions[hero.id][-1]

            next = leader_action.process_turn()

            if next_turn is None and next or next < next_turn:
                next_turn = next

        return next_turn

    def on_highlevel_data_updated(self):
        for hero in self.heroes.values():
            hero.on_highlevel_data_updated()

    ##########################
    # methods for test purposes
    def tests_get_last_action(self):
        return self.actions[sorted(self.actions.keys())[-1]]

    def tests_get_hero(self):
        return self.heroes.values()[0]

    def tests_get_angel(self):
        return self.angels.values()[0]


    def __eq__(self, other):
        # print self.angels == other.angels
        # print self.heroes == other.heroes
        # print self.actions == other.actions
        # print self.model == other.model
        return (self.angels == other.angels and
                self.heroes == other.heroes and
                self.actions == other.actions and
                self.model == other.model)
