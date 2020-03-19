
import smart_imports

smart_imports.all()


class EventBase:
    __slots__ = ('raw_ability_power',)

    TYPE = NotImplemented
    BASE_CYCLE_LENGTH = 1
    HAS_PROTECTORAT_BONUS = False
    ONLY_FOR_PROTECTORAT = False

    def __init__(self, raw_ability_power):
        self.raw_ability_power = raw_ability_power

    @classmethod
    def form(cls, emissary, post=None):
        from . import forms
        return forms.EmptyEventForm(cls.period_choices(emissary), post)

    @classmethod
    def construct_by_form(cls, emissary, form):
        return cls(raw_ability_power=cls.get_raw_ability_power(emissary))

    @classmethod
    def max_event_length(cls):
        return tt_clans_constants.MAX_EVENT_LENGTH

    @classmethod
    def actual_value(cls,
                     raw_ability_power,
                     left,
                     right,
                     bonus=0,
                     round=lambda value: int(math.ceil(value))):
        value = left + cls.ability_power(raw_ability_power) * (right - left)
        return round(value * (1 + bonus))

    @classmethod
    def period_choices(cls, emissary):
        days = cls.cycle_time(emissary)

        choices = []

        while days <= cls.max_event_length():
            choices.append((days, '{} — {} влияния'.format(utils_logic.verbose_timedelta(days*24*60*60),
                                                           cls.power_cost(emissary, days))))

            days += cls.cycle_time(emissary)

        return choices

    @classmethod
    def ability_power(cls, raw_ability_power):
        return raw_ability_power / tt_emissaries_constants.MAXIMUM_ATTRIBUTE_MAXIMUM

    @classmethod
    def get_raw_ability_power(cls, emissary):
        power = sum(emissary.abilities[ability] for ability in cls.TYPE.abilities)
        power /= len(cls.TYPE.abilities)
        return int(math.ceil(power))

    @classmethod
    def is_available(cls, emissary, active_events):
        if cls.TYPE in active_events:
            return False

        return True

    @classmethod
    def cycle_time(cls, emissary):
        return cls.BASE_CYCLE_LENGTH

    @classmethod
    def action_points_cost(cls, emissary):
        return int(math.ceil(tt_clans_constants.PRICE_START_EVENT *
                             cls.TYPE.action_points_cost_modifier *
                             (1.0 + cls._action_points_cost_modificator(emissary))))

    @classmethod
    def _action_points_cost_modificator(cls, emissary):
        cost = 0

        for ability in cls.TYPE.abilities:
            cost += getattr(emissary.attrs, ('EVENT_ACTION_POINTS_DELTA__' + ability.name).lower())

        return cost

    @classmethod
    def power_for_day_cost(cls, emissary):
        return int(math.ceil(logic.expected_power_per_day() *
                             cls.TYPE.power_cost_modifier *
                             tt_emissaries_constants.EVENT_POWER_FRACTION *
                             (1.0 + cls._power_cost_modificator(emissary))))

    @classmethod
    def _power_cost_modificator(cls, emissary):

        cost = 0.0

        for ability in cls.TYPE.abilities:
            cost += getattr(emissary.attrs, ('EVENT_POWER_DELTA__' + ability.name).lower())

        return cost

    @classmethod
    def power_cost(cls, emissary, days):
        return int(math.ceil(cls.power_for_day_cost(emissary) * days))

    @contextlib.contextmanager
    def on_create(self, emissary):
        yield

    def after_create(self, event):
        pass

    def on_cancel(self, event):
        return True

    def on_step(self, event):
        return True

    def on_finish(self, event):
        return True

    def on_monitoring(self, event):
        pass

    def serialize(self):
        return {'type': self.TYPE.value,
                'raw_ability_power': self.raw_ability_power,
                'data': None}

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        raise NotImplementedError

    def event_description(self, emissary):
        return self.effect_description(emissary=emissary,
                                       raw_ability_power=self.raw_ability_power)

    @classmethod
    def deserialize(cls, data):
        return cls(raw_ability_power=data['raw_ability_power'])

    def actual_info(self, emissary):
        return None

    def actual_info_help(self):
        return None

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.raw_ability_power == other.raw_ability_power)

    def __ne__(self, other):
        return not self.__eq__(other)


class Rest(EventBase):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.REST
    HAS_PROTECTORAT_BONUS = True

    @classmethod
    def health_per_step(cls, raw_ability_power, bonus):
        return cls.actual_value(raw_ability_power,
                                tt_emissaries_constants.HEALTH_REGENERATION_MIN,
                                tt_emissaries_constants.HEALTH_REGENERATION_MAX,
                                bonus=bonus)

    def on_step(self, event):
        health_to_regenerate = self.health_per_step(self.raw_ability_power,
                                                    bonus=event.emissary.protectorat_event_bonus())

        event.emissary.health = min(event.emissary.health + health_to_regenerate, event.emissary.attrs.max_health)

        logic.save_emissary(event.emissary)

        return True

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        health = cls.health_per_step(raw_ability_power,
                                     bonus=emissary.protectorat_event_bonus() if emissary else 0)
        return f'Восстанавливает эмиссару {health} здоровья каждый час.'


class Dismiss(EventBase):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.DISMISS

    @classmethod
    def max_event_length(cls):
        return cls.BASE_CYCLE_LENGTH

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        return 'Увольняет эмиссара. Вернуть эмиссара после увольнения нельзя.'

    def on_finish(self, event):
        logic.cancel_events_except_one(event, logic.stop_event_due_emissary_left_game)

        logic.dismiss_emissary(event.emissary.id)
        return True


class Relocation(EventBase):
    __slots__ = ('place_id',)

    BASE_CYCLE_LENGTH = 2

    TYPE = relations.EVENT_TYPE.RELOCATION

    def __init__(self, place_id, **kwargs):
        super().__init__(**kwargs)
        self.place_id = place_id

    @classmethod
    def form(cls, emissary, post=None):
        from . import forms
        return forms.RelocateEventForm(emissary.place_id, cls.period_choices(emissary), post)

    @classmethod
    def construct_by_form(cls, emissary, form):
        return cls(raw_ability_power=cls.get_raw_ability_power(emissary),
                   place_id=int(form.c.place))

    @classmethod
    def max_event_length(cls):
        return cls.BASE_CYCLE_LENGTH

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        return f'По завершении мероприятия эмиссар перемещается в указанный город, его влияние становится равным {logic.expected_power_per_day()}. Все активные мероприятия эмиссара автоматически отменяются.'

    def event_description(self, emissary):
        return 'Перемещает эмиссара в {}.'.format(places_storage.places[self.place_id].utg_name.forms[3])

    def on_finish(self, event):
        logic.cancel_events_except_one(event, logic.stop_event_due_emissary_relocated)

        logic.move_emissary(emissary_id=event.emissary_id,
                            new_place_id=self.place_id)
        return True

    def serialize(self):
        data = super().serialize()
        data['data'] = {'place_id': self.place_id}
        return data

    @classmethod
    def deserialize(cls, data):
        return cls(raw_ability_power=data['raw_ability_power'],
                   place_id=data['data']['place_id'])

    def __eq__(self, other):
        return (super().__eq__(other) and
                self.place_id == other.place_id)


class Rename(EventBase):
    __slots__ = ('new_name',)

    TYPE = relations.EVENT_TYPE.RENAME

    def __init__(self, new_name, **kwargs):
        super().__init__(**kwargs)
        self.new_name = new_name

    @classmethod
    def form(cls, emissary, post=None):
        from . import forms
        return forms.RenameEventForm(cls.period_choices(emissary),
                                     post,
                                     initial={'name': emissary.utg_name})

    @classmethod
    def construct_by_form(cls, emissary, form):
        return cls(raw_ability_power=cls.get_raw_ability_power(emissary),
                   new_name=form.c.name)

    @classmethod
    def max_event_length(cls):
        return cls.BASE_CYCLE_LENGTH

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        return 'Изменяет имя эмиссара.'

    def event_description(self, emissary):
        return 'Изменяет имя на {}.'.format(self.new_name.forms[3])

    def on_finish(self, event):
        logic.rename_emissary(emissary_id=event.emissary_id,
                              new_name=self.new_name)
        return True

    def serialize(self):
        data = super().serialize()
        data['data'] = {'new_name': self.new_name.serialize()}
        return data

    @classmethod
    def deserialize(cls, data):
        return cls(raw_ability_power=data['raw_ability_power'],
                   new_name=utg_words.Word.deserialize(data['data']['new_name']))

    def __eq__(self, other):
        return (super().__eq__(other) and
                self.new_name == other.new_name)


class ClanLevelUpMixin:
    TYPE = None
    PROPERTY = None

    def __init__(self, transaction_id=None, current_level=None, **kwargs):
        super().__init__(**kwargs)
        self.transaction_id = transaction_id
        self.current_level = current_level

    @classmethod
    def max_event_length(cls):
        return cls.BASE_CYCLE_LENGTH

    @classmethod
    def construct_by_form(cls, emissary, form):
        return cls(raw_ability_power=cls.get_raw_ability_power(emissary))

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        current_level, required_experience = cls.experience_and_current_level(emissary)

        if required_experience is None:
            return 'Увеличивает {}. Этот параметр гильдии уже достиг максимального значения.'.format(cls.PROPERTY.text)

        if cls.TYPE.is_LEVEL_UP_POINTS_GANE:
            delta = '{} в день'.format(cls.PROPERTY.delta)
        else:
            delta = cls.PROPERTY.delta

        return f'Увеличивает {cls.PROPERTY.text} на {delta}. Тратит {required_experience} опыта гильдии. Если одновременно запущено два мероприятия этого типа, то второе не будет иметь эффекта, потраченный опыт вернётся гильдии. При отмене мероприятия потраченный опыт возвращается гильдии.'

    def event_description(self, emissary):
        current_level, required_experience = self.experience_and_current_level(emissary, current_level=self.current_level)

        if required_experience is None:
            return 'Увеличивает {self.PROPERTY.text}. Этот параметр гильдии уже достиг максимального значения.'

        if self.TYPE.is_LEVEL_UP_POINTS_GANE:
            delta = '{self.PROPERTY.delta} в день'
        else:
            delta = self.PROPERTY.delta

        return 'Увеличивает {self.PROPERTY.text} на {delta}. Тратит {required_experience} опыта гильдии. Если одновременно запущено два мероприятия этого типа, то второе не будет иметь эффекта, потраченный опыт вернётся гильдии. При отмене мероприятия потраченный опыт возвращается гильдии.'

    @classmethod
    def experience_and_current_level(cls, emissary, current_level=None):

        if emissary is None:
            # for guide page
            return len(cls.PROPERTY.experience) - 1, cls.PROPERTY.experience[-1]

        if current_level is None:
            attributes = clans_logic.load_attributes(emissary.clan_id)

            current_level = getattr(attributes, cls.PROPERTY.property)

        if current_level < len(cls.PROPERTY.experience):
            return current_level, cls.PROPERTY.experience[current_level]

        return current_level, None

    @classmethod
    def is_available(cls, emissary, active_events):
        if not super().is_available(emissary, active_events):
            return False

        current_level, required_experience = cls.experience_and_current_level(emissary)

        if required_experience is None:
            return False

        experience = clans_tt_services.currencies.cmd_balance(emissary.clan_id,
                                                              currency=clans_relations.CURRENCY.EXPERIENCE)

        if experience < required_experience:
            return False

        return True

    @contextlib.contextmanager
    def on_create(self, emissary):
        current_level, required_experience = self.experience_and_current_level(emissary)

        if required_experience is None:
            raise exceptions.OnEventCreateError(message='already on maximum')

        transaction_lifetime = (self.cycle_time(emissary) + 1) * 24 * 60 * 60

        success, transaction_id = clans_tt_services.currencies.cmd_change_balance(account_id=emissary.clan_id,
                                                                                  type='level_up_{}'.format(self.PROPERTY.name).lower(),
                                                                                  amount=-required_experience,
                                                                                  asynchronous=False,
                                                                                  autocommit=False,
                                                                                  currency=clans_relations.CURRENCY.EXPERIENCE,
                                                                                  transaction_lifetime=transaction_lifetime)

        if not success:
            raise exceptions.OnEventCreateError(message='not enougth experience')

        self.transaction_id = transaction_id
        self.current_level = current_level

        try:
            yield
        except Exception:
            clans_tt_services.currencies.cmd_rollback_transaction(transaction_id)
            raise

    def on_finish(self, event):

        attributes = clans_logic.load_attributes(event.emissary.clan_id)

        current_value = getattr(attributes, self.PROPERTY.property)

        if current_value != self.current_level:
            clans_tt_services.currencies.cmd_rollback_transaction(self.transaction_id)
            return False

        if self.PROPERTY.maximum <= current_value:
            clans_tt_services.currencies.cmd_rollback_transaction(self.transaction_id)
            return False

        with clans_tt_services.currencies.commit_or_rollback(self.transaction_id):
            clans_tt_services.properties.cmd_set_property(event.emissary.clan_id,
                                                          self.PROPERTY.property,
                                                          self.current_level + 1)

        return True

    def on_cancel(self, event):
        clans_tt_services.currencies.cmd_rollback_transaction(self.transaction_id)

    def serialize(self):
        data = super().serialize()
        data['data'] = {'transaction_id': self.transaction_id,
                        'current_level': self.current_level}
        return data

    @classmethod
    def deserialize(cls, data):
        return cls(raw_ability_power=data['raw_ability_power'],
                   transaction_id=data['data']['transaction_id'],
                   current_level=data['data']['current_level'])

    def __eq__(self, other):
        return (super().__eq__(other) and
                self.transaction_id == other.transaction_id and
                self.current_level == other.current_level)


class PointsGainLevelUp(ClanLevelUpMixin, EventBase):
    __slots__ = ('transaction_id', 'current_level')

    TYPE = relations.EVENT_TYPE.LEVEL_UP_POINTS_GANE
    PROPERTY = clans_relations.UPGRADABLE_PROPERTIES.POINTS_GAIN


class FightersMaximumLevelUp(ClanLevelUpMixin, EventBase):
    __slots__ = ('transaction_id', 'current_level')

    TYPE = relations.EVENT_TYPE.LEVEL_UP_FIGHTERS_MAXIMUM
    PROPERTY = clans_relations.UPGRADABLE_PROPERTIES.FIGHTERS_MAXIMUM


class EmissariesMaximumLevelUp(ClanLevelUpMixin, EventBase):
    __slots__ = ('transaction_id', 'current_level')

    TYPE = relations.EVENT_TYPE.LEVEL_UP_EMISSARIES_MAXIMUM
    PROPERTY = clans_relations.UPGRADABLE_PROPERTIES.EMISSARIES_MAXIMUM


class FreeQuestsMaximumLevelUp(ClanLevelUpMixin, EventBase):
    __slots__ = ('transaction_id', 'current_level')

    TYPE = relations.EVENT_TYPE.LEVEL_UP_FREE_QUESTS_MAXIMUM
    PROPERTY = clans_relations.UPGRADABLE_PROPERTIES.FREE_QUESTS_MAXIMUM


class Training(EventBase):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.TRAINING

    @classmethod
    def experience_per_step(cls, raw_ability_power):
        return cls.actual_value(raw_ability_power,
                                tt_emissaries_constants.MIN_EXPERIENCE_PER_EVENT,
                                tt_emissaries_constants.MAX_EXPERIENCE_PER_EVENT)

    def on_step(self, event):
        experience = self.experience_per_step(self.raw_ability_power)

        status, transaction_id = clans_tt_services.currencies.cmd_change_balance(account_id=event.emissary.clan_id,
                                                                                 type='training_experience',
                                                                                 amount=experience,
                                                                                 asynchronous=False,
                                                                                 autocommit=True,
                                                                                 currency=clans_relations.CURRENCY.EXPERIENCE)
        return status

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        text = 'Приносит гильдии дополнительно {experience} опыта каждый час.'
        return text.format(experience=cls.experience_per_step(raw_ability_power))


class ReservesSearch(EventBase):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.RESERVES_SEARCH
    HAS_PROTECTORAT_BONUS = True

    @classmethod
    def action_points_per_step(cls, raw_ability_power, bonus):
        return cls.actual_value(raw_ability_power,
                                tt_emissaries_constants.MIN_ACTION_POINTS_PER_EVENT,
                                tt_emissaries_constants.MAX_ACTION_POINTS_PER_EVENT,
                                bonus=bonus)

    def on_step(self, event):
        action_points = self.action_points_per_step(self.raw_ability_power,
                                                    bonus=event.emissary.protectorat_event_bonus())

        restrictions = clans_tt_services.currencies.Restrictions(hard_minimum=0,
                                                                 soft_maximum=tt_clans_constants.MAXIMUM_POINTS)

        status, transaction_id = clans_tt_services.currencies.cmd_change_balance(account_id=event.emissary.clan_id,
                                                                                 type='reserves_search',
                                                                                 amount=action_points,
                                                                                 asynchronous=False,
                                                                                 autocommit=True,
                                                                                 restrictions=restrictions,
                                                                                 currency=clans_relations.CURRENCY.ACTION_POINTS)

        return status

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        points = cls.action_points_per_step(raw_ability_power,
                                            bonus=emissary.protectorat_event_bonus() if emissary else 0)
        return f'Приносит гильдии дополнительно {points} очков действий каждый час.'


class PlaceEffectEvent(EventBase):
    __slots__ = ('effect_id',)

    def __init__(self, effect_id=None, **kwargs):
        super().__init__(**kwargs)
        self.effect_id = effect_id

    def attribute(self, event):
        return self.ATTRIBUTE

    def _effect_value(self, event):
        raise NotImplementedError

    def add_effect(self, event):
        if self.effect_id is not None:
            return

        self.effect_id = places_logic.register_effect(place_id=event.emissary.place_id,
                                                      attribute=self.attribute(event),
                                                      value=self._effect_value(event),
                                                      name='эмиссар [{}] {}'.format(clans_storage.infos[event.emissary.clan_id].abbr,
                                                                                    event.emissary.name),
                                                      refresh_effects=True,
                                                      refresh_places=True,
                                                      info={'source': 'emissaries_events',
                                                            'emissary': event.emissary_id,
                                                            'event': event.id})

    def remove_effect(self, emissary):
        if self.effect_id is None:
            return

        places_logic.remove_effect(self.effect_id,
                                   place_id=emissary.place_id,
                                   refresh_effects=True,
                                   refresh_places=True)

        self.effect_id = None

    def is_effect_allowed(self, emissary):
        raise NotImplementedError

    def after_create(self, event):
        if self.is_effect_allowed(event.emissary):
            self.add_effect(event)

    def sync_effect(self, event):
        if self.is_effect_allowed(event.emissary):
            self.add_effect(event)
        else:
            self.remove_effect(event.emissary)

    def on_step(self, event):
        self.sync_effect(event)
        return True

    def on_cancel(self, event):
        self.remove_effect(event.emissary)
        return True

    def on_finish(self, event):
        self.remove_effect(event.emissary)
        return True

    def serialize(self):
        data = super().serialize()
        data['data'] = {'effect_id': self.effect_id}
        return data

    @classmethod
    def deserialize(cls, data):
        return cls(raw_ability_power=data['raw_ability_power'],
                   effect_id=data['data']['effect_id'])

    def __eq__(self, other):
        return (super().__eq__(other) and
                self.effect_id == other.effect_id)


class CountedMixin:

    CURRENCY = NotImplemented

    @classmethod
    def minimum_poins_a_day(cls):
        return tt_emissaries_constants.STANDART_LIMITED_TASK_POINTS_MINIMUM

    @classmethod
    def maximum_points_a_day(cls):
        return tt_emissaries_constants.STANDART_LIMITED_TASK_POINTS_MAXIMUM

    @classmethod
    def tokens_per_day(cls, raw_ability_power, bonus):
        return cls.actual_value(raw_ability_power,
                                cls.minimum_poins_a_day(),
                                cls.maximum_points_a_day(),
                                bonus=bonus,
                                round=lambda value: round(value, 4))

    def resource_id(self, emissary):
        return logic.resource_id(clan_id=emissary.clan_id,
                                 place_id=emissary.place_id)

    def points_per_step(self, bonus):
        tokens_per_day = self.tokens_per_day(self.raw_ability_power, bonus=bonus)
        return int(math.ceil(tokens_per_day / 24 * tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER))

    def change_points(self, emissary, amount):
        logic.change_event_points(resource_id=self.resource_id(emissary),
                                  type='on_step_update',
                                  currency=self.CURRENCY,
                                  amount=amount)

    def is_effect_allowed(self, emissary):
        points = tt_services.events_currencies.cmd_balance(self.resource_id(emissary), currency=self.CURRENCY)
        return tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER <= points

    def actual_info(self, emissary):
        points = tt_services.events_currencies.cmd_balance(self.resource_id(emissary), currency=self.CURRENCY)
        effects_number = points / tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER

        return f'Накопившееся количество срабатываний: {effects_number:.2f}'

    def actual_info_help(self):
        return 'Эффект мероприятия применится, как только количество срабатываний превысит 1 и выполнятся специфичные для мероприятия условия.'


class BaseCountedEvent(CountedMixin, PlaceEffectEvent):
    __slots__ = ()

    CURRENCY = NotImplemented
    HAS_PROTECTORAT_BONUS = True

    def _effect_value(self, event):
        return event.emissary.clan_id

    def after_create(self, event):
        # даём очки на срабатывание вперёд, чтобы сразу начинало действовать
        # кроме того, это снимает проблему последних часов,
        # так как последние очки (а значит и последний токен) будут начислены сразу перед окончанием мерприятия
        # по факту получается, что даётся немного больше токенов, чем должно быть
        # если окажется, что это слишком большой бонус, можно давать на очки ровно на токен больше необходимого
        self.change_points(event.emissary, amount=tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER)
        super().after_create(event)

    def on_step(self, event):
        self.change_points(event.emissary,
                           amount=self.points_per_step(bonus=event.emissary.protectorat_event_bonus()))
        return super().on_step(event)

    def on_monitoring(self, event):
        self.sync_effect(event)


class TaskBoardUpdating(BaseCountedEvent):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.TASK_BOARD_UPDATING
    CURRENCY = relations.EVENT_CURRENCY.TASK_BOARD
    ATTRIBUTE = places_relations.ATTRIBUTE.TASK_BOARD

    @classmethod
    def minimum_poins_a_day(cls):
        return tt_clans_constants.FIGHTERS_TO_EMISSARY

    @classmethod
    def maximum_points_a_day(cls):
        return 5 * tt_clans_constants.FIGHTERS_TO_EMISSARY

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):

        if emissary is not None:
            places = places_logic.task_board_places(emissary.place)

            places_text = 'Города:' + ', '.join(sorted(place.name for place in places))

        else:
            places_text = ''

        tokens_per_day = cls.tokens_per_day(raw_ability_power,
                                            bonus=emissary.protectorat_event_bonus() if emissary else 0)

        return f'Герои гильдии не бездельничают в городе и {tt_emissaries_constants.TASK_BOARD_PLACES_NUMBER - 1} ближайших городах (по манхеттенскому расстоянию). Количество срабатываний в сутки: {tokens_per_day}. {places_text}'


class FastTransportation(BaseCountedEvent):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.FAST_TRANSPORTATION
    CURRENCY = relations.EVENT_CURRENCY.FAST_TRANSPORTATION
    ATTRIBUTE = places_relations.ATTRIBUTE.FAST_TRANSPORTATION

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        points = cls.tokens_per_day(raw_ability_power,
                                    bonus=emissary.protectorat_event_bonus() if emissary else 0)
        return f'Предоставляет героям гильдии безопасный путь до следующего города. Количество срабатываний в сутки: {points}.'


class CompanionsSupport(BaseCountedEvent):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.COMPANIONS_SUPPORT
    CURRENCY = relations.EVENT_CURRENCY.COMPANIONS_SUPPORT
    ATTRIBUTE = places_relations.ATTRIBUTE.COMPANIONS_SUPPORT

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        points = cls.tokens_per_day(raw_ability_power,
                                    bonus=emissary.protectorat_event_bonus() if emissary else 0)
        health = c.COMPANIONS_HEAL_AMOUNT

        return f'Лечит спутников героя при посещении города на {health} здоровья. Количество срабатываний в сутки: {points}.'


class ArtisansSupport(PlaceEffectEvent):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.ARTISANS_SUPPORT
    ATTRIBUTE = places_relations.ATTRIBUTE.PRODUCTION
    HAS_PROTECTORAT_BONUS = True

    @classmethod
    def direct_effect_value(cls, raw_ability_power, bonus):
        return cls.actual_value(raw_ability_power,
                                int(math.ceil(tt_emissaries_constants.PLACE_EVENT_MIN_EFFECT_POWER * c.PLACE_GOODS_BONUS)),
                                int(math.ceil(tt_emissaries_constants.PLACE_EVENT_MAX_EFFECT_POWER * c.PLACE_GOODS_BONUS)),
                                bonus=bonus)

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        production = cls.direct_effect_value(raw_ability_power,
                                             bonus=emissary.protectorat_event_bonus() if emissary else 0)
        return f'Увеличивает производство города на {production}.'

    def is_effect_allowed(self, emissary):
        return emissary.is_place_leader()

    def _effect_value(self, event):
        return self.direct_effect_value(self.raw_ability_power,
                                        bonus=event.emissary.protectorat_event_bonus() if event.emissary else 0)


class PublicOpinionManagement(PlaceEffectEvent):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.PUBLIC_OPINION_MANAGEMENT
    ATTRIBUTE = places_relations.ATTRIBUTE.STABILITY
    HAS_PROTECTORAT_BONUS = True

    @classmethod
    def direct_effect_value(cls, raw_ability_power, bonus):
        return cls.actual_value(raw_ability_power,
                                tt_emissaries_constants.PLACE_EVENT_MIN_EFFECT_POWER * c.PLACE_STABILITY_UNIT,
                                tt_emissaries_constants.PLACE_EVENT_MAX_EFFECT_POWER * c.PLACE_STABILITY_UNIT,
                                bonus=bonus,
                                round=lambda value: round(value, 4))

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        stability = cls.direct_effect_value(raw_ability_power,
                                            bonus=emissary.protectorat_event_bonus() if emissary else 0) * 100
        return f'Увеличивает стабильность города на {stability:.2f}%.'

    def is_effect_allowed(self, emissary):
        return emissary.is_place_leader()

    def _effect_value(self, event):
        return self.direct_effect_value(self.raw_ability_power,
                                        bonus=event.emissary.protectorat_event_bonus() if event.emissary else 0)


class Patronage(PlaceEffectEvent):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.PATRONAGE
    ATTRIBUTE = places_relations.ATTRIBUTE.CULTURE
    HAS_PROTECTORAT_BONUS = True

    @classmethod
    def direct_effect_value(cls, raw_ability_power, bonus):
        return cls.actual_value(raw_ability_power,
                                tt_emissaries_constants.PLACE_EVENT_MIN_EFFECT_POWER * c.PLACE_CULTURE_FROM_BEST_PERSON,
                                tt_emissaries_constants.PLACE_EVENT_MAX_EFFECT_POWER * c.PLACE_CULTURE_FROM_BEST_PERSON,
                                bonus=bonus,
                                round=lambda value: round(value, 4))

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        culture = cls.direct_effect_value(raw_ability_power,
                                          bonus=emissary.protectorat_event_bonus() if emissary else 0) * 100
        return f'Увеличивает культуру города на {culture:.2f}%.'

    def is_effect_allowed(self, emissary):
        return emissary.is_place_leader()

    def _effect_value(self, event):
        return self.direct_effect_value(self.raw_ability_power,
                                        bonus=event.emissary.protectorat_event_bonus() if event.emissary else 0)


class PatrioticPatronage(PlaceEffectEvent):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.PATRIOTIC_PATRONAGE
    HAS_PROTECTORAT_BONUS = True

    def attribute(self, event):
        return getattr(places_relations.ATTRIBUTE, 'DEMOGRAPHICS_PRESSURE_{}'.format(event.emissary.race.name))

    @classmethod
    def direct_effect_value(cls, raw_ability_power, bonus):
        return cls.actual_value(raw_ability_power,
                                tt_emissaries_constants.RACE_PRESSURE_MODIFIER_MIN,
                                tt_emissaries_constants.RACE_PRESSURE_MODIFIER_MAX,
                                bonus=bonus,
                                round=lambda value: round(value, 4))

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        culture = cls.direct_effect_value(raw_ability_power,
                                          bonus=emissary.protectorat_event_bonus() if emissary else 0) * 100
        return f'Увеличивает давление расы эмиссара в городе на {culture:.2f}%.'

    def is_effect_allowed(self, emissary):
        return emissary.is_place_leader()

    def _effect_value(self, event):
        return self.direct_effect_value(self.raw_ability_power,
                                        bonus=event.emissary.protectorat_event_bonus() if event.emissary else 0)


class GloryOfTheKeepers(CountedMixin, EventBase):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.GLORY_OF_THE_KEEPERS
    CURRENCY = relations.EVENT_CURRENCY.GLORY_OF_THE_KEEPERS
    HAS_PROTECTORAT_BONUS = True

    @classmethod
    def minimum_poins_a_day(cls):
        return 1

    @classmethod
    def maximum_points_a_day(cls):
        return tt_clans_constants.FIGHTERS_TO_EMISSARY

    def resource_id(self, emissary):
        return logic.resource_id(clan_id=emissary.clan_id,
                                 place_id=None)

    def get_receiver(self, event):
        memberships = clans_logic.get_clan_memberships(event.emissary.clan_id)

        property_name = accounts_tt_services.PLAYER_PROPERTIES.last_card_by_emissary

        accounts_properties = accounts_tt_services.players_properties.cmd_get_properties({account_id: [property_name]
                                                                                          for account_id in memberships.keys()})

        allowed_accounts = [account_id
                            for account_id, properties in accounts_properties.items()
                            if properties.last_card_by_emissary + conf.settings.CARD_RECEIVING_BY_EMISSARY_TIMEOUT < time.time()]

        if not allowed_accounts:
            return None

        receiver_id = random.choice(allowed_accounts)

        return accounts_prototypes.AccountPrototype.get_by_id(receiver_id)

    def on_step(self, event):
        if not event.emissary.is_place_leader():
            return True

        self.change_points(event.emissary, amount=self.points_per_step(bonus=event.emissary.protectorat_event_bonus()))

        while self.is_effect_allowed(event.emissary):
            account = self.get_receiver(event)

            if account is None:
                return True

            cards_logic.give_new_cards(account_id=account.id,
                                       operation_type='give-new-card-by-emissary',
                                       allow_premium_cards=account.cards_receive_mode().is_ALL,
                                       available_for_auction=account.is_premium,
                                       number=1)

            logic.withdraw_event_points_by_resource_id(self.resource_id(event.emissary), currency=self.CURRENCY)

            accounts_tt_services.players_properties.cmd_set_property(object_id=account.id,
                                                                     name=accounts_tt_services.PLAYER_PROPERTIES.last_card_by_emissary,
                                                                     value=time.time())

            logic.send_event_success_message(event, account, suffix='вы получили дополнительную Карту Судьбы.')

        return True

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        points = cls.tokens_per_day(raw_ability_power,
                                    bonus=emissary.protectorat_event_bonus() if emissary else 0)
        return f'Случайный игрок гильдии периодически получает карту судьбы. Свойства карты такие же, как и при получении их обычным образом. Количество срабатываний в сутки: {points}. С помощью мероприятий Хранитель не может получить более одной карты в 12 часов.'


class Revolution(EventBase):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.REVOLUTION

    BASE_CYCLE_LENGTH = 7

    POWER_BARRIER = 0

    @classmethod
    def max_event_length(cls):
        return cls.BASE_CYCLE_LENGTH

    @classmethod
    def is_available(cls, emissary, active_events):
        if not super().is_available(emissary, active_events):
            return False

        return emissary.can_participate_in_pvp()

    @contextlib.contextmanager
    def on_create(self, emissary):

        if emissary.place.attrs.clan_protector == emissary.clan_id:
            raise exceptions.OnEventCreateError(message='already protector')

        yield

    def message(self, template, emissary):
        clan_info = clans_storage.infos[emissary.clan_id]
        place = emissary.place

        return linguistics_logic.technical_render(template,
                                                  {'emissary': emissary.utg_name_form,
                                                   'clan': lexicon_dictionary.text(clan_info.name),
                                                   'place': place.utg_name_form})

    def after_create(self, event):
        message = self.message('Эмиссар [emissary] из гильдии «[clan]» пытается установить протекторат над [place|тв]',
                               event.emissary)

        logic.notify_clans(place_id=event.emissary.place_id,
                           exclude_clans_ids=(),
                           message=message,
                           roles=clans_relations.ROLES_TO_NOTIFY)

    def message_on_fail(self, event):
        message = self.message('Эмиссар [emissary] из гильдии «[clan]» не [смог|emissary] установить протекторат над [place|тв]',
                               event.emissary)

        logic.notify_clans(place_id=event.emissary.place_id,
                           exclude_clans_ids=(),
                           message=message,
                           roles=clans_relations.ROLES_TO_NOTIFY)

    def message_on_success(self, event):
        message = self.message('Эмиссар [emissary] из гильдии «[clan]» [установил|emissary] протекторат над [place|тв]',
                               event.emissary)

        logic.notify_clans(place_id=event.emissary.place_id,
                           exclude_clans_ids=(),
                           message=message,
                           roles=clans_relations.ROLES_TO_NOTIFY)

    def on_finish(self, event):

        protector_id = event.emissary.place.attrs.clan_protector

        if protector_id == event.emissary.clan_id:
            self.message_on_success(event)
            return True

        if not event.emissary.is_place_leader():
            self.message_on_fail(event)
            return False

        emissaries = storage.emissaries.emissaries_in_place(event.emissary.place_id)

        powers = politic_power_logic.get_emissaries_power([emissary.id for emissary in emissaries])

        if powers[event.emissary.id] <= self.POWER_BARRIER:
            self.message_on_fail(event)
            return False

        for emissary in emissaries:
            if emissary.clan_id != protector_id:
                continue

            if powers[event.emissary.id] < powers[emissary.id]:
                self.message_on_fail(event)
                return False

        places_logic.register_effect(place_id=event.emissary.place_id,
                                     attribute=places_relations.ATTRIBUTE.CLAN_PROTECTOR,
                                     value=event.emissary.clan_id,
                                     name='эмиссар [{}] {}'.format(clans_storage.infos[event.emissary.clan_id].abbr,
                                                                   event.emissary.name),
                                     refresh_effects=True,
                                     refresh_places=True,
                                     info={'source': 'emissaries_events',
                                           'emissary': event.emissary_id,
                                           'event': event.id})

        self.message_on_success(event)

        clans_tt_services.chronicle.cmd_add_event(clan=clans_storage.infos[event.emissary.clan_id],
                                                  event=clans_relations.EVENT.PROTECTORAT_ESTABLISHED,
                                                  tags=[event.emissary.place.meta_object().tag,
                                                        event.emissary.meta_object().tag],
                                                  message=f'Установлен протекторат над городом «{event.emissary.place.name}»')

        return True

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        text = f'Делает гильдию эмиссара протектором города, в котором тот находится. Проваливается, если в момент завершения мероприятия эмиссар не находится в числе лидеров города, либо имеет не более {cls.POWER_BARRIER} влияния, либо имеет меньше влияния, чем эмиссар текущей гильдии-протектора. При начале и завершении мероприятия будет отправлено соответствующее сообщение всем членам гильдий (с эмиссарами в городе) с правом «{clans_relations.PERMISSION.RECEIVE_MESSAGES.text}». Начать мероприятие может только эмиссар с суммой способностей больше {tt_emissaries_constants.ATTRIBUTES_FOR_PARTICIPATE_IN_PVP}'
        return text


class DarkRituals(CountedMixin, EventBase):
    __slots__ = ()

    TYPE = relations.EVENT_TYPE.DARK_RITUALS
    CURRENCY = relations.EVENT_CURRENCY.DARK_RITUALS
    ONLY_FOR_PROTECTORAT = True

    @classmethod
    def minimum_poins_a_day(cls):
        return 0.5

    @classmethod
    def maximum_points_a_day(cls):
        # С изменением этого параметра необходимо быть очень аккуратным,
        # так как бесконтрольня раздача подписки очень опасна
        return 1.5

    def resource_id(self, emissary):
        return logic.resource_id(clan_id=emissary.clan_id,
                                 place_id=None)

    def get_receiver(self, event):
        memberships = clans_logic.get_clan_memberships(event.emissary.clan_id)

        memberships = {key: record
                       for key, record in memberships.items()
                       if not record.is_freezed()}

        property_name = accounts_tt_services.PLAYER_PROPERTIES.last_premium_by_emissary

        accounts_properties = accounts_tt_services.players_properties.cmd_get_properties({account_id: [property_name]
                                                                                          for account_id in memberships.keys()})

        allowed_accounts = [account_id
                            for account_id, properties in accounts_properties.items()
                            if properties.last_premium_by_emissary + conf.settings.PREMIUM_RECEIVING_BY_EMISSARY_TIMEOUT < time.time()]

        accounts_query = accounts_prototypes.AccountPrototype._db_filter(id__in=allowed_accounts)

        accounts = accounts_prototypes.AccountPrototype.from_query(accounts_query)

        accounts = [account for account in accounts if not account.is_premium_infinit]

        if not accounts:
            return None

        return random.choice(accounts)

    def on_step(self, event):
        if event.emissary.clan_id != event.emissary.place.attrs.clan_protector:
            return True

        if not event.emissary.is_place_leader():
            return True

        self.change_points(event.emissary, amount=self.points_per_step(bonus=0))

        while self.is_effect_allowed(event.emissary):
            account = self.get_receiver(event)

            if account is None:
                return True

            # TODO: проблемное место, но пересечение с другой логикой досаточно маловероятно,
            # чтобы отложить правильную реализацию до момента рефакторинга аккаунтов (см. gh-2480 для подробной информации)
            account.prolong_premium(1)
            account.save()

            logic.withdraw_event_points_by_resource_id(self.resource_id(event.emissary), currency=self.CURRENCY)

            accounts_tt_services.players_properties.cmd_set_property(object_id=account.id,
                                                                     name=accounts_tt_services.PLAYER_PROPERTIES.last_premium_by_emissary,
                                                                     value=time.time())

            logic.send_event_success_message(event, account, suffix='вы получили 1 день подписки.')

        return True

    @classmethod
    def effect_description(cls, emissary, raw_ability_power):
        points = cls.tokens_per_day(raw_ability_power,
                                    bonus=0)
        return f'Случайный игрок гильдии периодически получает 1 день подписки. Игрок выбирается из всех членов гильдии кроме замороженных и обладающих вечной подпиской. Количество срабатываний в сутки: {points}. Один и тот же Хранитель неможет получить день подписки не чаще одного раза в 12 часов.'


TYPES = {event_class.TYPE: event_class
         for event_class in utils_discovering.discover_classes(list(globals().values()), EventBase)
         if event_class not in (BaseCountedEvent, PlaceEffectEvent)}
