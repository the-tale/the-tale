# -*- coding: utf-8 -*-
import inspect

from django.core.urlresolvers import reverse

from django_next.utils.decorators import nested_commit_on_success
from django_next.utils import s11n

from ..heroes.prototypes import HeroPrototype, get_hero_by_id

from .models import Card, CardsQueueItem
from . import forms

MAIN_DESCRIPTION = u'''
Карты - это основной инструмент, с помощью которого Ангелы могут влиять на происходящее в окружающем мире.
'''

def get_card_by_id(model_id):
    card = Card.objects.get(id=model_id)
    card_type = get_card_type(card.type)
    return card_type(model=card)

def get_card_by_model(model):
    card_type = get_card_type(model.type)
    return card_type(model=model)

def get_card_type(type_name):
    card_type = globals()[type_name]
    return card_type

def get_prototypes():
    result = {}
    for k, v in globals().items():
        if inspect.isclass(v) and issubclass(v, CardPrototype) and v != CardPrototype:
            result[k] = v
    return result

def get_card_queue_item_by_model(model):
    return CardsQueueItemPrototype(model=model)


class CardsQueueItemPrototype(object):

    def __init__(self, model, *argv, **kwargs):
        super(CardsQueueItemPrototype, self).__init__(*argv, **kwargs)
        self.model = model

    def remove(self): return self.model.delete()
    def save(self): self.model.save()

    @property
    def id(self): return self.model.id

    def get_processed(self): return self.model.processed
    def set_processed(self, value): self.model.processed = value
    processed = property(get_processed, set_processed)

    @property
    def card(self): 
        if not hasattr(self, '_card'):
            self._card = get_card_by_id(self.model.card_id)
        return self._card

    @property
    def data(self): 
        if not hasattr(self, '_data'):
            self._data = s11n.from_json(self.model.data)            
        return self._data

    @nested_commit_on_success
    def process(self):
        self.card.process_from_query(self.data)
        self.processed = True
        self.save()

    @classmethod
    def create(cls, turn, card, data={}):
        query_item = CardsQueueItem.objects.create(turn=turn.model,
                                                   card=card.model,
                                                   data=s11n.to_json(data))
        return query_item


class ACTIVATION_TYPE(object):

    INSTANT = 'instant'


class CardPrototype(object):

    activation_type = ACTIVATION_TYPE.INSTANT
    name = u'нет имени'
    description = u'нет описания'
    artistic = u'нет художественного описания'
    use_form = False

    form = None
    template = None

    COOLDOWN = 1

    def __init__(self, model, *argv, **kwargs):
        super(CardPrototype, self).__init__(*argv, **kwargs)
        self.model = model

    @property
    def angel_id(self): return self.model.angel_id

    def remove(self): return self.model.delete()
    def save(self): self.model.save()

    @property
    def id(self): return self.model.id

    def get_cooldown_end(self): return self.model.cooldown_end
    def set_cooldown_end(self, value): self.model.cooldown_end = value
    cooldown_end = property(get_cooldown_end, set_cooldown_end)

    @property
    def type(self): return self.__class__.__name__

    @classmethod
    def create_form(cls, resource):
        if resource.request.POST:
            return True, cls.form(resource.request.POST)
        return True, cls.form()

    def ui_info(self):
        return {'id': self.id,
                'type': self.type,
                'angel': self.angel_id,
                'form_link': reverse('game:cards:form', args=[self.id]),
                'activation_link': reverse('game:cards:activate', args=[self.id]),
                'activation_type': self.activation_type,
                'name': self.name,
                'description': self.description,
                'use_form': self.use_form,
                'cooldown_end': self.cooldown_end,
                'artistic': self.artistic}

    @classmethod
    @nested_commit_on_success
    def create(cls, angel):
        card = Card()
        card.angel = angel.model
        card.type = cls.__name__
        card.save()
        return card


class FirstHeroCard(CardPrototype):

    activation_type = ACTIVATION_TYPE.INSTANT
    name = u'Первый'
    description = u'Первый и самый родной герой каждого ангела. Ангел сам выбирает, кто удостоится чести первым получить его покровительство.'
    artistic = u'У него не было памяти, не было вещей; обладал он только именем, которое получил от Ангела и верой в то, что покровителем для него уготована великая судьба.'

    form = forms.FirstHeroCardForm
    use_form = True
    template = 'cards/prototypes/first_hero_card.html'

    @nested_commit_on_success
    def activate(self, resource, form):
        HeroPrototype.create(angel=resource.angel,
                             name=form.c.name,
                             first=True,
                             intellect=form.c.intellect,
                             constitution=form.c.constitution,
                             reflexes=form.c.reflexes,
                             charisma=form.c.charisma,
                             chaoticity=form.c.chaoticity)
        self.remove()


class PushToQuestCard(CardPrototype):

    activation_type = ACTIVATION_TYPE.INSTANT
    name = u'Стимул'
    description = u'Принудить героя к действию, если тот бездельничает.'
    artistic = u'Как и все люди, герои - существа ленивые. Поэтому иногда их следует вежливо, или не очень, подтолнкуть в сторону активных действий.'

    form = forms.ApplyToHeroForm
    template = 'cards/prototypes/apply_to_hero.html'

    @classmethod
    def create_form(cls, resource):
        heroes = resource.angel.heroes

        if len(heroes) == 0:
            # TODO: move to configuration?
            return False, u'У Вас нет героя, к которому можно применить данный эффект'

        if resource.request.POST:
            return True, cls.form(heroes, resource.request.POST)
        
        return True, cls.form(heroes)


    @nested_commit_on_success
    def activate(self, resource, form):
        self.cooldown_end = resource.turn.number + self.COOLDOWN
        self.save()

        CardsQueueItemPrototype.create(turn=resource.turn, 
                                       card=self,
                                       data={'hero_id': form.c.hero})

    #TODO: do all needed checks befor push
    @nested_commit_on_success
    def process_from_query(self, data):

        hero = get_hero_by_id(data['hero_id'])

        hero.create_tmp_log_message('Go and kill some monsters!!!')

        lead_action = hero.get_actions()[-1]
        lead_action.entropy = lead_action.ENTROPY_BARRIER + 1
        lead_action.save()
        
