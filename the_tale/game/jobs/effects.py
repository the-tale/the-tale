# coding: utf-8
from rels import Column
from rels.django import DjangoEnum

from the_tale.amqp_environment import environment

from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.game import effects
from the_tale.game.balance import constants as c

from the_tale.game.places import relations as places_relations



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

        positive_kwargs = dict(message_type=self.message_type(actor_type, effect, direction, 'friends'), **method_kwargs)

        after_update_operations = []

        for hero_id in positive_heroes:
            operation = self.invoke_hero_method(account_id=heroes_to_accounts[hero_id],
                                                hero_id=hero_id,
                                                method_name=method_names[0],
                                                method_kwargs=positive_kwargs)
            after_update_operations.append(operation)

        negative_kwargs = dict(message_type=self.message_type(actor_type, effect, direction, 'enemies'), **method_kwargs)

        for hero_id in negative_heroes:
            operation = self.invoke_hero_method(account_id=heroes_to_accounts[hero_id],
                                                hero_id=hero_id,
                                                method_name=method_names[1],
                                                method_kwargs=negative_kwargs)
            after_update_operations.append(operation)

        return after_update_operations


    def invoke_hero_method(self, account_id, hero_id, method_name, method_kwargs):
        from the_tale.game.heroes import postponed_tasks as heroes_postponed_tasks

        logic_task = heroes_postponed_tasks.InvokeHeroMethodTask(hero_id=hero_id,
                                                                 method_name=method_name,
                                                                 method_kwargs=method_kwargs)

        task = PostponedTaskPrototype.create(logic_task)

        return lambda: environment.workers.supervisor.cmd_logic_task(account_id=account_id, task_id=task.id)


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
        effect_value = self.base_value*job_power
        effect_delta = effect_value * (1.0 / c.NORMAL_JOB_LENGTH)
        place.effects.add(effects.Effect(name=actor_name, attribute=self.attribute, value=effect_value, delta=effect_delta))

        return self.apply_to_heroes(actor_type=actor_type,
                                    effect=getattr(EFFECT, 'PLACE_{}'.format(self.attribute.name)),
                                    method_names=('job_message', 'job_message'),
                                    method_kwargs={'place_id': place.id, 'person_id': person.id if person else None, 'job_power': job_power},
                                    positive_heroes=positive_heroes,
                                    negative_heroes=negative_heroes,
                                    direction='positive')


    def apply_negative(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        effect_value = self.base_value*job_power
        effect_delta = effect_value * (1.0 / c.NORMAL_JOB_LENGTH)
        place.effects.add(effects.Effect(name=actor_name, attribute=self.attribute, value=-effect_value, delta=effect_delta))

        return self.apply_to_heroes(actor_type=actor_type,
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
        return self.apply_to_heroes(actor_type=actor_type,
                                    effect=getattr(EFFECT, self.effect_name),
                                    method_names=(self.method_name, 'job_message'),
                                    method_kwargs={'place_id': place.id, 'person_id': person.id if person else None, 'job_power': job_power},
                                    positive_heroes=positive_heroes,
                                    negative_heroes=negative_heroes,
                                    direction='positive')

    def apply_negative(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        return self.apply_to_heroes(actor_type=actor_type,
                                    effect=getattr(EFFECT, self.effect_name),
                                    method_names=('job_message', self.method_name),
                                    method_kwargs={'place_id': place.id, 'person_id': person.id if person else None, 'job_power': job_power},
                                    positive_heroes=positive_heroes,
                                    negative_heroes=negative_heroes,
                                    direction='negative')



def place_attribute(id, attribute_name, base_value, attribute_text):
    attribute = places_relations.ATTRIBUTE.index_name[attribute_name]
    return ('PLACE_{}'.format(attribute_name),
            id,
            attribute.text,
            ChangePlaceAttribute(attribute=attribute, base_value=base_value),
            EFFECT_GROUP.ON_PLACE,
            1.0,
            u'При удачном завершении проекта, временно улучшает {} города, в случае неудачи — ухудшает.'.format(attribute_text))


def hero_profit(id, profit_name, text, power_modifier, description):
    effect_name = 'HERO_{}'.format(profit_name)
    return (effect_name,
            id,
            text,
            HeroMethod(effect_name=effect_name, method_name='job_{}'.format(profit_name).lower()),
            EFFECT_GROUP.ON_HEROES,
            power_modifier,
            description)


class EFFECT_GROUP(DjangoEnum):
    records = ( ('ON_PLACE', 0, u'на город'),
                ('ON_HEROES', 1, u'на героев') )


class EFFECT(DjangoEnum):
    logic = Column(single_type=False)
    group = Column(unique=False)
    power_modifier = Column(single_type=False, unique=False)
    description = Column()

    records = ( place_attribute(1, 'PRODUCTION', base_value=c.JOB_PRODUCTION_BONUS, attribute_text=u'производство'),
                place_attribute(2, 'SAFETY', base_value=c.JOB_SAFETY_BONUS, attribute_text=u'безопасность'),
                place_attribute(3, 'TRANSPORT', base_value=c.JOB_TRANSPORT_BONUS, attribute_text=u'транспорт'),
                place_attribute(4, 'FREEDOM', base_value=c.JOB_FREEDOM_BONUS, attribute_text=u'свободу'),
                place_attribute(5, 'STABILITY', base_value=c.JOB_STABILITY_BONUS, attribute_text=u'стабильность'),

                hero_profit(6, 'MONEY', u'золото ближнему кругу', 0.5, u'В случае удачного завершения проекта, высылает деньги помогающим героям из ближнего круга. В случае неудачи деньги достаются мешающим героям.'),
                hero_profit(7, 'ARTIFACT', u'артефакт ближнему кругу', 1.5, u'В случае удачного завершения проекта, высылает по артефакту помогающим героям из ближнего круга. В случае неудачи артефакты достаются мешающим героям.'),
                hero_profit(8, 'EXPERIENCE', u'опыт ближнему кругу', 2.0, u'В случае удачного завершения проекта, помогающие герои из ближнего круга получают немного опыта. В случае неудачи опыт достаётся мешающим героям.'),
                hero_profit(9, 'ENERGY', u'энергию ближнему кругу', 1.0, u'В случае удачного завершения проекта, Хранители помогающих героев из ближнего круга получают немного энергии. В случае неудачи энергия достаётся Хранителям мешающих героев.') )
