# coding utf-8
from dext.utils.decorators import nested_commit_on_success

from .angels.prototypes import get_angel_by_id

from .models import Bundle, BundleMember, BUNDLE_TYPE

def get_bundle_by_id(id):
    bundle = Bundle.objects.get(id=id)
    return get_bundle_by_model(model=bundle)

def get_bundle_by_model(model):
    return BundlePrototype(model=model)

class BundleException(Exception): pass

class BundlePrototype(object):

    def __init__(self, model):
        self.model = model

        self.angels = {}
        self.heroes = {}
        self.actions = {}

        self.heroes_to_actions = {}

        self.load_data()

    @property
    def id(self): return self.model.id

    @property
    def type(self): return self.model.type

    def get_owner(self): return self.model.owner
    def set_owner(self, value): self.model.owner = value
    owner = property(get_owner, set_owner)

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
            angel = get_angel_by_id(member.angel_id)
            self.angels[angel.id] = angel

            for hero in angel.heroes():
                self.add_hero(hero)

    @nested_commit_on_success
    def save_data(self):

        for angel in self.angels.values():
            angel.save()

        for hero in self.heroes.values():
            hero.save()

        for action in self.actions.values():
            if action.updated:
                action.save()


    @classmethod
    @nested_commit_on_success
    def create(cls, angel):

        bundle = Bundle.objects.create(type=BUNDLE_TYPE.BASIC)
        member = BundleMember.objects.create(angel=angel.model)
        bundle.members.add(member)

        return BundlePrototype(model=bundle)

    @nested_commit_on_success
    def save(self):
        self.model.save()

    def process_turn(self, turn_number):
        next_turn = None

        for angel in self.angels.values():
            next = angel.process_turn(turn_number)
            if next_turn is None and next or next < next_turn:
                next_turn = next

        for hero in self.heroes.values():
            next = hero.process_turn(turn_number)
            if next_turn is None and next or next < next_turn:
                next_turn = next

        for action in self.actions.values():
            if not action.leader:
                continue
            next = action.process_turn(turn_number)
            if next_turn is None and next or next < next_turn:
                next_turn = next

        self.save_data()

        return next_turn

    ##########################
    # methods for test purposes
    def tests_get_last_action(self):
        return self.actions[sorted(self.actions.keys())[-1]]

    def tests_get_hero(self):
        return self.heroes.values()[0]
