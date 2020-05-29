
import smart_imports

smart_imports.all()


class BaseEffect(object):
    __slots__ = ()

    def __init__(self):
        pass

    def apply_positive(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        raise NotImplementedError()

    def apply_negative(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        raise NotImplementedError()

    def positive_effect_value(self, job_power):
        raise NotImplementedError()

    def negative_effect_value(self, job_power):
        raise NotImplementedError()

    def short_effect_description(self, value):
        raise NotImplementedError()

    def effect_type(self):
        raise NotImplementedError()

    def power_required(self, normal_power):
        return int(math.ceil(normal_power / self.effect_type().priority))

    def apply_to_heroes(self, actor_type, effect, method_names, method_kwargs, positive_heroes, negative_heroes, direction):
        from the_tale.game.heroes import logic as heroes_logic

        heroes_to_accounts = heroes_logic.get_heroes_to_accounts_map(positive_heroes | negative_heroes)

        positive_kwargs = dict(message_type=self.message_type(actor_type, effect, direction, 'friends'), **method_kwargs)

        after_update_operations = []

        for hero_id in positive_heroes:
            if hero_id not in heroes_to_accounts:
                continue  # skip removed fast accounts

            operation = self.invoke_hero_method(account_id=heroes_to_accounts[hero_id],
                                                hero_id=hero_id,
                                                method_name=method_names[0],
                                                method_kwargs=positive_kwargs)
            after_update_operations.append(operation)

        negative_kwargs = dict(message_type=self.message_type(actor_type, effect, direction, 'enemies'), **method_kwargs)

        for hero_id in negative_heroes:
            if hero_id not in heroes_to_accounts:
                continue  # skip removed fast accounts

            operation = self.invoke_hero_method(account_id=heroes_to_accounts[hero_id],
                                                hero_id=hero_id,
                                                method_name=method_names[1],
                                                method_kwargs=negative_kwargs)
            after_update_operations.append(operation)

        return after_update_operations

    def invoke_hero_method(self, account_id, hero_id, method_name, method_kwargs):
        logic_task = heroes_postponed_tasks.InvokeHeroMethodTask(hero_id=hero_id,
                                                                 method_name=method_name,
                                                                 method_kwargs=method_kwargs)

        task = PostponedTaskPrototype.create(logic_task)

        return lambda: amqp_environment.environment.workers.supervisor.cmd_logic_task(account_id=account_id, task_id=task.id)

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

    def effect_delta(self, value):
        return value * (1.0 / (24 * c.PLACE_STANDARD_EFFECT_LENGTH))

    def positive_effect_value(self, job_power):
        return self.base_value * job_power

    def negative_effect_value(self, job_power):
        return -self.base_value * job_power * c.JOB_NEGATIVE_POWER_MULTIPLIER

    def short_effect_description(self, value):
        return '{} от {}{} до 0{} на {} дней'.format(self.attribute.text,
                                                     self.attribute.formatter(value),
                                                     self.attribute.verbose_units,
                                                     self.attribute.verbose_units,
                                                     c.PLACE_STANDARD_EFFECT_LENGTH)

    def effect_type(self):
        return getattr(EFFECT, 'PLACE_{}'.format(self.attribute.name))

    def apply_positive(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        from the_tale.game.places import logic as places_logic

        value = self.positive_effect_value(job_power)

        delta = self.effect_delta(value)

        places_logic.register_effect(place_id=place.id,
                                     attribute=self.attribute,
                                     value=value,
                                     name=actor_name,
                                     delta=delta,
                                     refresh_effects=True,
                                     refresh_places=False,
                                     info={'source': 'jobs'})

        return self.apply_to_heroes(actor_type=actor_type,
                                    effect=self.effect_type(),
                                    method_names=('job_message', 'job_message'),
                                    method_kwargs={'place_id': place.id,
                                                   'person_id': person.id if person else None},
                                    positive_heroes=positive_heroes,
                                    negative_heroes=negative_heroes,
                                    direction='positive')

    def apply_negative(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        from the_tale.game.places import logic as places_logic

        value = self.negative_effect_value(job_power)

        delta = self.effect_delta(abs(value))

        places_logic.register_effect(place_id=place.id,
                                     attribute=self.attribute,
                                     value=value,
                                     name=actor_name,
                                     delta=delta,
                                     refresh_effects=True,
                                     refresh_places=False,
                                     info={'source': 'jobs'})

        return self.apply_to_heroes(actor_type=actor_type,
                                    effect=self.effect_type(),
                                    method_names=('job_message', 'job_message'),
                                    method_kwargs={'place_id': place.id,
                                                   'person_id': person.id if person else None},
                                    positive_heroes=positive_heroes,
                                    negative_heroes=negative_heroes,
                                    direction='negative')


class HeroMethod(BaseEffect):
    __slots__ = ('effect_name', 'method_name',)

    EFFECT_NAME = NotImplemented
    METHOD_NAME = NotImplemented

    def effect_type(self):
        return getattr(EFFECT, self.EFFECT_NAME)

    def apply_positive(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        return self.apply_to_heroes(actor_type=actor_type,
                                    effect=self.effect_type(),
                                    method_names=(self.METHOD_NAME, 'job_message'),
                                    method_kwargs={'place_id': place.id,
                                                   'person_id': person.id if person else None,
                                                   'effect_value': self.positive_effect_value(job_power)},
                                    positive_heroes=positive_heroes,
                                    negative_heroes=negative_heroes,
                                    direction='positive')

    def apply_negative(self, actor_type, actor_name, place, person, positive_heroes, negative_heroes, job_power):
        return self.apply_to_heroes(actor_type=actor_type,
                                    effect=self.effect_type(),
                                    method_names=('job_message', self.METHOD_NAME),
                                    method_kwargs={'place_id': place.id,
                                                   'person_id': person.id if person else None,
                                                   'effect_value': self.negative_effect_value(job_power)},
                                    positive_heroes=positive_heroes,
                                    negative_heroes=negative_heroes,
                                    direction='negative')


class HeroMoney(HeroMethod):
    __slots__ = ()

    EFFECT_NAME = 'HERO_MONEY'
    METHOD_NAME = 'job_money'

    TARGET_LEVEL = f.lvl_after_time(3 * 365 * 24)

    def money(self, job_power):
        return max(1, int(math.ceil(f.normal_action_price(self.TARGET_LEVEL) * job_power * c.NORMAL_JOB_LENGTH)))

    def positive_effect_value(self, job_power):
        return self.money(job_power)

    def negative_effect_value(self, job_power):
        return self.money(job_power * c.JOB_NEGATIVE_POWER_MULTIPLIER)

    def short_effect_description(self, value):
        return f'герой получает монеты: {value}'


class HeroExperience(HeroMethod):
    __slots__ = ()

    EFFECT_NAME = 'HERO_EXPERIENCE'
    METHOD_NAME = 'job_experience'

    def experience(self, job_power):
        from the_tale.game.places import storage as places_storage

        return max(1, int(math.ceil(f.experience_for_quest__real(places_storage.places.expected_minimum_quest_distance()) *
                                    job_power *
                                    c.NORMAL_JOB_LENGTH)))

    def positive_effect_value(self, job_power):
        return self.experience(job_power)

    def negative_effect_value(self, job_power):
        return self.experience(job_power * c.JOB_NEGATIVE_POWER_MULTIPLIER)

    def short_effect_description(self, value):
        return f'герой получает опыт: {value}'


class HeroArtifact(HeroMethod):
    __slots__ = ()

    EFFECT_NAME = 'HERO_ARTIFACT'
    METHOD_NAME = 'job_artifact'

    def priority(self, job_power):
        return {artifacts_relations.RARITY.RARE.value: c.RARE_ARTIFACT_PROBABILITY,
                artifacts_relations.RARITY.EPIC.value: c.EPIC_ARTIFACT_PROBABILITY * job_power}

    def positive_effect_value(self, job_power):
        return self.priority(job_power)

    def negative_effect_value(self, job_power):
        return self.priority(job_power * c.JOB_NEGATIVE_POWER_MULTIPLIER)

    def short_effect_description(self, value):
        percents = utils_logic.normalize_dict(dict(value))
        rare_percents = round(percents[artifacts_relations.RARITY.RARE.value] * 100)
        epic_percents = round(percents[artifacts_relations.RARITY.EPIC.value] * 100)
        return f'герой получает редкий ({rare_percents}%) или эпический ({epic_percents}%) артефакт'


class HeroCards(HeroMethod):
    __slots__ = ()

    EFFECT_NAME = 'HERO_CARDS'
    METHOD_NAME = 'job_cards'

    def cards_number(self, job_power):
        return max(1, int(math.ceil(24.0 / tt_cards_constants.NORMAL_RECEIVE_TIME * c.NORMAL_JOB_LENGTH * job_power)))

    def positive_effect_value(self, job_power):
        return self.cards_number(job_power)

    def negative_effect_value(self, job_power):
        return self.cards_number(job_power * c.JOB_NEGATIVE_POWER_MULTIPLIER)

    def short_effect_description(self, value):
        return f'Хранитель получает карты судьбы: {value}'


def place_attribute(id, attribute_name, base_value, attribute_text, priority):
    attribute = getattr(places_relations.ATTRIBUTE, attribute_name)
    return ('PLACE_{}'.format(attribute_name),
            id,
            f'{attribute.text} для города',
            ChangePlaceAttribute(attribute=attribute, base_value=base_value),
            EFFECT_GROUP.ON_PLACE,
            f'При удачном завершении проекта, временно улучшает {attribute_text} города, в случае неудачи — ухудшает.',
            priority)


def hero_profit(id, EffectClass, text, priority, description):
    return (EffectClass.EFFECT_NAME,
            id,
            text,
            EffectClass(),
            EFFECT_GROUP.ON_HEROES,
            description,
            priority)


class EFFECT_GROUP(rels_django.DjangoEnum):
    priority = rels.Column(unique=False)

    records = (('ON_PLACE', 0, 'для города', 1),
               ('ON_HEROES', 1, 'для героев', 1))


class EFFECT(rels_django.DjangoEnum):
    logic = rels.Column(single_type=False)
    group = rels.Column(unique=False)
    description = rels.Column()
    priority = rels.Column(unique=False, single_type=False)

    records = (place_attribute(1, 'PRODUCTION', base_value=c.JOB_PRODUCTION_BONUS, attribute_text='производство', priority=1),
               place_attribute(2, 'SAFETY', base_value=c.JOB_SAFETY_BONUS, attribute_text='безопасность', priority=0.5),
               place_attribute(3, 'TRANSPORT', base_value=c.JOB_TRANSPORT_BONUS, attribute_text='транспорт', priority=0.5),
               place_attribute(4, 'FREEDOM', base_value=c.JOB_FREEDOM_BONUS, attribute_text='свободу', priority=1),
               place_attribute(5, 'STABILITY', base_value=c.JOB_STABILITY_BONUS, attribute_text='стабильность', priority=0.25),

               hero_profit(6, HeroMoney, 'золото для героев', 1,
                           'В случае удачного завершения проекта, высылает деньги помогающим героям из ближнего круга. В случае неудачи деньги достаются мешающим героям.'),
               hero_profit(7, HeroArtifact, 'артефакты для героев', 0.75,
                           'В случае удачного завершения проекта, высылает по артефакту помогающим героям из ближнего круга. В случае неудачи артефакты достаются мешающим героям.'),
               hero_profit(8, HeroExperience, 'опыт для героев', 1,
                           'В случае удачного завершения проекта, помогающие герои из ближнего круга получают немного опыта. В случае неудачи опыт достаётся мешающим героям.'),
               hero_profit(9, HeroCards, 'карты судьбы для Хранителя', 0.5,
                           'В случае удачного завершения проекта, Хранители помогающих героев из ближнего круга получают карты судьбы. В случае неудачи карты достаются Хранителям мешающих героев.'),

               place_attribute(10, 'CULTURE', base_value=c.JOB_STABILITY_BONUS, attribute_text='культуру', priority=1))
