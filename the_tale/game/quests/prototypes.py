# -*- coding: utf-8 -*-

from django_next.utils.decorators import nested_commit_on_success

from ..heroes.prototypes import get_hero_by_model
from ..map.places.models import Place
from ..map.places.prototypes import PlacePrototype
#from ..actions.models import ActionQuest

from .models import Quest, QuestMailDelivery

def get_quests_types():
    quests = {}
    for key, cls in globals().items():
        if isinstance(cls, type) and issubclass(cls, QuestPrototype) and cls != QuestPrototype:
            quests[cls.TYPE] = cls
    return quests

def get_quest_by_model(base_model):
    return QUESTS_TYPES[base_model.type](base_model=base_model)


class QuestPrototype(object):

    TYPE = 'BASE'

    def __init__(self, base_model, *argv, **kwargs):
        super(QuestPrototype, self).__init__(*argv, **kwargs)
        self.base_model = base_model

    @property
    def id(self): return self.base_model.id

    @property
    def type(self): return self.base_model.type

    def get_state(self): return self.base_model.state
    def set_state(self, state): self.base_model.state = state
    state = property(get_state, set_state)

    def get_percents(self): return self.base_model.percents
    def set_percents(self, value): self.base_model.percents = value
    percents = property(get_percents, set_percents)

    @property
    def heroes(self): return []

    # @property
    # def base_action(self): 
    #     from ..actions.prototypes import get_action_by_model
    #     if not hasattr(self, '_base_action'):
    #         action_model = ActionQuest.objects.select_related('base_action').get(quest=self.model)
    #         self._base_action = get_action_by_model(base_model=action_model, model=action_model.base_action)
    #     return self._base_action

    ###########################################
    # Object operations
    ###########################################

    def remove(self): self.base_model.delete()
    def save(self): self.base_model.save()

    def ui_info(self):
        return {'id': self.id,
                'type': self.type,
                'state': self.state}


class QuestMailDeliveryPrototype(QuestPrototype):

    TYPE = 'MAIL_DELIVERY'

    class STATE:
        INITIAL = 'INITIAL'
        DELIVERY = 'DELIVERY'
        DELIVERED = 'DELIVERED'

    def __init__(self, base_model, model=None, *argv, **kwargs):
        super(QuestMailDeliveryPrototype, self).__init__(base_model, *argv, **kwargs)
        self.model = model if model else base_model.mail_delivery

    def remove(self): 
        self.model.delete()
        super(QuestMailDeliveryPrototype, self).remove()

    def save(self):
        self.model.save()
        super(QuestMailDeliveryPrototype, self).save()

    def ui_info(self):
        info = super(QuestMailDeliveryPrototype, self).ui_info()
        return info

    @property
    def delivery_from(self): 
        if not hasattr(self, '_delivery_from'):
            self._delivery_from = PlacePrototype(model=self.model.delivery_from)
        return self._delivery_from

    @property
    def delivery_to(self): 
        if not hasattr(self, '_delivery_to'):
            self._delivery_to = PlacePrototype(model=self.model.delivery_to)
        return self._delivery_to

    @property
    def hero(self):
        if not hasattr(self, '_hero'):
            self._hero = get_hero_by_model(self.model.hero)
        return self._hero

    @property
    def heroes(self): return [self.hero]

    @nested_commit_on_success
    def create_action(self):
        from ..actions.prototypes import ActionQuestMailDeliveryPrototype
        return ActionQuestMailDeliveryPrototype.create(quest=self)

    @classmethod
    @nested_commit_on_success
    def create(cls, hero):
        base_model = Quest.objects.create( type=cls.TYPE, 
                                           state=cls.STATE.INITIAL)

        # TODO: check situation when hero moved between places (i.e. hero.position.place is None)

        place_from = hero.position.place

        place_to = Place.objects.exclude(id=place_from.id).order_by('?')[0]
        
        model = QuestMailDelivery.objects.create( base_quest=base_model, 
                                                  hero=hero.model,
                                                  delivery_from=place_from.model,
                                                  delivery_to=place_to)

        quest = cls(base_model=base_model, model=model)

        return quest

        
QUESTS_TYPES = get_quests_types()
