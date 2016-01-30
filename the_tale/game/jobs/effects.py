# coding: utf-8
from rels import Column
from rels.django import DjangoEnum

from the_tale.amqp_environment import environment

from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.game.places import relations as places_relations
from the_tale.game.places import effects as places_effects


class BaseEffect(object):
    __slots__ = ()

    def __init__(self):
        pass

    def apply_positive(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        raise NotImplementedError()

    def apply_negative(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        raise NotImplementedError()

    def apply_to_heroes(self, actor_type, effect, method_names, method_kwargs, positive_heroes, negative_heroes, direction):
        from the_tale.game.heroes import logic as heroes_logic

        heroes_to_accounts = heroes_logic.get_heroes_to_accounts_map(positive_heroes|negative_heroes)

        method_kwargs['message_type'] = self.message_type(actor_type, effect, direction, 'friends')

        for hero_id in positive_heroes:
            self.invoke_hero_method(account_id=heroes_to_accounts[hero_id],
                                    hero_id=hero_id,
                                    method_name=method_names[0],
                                    method_kwargs=method_kwargs)

        method_kwargs['message_type'] = self.message_type(actor_type, effect, direction, 'enemies')

        for hero_id in negative_heroes:
            self.invoke_hero_method(account_id=heroes_to_accounts[hero_id],
                                    hero_id=hero_id,
                                    method_name=method_names[1],
                                    method_kwargs=method_kwargs)

    def invoke_hero_method(self, account_id, hero_id, method_name, method_kwargs):
        from the_tale.game.heroes import postponed_tasks as heroes_postponed_tasks

        logic_task = heroes_postponed_tasks.InvokeHeroMethodTask(hero_id=hero_id,
                                                                 method_name=method_name,
                                                                 method_kwargs=method_kwargs)

        task = PostponedTaskPrototype.create(logic_task)
        environment.workers.supervisor.cmd_logic_task(account_id, task.id)

    def message_type(self, actor, effect, direction, group):
        return 'job_diary_{actor}_{effect}_{direction}_{group}'.format(actor=actor,
                                                                       effect=effect.name.lower(),
                                                                       direction=direction,
                                                                       group=group)

class ChangePlaceAttribute(BaseEffect):
    __slots__ = ('attribute', 'base_value')

    def __init__(self, attribute, base_value, **kwargs_view):
        super(ChangePlaceAttribute, self).__init__(**kwargs_view)
        self.attribute = attribute
        self.base_value = base_value


    def apply_positive(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        place.effects.add(places_effects.Effect(name=actor_name, attribute=self.attribute, value=self.base_value*job_power))

        self.apply_to_heroes(actor_type=actor_type,
                             effect=getattr(EFFECT, 'PLACE_{}'.format(self.attribute.name)),
                             method_names=('job_message', 'job_message'),
                             method_kwargs={'place_id': place.id, 'person_id': person.id if person else None, 'job_power': job_power},
                             positive_heroes=positive_heroes,
                             negative_heroes=negative_heroes,
                             direction='positive')

    def apply_negative(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        place.effects.add(places_effects.Effect(name=actor_name, attribute=self.attribute, value=-self.base_value*job_power))

        self.apply_to_heroes(actor_type=actor_type,
                             effect=getattr(EFFECT, 'PLACE_{}'.format(self.attribute.name)),
                             method_names=('job_message', 'job_message'),
                             method_kwargs={'place_id': place.id, 'person_id': person.id if person else None, 'job_power': job_power},
                             positive_heroes=positive_heroes,
                             negative_heroes=negative_heroes,
                             direction='negative')


class HeroMethod(BaseEffect):
    __slots__ = ('effect_name', 'method_name',)

    def __init__(self, effect_name, method_name, **kwargs_view):
        super(HeroMethod, self).__init__(**kwargs_view)
        self.effect_name = effect_name
        self.method_name = method_name


    def apply_positive(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        self.apply_to_heroes(actor_type=actor_type,
                             effect=getattr(EFFECT, self.effect_name),
                             method_names=(self.method_name, 'job_message'),
                             method_kwargs={'place_id': place.id, 'person_id': person.id if person else None, 'job_power': job_power},
                             positive_heroes=positive_heroes,
                             negative_heroes=negative_heroes,
                             direction='positive')

    def apply_negative(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        self.apply_to_heroes(actor_type=actor_type,
                             effect=getattr(EFFECT, self.effect_name),
                             method_names=('job_message', self.method_name),
                             method_kwargs={'place_id': place.id, 'person_id': person.id if person else None, 'job_power': job_power},
                             positive_heroes=positive_heroes,
                             negative_heroes=negative_heroes,
                             direction='negative')



def place_attribute(id, attribute_name, base_value):
    attribute = places_relations.ATTRIBUTE.index_name[attribute_name]
    return ('PLACE_{}'.format(attribute_name),
            id,
            attribute.text,
            ChangePlaceAttribute(attribute=attribute, base_value=base_value))


def hero_profit(id, profit_name, text):
    effect_name = 'HERO_{}'.format(profit_name)
    return (effect_name,
            id,
            text,
            HeroMethod(effect_name=effect_name, method_name='job_{}'.format(profit_name).lower()))

class EFFECT(DjangoEnum):
    logic = Column(single_type=False)

    records = ( place_attribute(1, 'PRODUCTION', base_value=1.0),
                place_attribute(2, 'SAFETY', base_value=1.0),
                place_attribute(3, 'TRANSPORT', base_value=1.0),
                place_attribute(4, 'FREEDOM', base_value=1.0),
                place_attribute(5, 'STABILITY', base_value=1.0),

                hero_profit(6, 'MONEY', u'золото ближнему кругу'),
                hero_profit(7, 'ARTIFACT', u'артефакт ближнему кругу'),
                hero_profit(8, 'EXPERIENCE', u'опыт ближнему кругу'),
                hero_profit(9, 'ENERGY', u'энергию ближнему кругу') )
