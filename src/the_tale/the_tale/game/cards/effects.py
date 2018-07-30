
import smart_imports

smart_imports.all()


class BaseEffect:
    __slots__ = ()

    FORM_TEMPLATE = 'cards/effect_form.html'

    def __init__(self):
        pass

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    def activate(self, hero, card, data):
        data['hero_id'] = hero.id
        data['account_id'] = hero.account_id
        data['card'] = {'id': card.uid.hex,
                        'data': card.serialize()}

        card_task = postponed_tasks.UseCardTask(processor_id=card.type.value,
                                                hero_id=hero.id,
                                                data=data)

        task = PostponedTaskPrototype.create(card_task)

        amqp_environment.environment.workers.supervisor.cmd_logic_task(hero.account_id, task.id)

        return task

    def use(self, *argv, **kwargs):
        raise NotImplementedError()

    def check_hero_conditions(self, hero, data):
        return logic.has_cards(owner_id=hero.account_id, cards_ids=[uuid.UUID(data['card']['id'])])

    def hero_actions(self, hero, data):
        card = objects.Card.deserialize(uuid.UUID(data['card']['id']), data['card']['data'])

        logic.change_cards(owner_id=hero.account_id,
                           operation_type='use-card',
                           to_remove=[card])

        hero.statistics.change_cards_used(1)

    def create_card(self, type, available_for_auction, uid=None):
        return objects.Card(type=type,
                            available_for_auction=available_for_auction,
                            uid=uid if uid else uuid.uuid4())

    def name_for_card(self, card):
        return card.type.text

    def available(self, card):
        return True

    def item_full_type(self, card):
        return '{}'.format(card.type.value)

    def full_type_names(self, card_type):
        return {'{}'.format(card_type.value): card_type.text}

    def get_dialog_info(self, card, hero):
        return None


class ModificatorBase(BaseEffect):
    __slots__ = ('base', 'level')

    def __init__(self, base, level):
        self.base = base
        self.level = level

    @property
    def modificator(self):
        return self.base * tt_cards_constants.LEVEL_MULTIPLIERS[self.level - 1]

    @property
    def upper_modificator(self):
        return int(math.ceil(self.modificator))


class LevelUp(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    def __init__(self):
        pass

    DESCRIPTION = 'Герой получает новый уровень. Накопленный опыт не сбрасывается.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        task.hero.increment_level(send_message=False)
        storage.save_bundle_data(bundle_id=task.hero.actions.current_action.bundle_id)
        return task.logic_result()


class AddExperience(ModificatorBase):
    __slots__ = ()

    @property
    def DESCRIPTION(self):
        return 'Увеличивает опыт, который герой получит за выполнение текущего задания, на %(experience)d единиц.' % {'experience': self.modificator}

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        if not task.hero.quests.has_quests:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='У героя нет задания.')

        task.hero.quests.current_quest.current_info.experience_bonus += self.modificator
        task.hero.quests.mark_updated()

        return task.logic_result()


class AddCompanionExpirence(ModificatorBase):
    __slots__ = ()

    @property
    def DESCRIPTION(self):
        return 'Увеличивает опыт спутника на %(experience)d единиц.' % {'experience': self.modificator}

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613

        if task.hero.companion is None:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='У героя сейчас нет спутника.')

        task.hero.companion.add_experience(self.modificator, force=True)

        return task.logic_result()


class AddPoliticPower(ModificatorBase):
    __slots__ = ()

    @property
    def DESCRIPTION(self):
        return 'Увеличивает влияние текущего задания, на %(power)d единиц (учтите, что итоговое влияние задания зависит и от влиятельности вашего героя).' % {'power': self.modificator}

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        if not task.hero.quests.has_quests:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='У героя нет задания.')

        task.hero.quests.current_quest.current_info.power_bonus += self.modificator
        task.hero.quests.mark_updated()

        return task.logic_result()


class AddBonusEnergy(ModificatorBase):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    @property
    def DESCRIPTION(self):
        return 'Вы получаете %(energy)d единиц энергии.' % {'energy': self.modificator}

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        game_tt_services.energy.cmd_change_balance(account_id=task.hero.account_id,
                                                   type='card',
                                                   energy=int(self.modificator),
                                                   async=True,
                                                   autocommit=True)
        return task.logic_result()


class AddGold(ModificatorBase):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    @property
    def DESCRIPTION(self):
        return 'Герой получает %(gold)d монет.' % {'gold': self.modificator}

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        task.hero.change_money(heroes_relations.MONEY_SOURCE.EARNED_FROM_HELP, self.modificator)
        return task.logic_result()


class ChangeHabit(ModificatorBase):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    @property
    def DESCRIPTION(self):
        return 'Изменяет черту героя на {} единиц в указанную в названии сторону.'.format(int(self.modificator))

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        card = objects.Card.deserialize(uuid.UUID(task.data['card']['id']), task.data['card']['data'])

        habit = game_relations.HABIT_TYPE(card.data['habit_id'])

        delta = card.data['direction'] * self.modificator

        old_habits = (task.hero.habit_honor.raw_value, task.hero.habit_peacefulness.raw_value)

        task.hero.change_habits(habit, delta)

        if old_habits == (task.hero.habit_honor.raw_value, task.hero.habit_peacefulness.raw_value):
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Применение карты никак не изменит черты героя.')

        return task.logic_result(message='Черта героя изменена.')

    def allowed_habits(self):
        return game_relations.HABIT_TYPE.records

    def allowed_directions(self):
        return (-1, 1)

    def create_card(self, type, available_for_auction, habit=None, direction=None, uid=None):
        if habit is None:
            habit = random.choice(self.allowed_habits())

        if direction is None:
            direction = random.choice(self.allowed_directions())

        return objects.Card(type=type,
                            available_for_auction=available_for_auction,
                            data={'habit_id': habit.value,
                                  'direction': direction},
                            uid=uid if uid else uuid.uuid4())

    def _item_full_type(self, type, habit_id, direction):
        return '{}-{}-{:+d}'.format(type.value, habit_id, direction)

    def item_full_type(self, card):
        return self._item_full_type(card.type, card.data['habit_id'], card.data['direction'])

    def full_type_names(self, card_type):
        names = {}

        for direction in self.allowed_directions():
            for habit in self.allowed_habits():
                full_type = self._item_full_type(card_type, habit.value, direction)
                names[full_type] = self._name_for_card(card_type, habit.value, direction)

        return names

    def _name_for_card(self, type, habit_id, direction):
        return '{}: {} {:+d}'.format(type.text,
                                     game_relations.HABIT_TYPE(habit_id).text,
                                     int(self.modificator * direction))

    def name_for_card(self, card):
        return self._name_for_card(card.type, card.data['habit_id'], card.data['direction'])


class ChangePreference(BaseEffect):
    __slots__ = ()

    DESCRIPTION = 'Позволяет изменить указанное в названии предпочтение героя.'

    def get_form(self, card, hero, data):
        preference = heroes_relations.PREFERENCE_TYPE(card.data['preference_id'])

        return preferences_forms.FORMS[preference](data, hero=hero)

    def get_dialog_info(self, card, hero):
        preference = heroes_relations.PREFERENCE_TYPE(card.data['preference_id'])
        return 'heroes/preferences/{}.html'.format(preference.base_name)

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613

        card = objects.Card.deserialize(uuid.UUID(task.data['card']['id']), task.data['card']['data'])

        preference = heroes_relations.PREFERENCE_TYPE(card.data['preference_id'])

        if not task.hero.preferences.set(preferences_type=preference, value=task.data.get('value')):
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR,
                                     message='Мы не можете изменить предпочтение героя на то же самое.')

        storage.save_bundle_data(bundle_id=task.hero.actions.current_action.bundle_id)

        return task.logic_result()

    def allowed_preferences(self):
        return heroes_relations.PREFERENCE_TYPE.records

    def create_card(self, type, available_for_auction, preference=None, uid=None):
        if preference is None:
            preference = random.choice(self.allowed_preferences())

        return objects.Card(type=type,
                            available_for_auction=available_for_auction,
                            data={'preference_id': preference.value},
                            uid=uid if uid else uuid.uuid4())

    def _item_full_type(self, type, preference_id):
        return '{}-{}'.format(type.value, preference_id)

    def item_full_type(self, card):
        return self._item_full_type(card.type, card.data['preference_id'])

    def full_type_names(self, card_type):
        names = {}

        for preference in self.allowed_preferences():
            full_type = self._item_full_type(card_type, preference.value)
            names[full_type] = self._name_for_card(card_type, preference.value)

        return names

    def _name_for_card(self, type, preference_id):
        return type.text + ': ' + heroes_relations.PREFERENCE_TYPE(preference_id).text

    def name_for_card(self, card):
        return self._name_for_card(card.type, card.data['preference_id'])


class ChangeAbilitiesChoices(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Изменяет список предлагаемых герою способностей (при выборе новой способности).'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        if not task.hero.abilities.rechooce_choices():
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Герой не может изменить выбор способностей (возможно, больше не из чего выбирать).')

        storage.save_bundle_data(bundle_id=task.hero.actions.current_action.bundle_id)

        return task.logic_result()


class ResetAbilities(BaseEffect):
    __slots__ = ()
    DESCRIPTION = 'Сбрасывает все способности героя.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        if task.hero.abilities.is_initial_state():
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Способности героя уже сброшены.')

        task.hero.abilities.reset()

        storage.save_bundle_data(bundle_id=task.hero.actions.current_action.bundle_id)

        return task.logic_result()


class ChangeItemOfExpenditure(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    @property
    def DESCRIPTION(self):
        return 'Меняет текущую цель трат героя на указанную в названии'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613

        card = objects.Card.deserialize(uuid.UUID(task.data['card']['id']), task.data['card']['data'])

        item = heroes_relations.ITEMS_OF_EXPENDITURE(card.data['item_id'])

        if task.hero.next_spending == item:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Герой уже копит деньги на эту цель.')

        if item.is_HEAL_COMPANION and task.hero.companion is None:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='У героя нет спутника, лечить некого.')

        task.hero.next_spending = item
        task.hero.quests.mark_updated()
        return task.logic_result()

    def allowed_items(self):
        return [item for item in heroes_relations.ITEMS_OF_EXPENDITURE.records
                if not item.is_USELESS and not item.is_IMPACT]

    def create_card(self, type, available_for_auction, item=None, uid=None):
        if item is None:
            item = random.choice(self.allowed_items())

        return objects.Card(type=type,
                            available_for_auction=available_for_auction,
                            data={'item_id': item.value},
                            uid=uid if uid else uuid.uuid4())

    def _item_full_type(self, type, item_id):
        return '{}-{}'.format(type.value, item_id)

    def item_full_type(self, card):
        return self._item_full_type(card.type, card.data['item_id'])

    def full_type_names(self, card_type):
        names = {}

        for item in self.allowed_items():
            full_type = self._item_full_type(card_type, item.value)
            names[full_type] = self._name_for_card(card_type, item.value)

        return names

    def _name_for_card(self, type, item_id):
        return type.text + ': ' + heroes_relations.ITEMS_OF_EXPENDITURE(item_id).text

    def name_for_card(self, card):
        return self._name_for_card(card.type, card.data['item_id'])


class RepairRandomArtifact(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Чинит случайный артефакт из экипировки героя.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        choices = [item for item in list(task.hero.equipment.values()) if item.integrity < item.max_integrity]

        if not choices:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Экипировка не нуждается в ремонте.')

        artifact = random.choice(choices)

        artifact.repair_it()

        return task.logic_result(message='Целостность артефакта %(artifact)s полностью восстановлена.' % {'artifact': artifact.html_label()})


class RepairAllArtifacts(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Чинит все артефакты из экипировки героя.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613

        if not [item for item in list(task.hero.equipment.values()) if item.integrity < item.max_integrity]:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Экипировка не нуждается в ремонте.')

        for item in list(task.hero.equipment.values()):
            item.repair_it()

        return task.logic_result()


class CancelQuest(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Отменяет текущее задание героя. Если герой выполняет цепочку заданий, отменяется вся цепочка.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        if not task.hero.quests.has_quests:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='У героя нет задания.')

        task.hero.quests.pop_quest()
        task.hero.quests.mark_updated()

        return task.logic_result()


class GetArtifact(BaseEffect):
    __slots__ = ('type',)

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    class ARTIFACT_TYPE_CHOICES(rels_django.DjangoEnum):
        rarity = rels.Column(unique=False, single_type=False)
        description = rels.Column()

        records = (('LOOT', 0, 'лут', artifacts_relations.RARITY.NORMAL, 'Герой получает случайный бесполезный предмет.'),
                   ('COMMON', 1, 'обычные', artifacts_relations.RARITY.NORMAL, 'Герой получает случайный артефакт лучше экипированного, близкий архетипу героя.'),
                   ('RARE', 2, 'редкие', artifacts_relations.RARITY.RARE, 'Герой получает случайный редкий артефакт лучше экипированного, близкий архетипу героя.'),
                   ('EPIC', 3, 'эпические', artifacts_relations.RARITY.EPIC, 'Герой получает случайный эпический артефакт лучше экипированного, близкий архетипу героя.'))

    def __init__(self, type):
        super().__init__()
        self.type = type

    @property
    def DESCRIPTION(self):
        return self.ARTIFACT_TYPE_CHOICES(self.type).description

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        artifact_type = self.ARTIFACT_TYPE_CHOICES(self.type)

        if artifact_type.is_LOOT:
            artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.loot,
                                                                               task.hero.level,
                                                                               rarity=artifact_type.rarity)
            task.hero.put_loot(artifact, force=True)
        else:
            artifact, unequipped, sell_price = task.hero.receive_artifact(equip=False,
                                                                          better=True,
                                                                          prefered_slot=False,
                                                                          prefered_item=True,
                                                                          archetype=True,
                                                                          rarity_type=artifact_type.rarity)

        task.hero.actions.request_replane()

        return task.logic_result(message='В рюкзаке героя появился новый артефакт: %(artifact)s.' % {'artifact': artifact.html_label()})


class InstantMonsterKill(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Мгновенно убивает монстра, с которым сражается герой.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613

        if not task.hero.actions.current_action.TYPE.is_BATTLE_PVE_1X1:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Герой ни с кем не сражается.')

        task.hero.actions.current_action.bit_mob(task.hero.actions.current_action.mob.max_health)

        return task.logic_result()


class KeepersGoods(ModificatorBase):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Place(data)

    @property
    def DESCRIPTION(self):
        return 'Создаёт в указанном городе %(goods)d «даров Хранителей». Город будет постепенно переводить их в продукцию, пока дары не кончатся.' % {'goods': self.modificator}

    def use(self, task, storage, highlevel=None, **kwargs):  # pylint: disable=R0911,W0613

        place_id = task.data.get('value')

        if place_id not in places_storage.places:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Город не найден.')

        if task.step.is_LOGIC:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.HIGHLEVEL)

        elif task.step.is_HIGHLEVEL:
            place = places_storage.places[place_id]

            place.attrs.keepers_goods += self.modificator
            place.refresh_attributes()

            places_logic.save_place(place)

            places_storage.places.update_version()

            return task.logic_result()


class GiveStability(ModificatorBase):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Place(data)

    @property
    def DESCRIPTION(self):
        return 'Увеличивает стабильность в указанном городе на {0:.1f}%. Бонус будет уменьшаться по стандартным правилам изменения стабильности.'.format(self.modificator * 100)

    def use(self, task, storage, highlevel=None, **kwargs):  # pylint: disable=R0911,W0613

        place_id = task.data.get('value')

        if place_id not in places_storage.places:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Город не найден.')

        if task.step.is_LOGIC:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.HIGHLEVEL)

        elif task.step.is_HIGHLEVEL:
            place = places_storage.places[place_id]

            place.effects.add(game_effects.Effect(name='Хранитель {}'.format(accounts_prototypes.AccountPrototype.get_by_id(task.hero_id).nick),
                                                  attribute=places_relations.ATTRIBUTE.STABILITY,
                                                  value=self.modificator,
                                                  delta=place.attrs.stability_renewing_speed))

            place.refresh_attributes()

            places_logic.save_place(place)

            places_storage.places.update_version()

            return task.logic_result()


class RepairBuilding(ModificatorBase):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Building(data)

    @property
    def DESCRIPTION(self):
        return 'Ремонтирует указанное строение на {}%. Целостность может накапливаться больше 100%.'.format(self.modificator * 100)

    def use(self, task, storage, highlevel=None, **kwargs):  # pylint: disable=R0911,W0613
        building_id = task.data.get('value')

        if building_id not in places_storage.buildings:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Строение не найдено.')

        if task.step.is_LOGIC:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.HIGHLEVEL)

        elif task.step.is_HIGHLEVEL:
            building = places_storage.buildings[building_id]

            building.repair(self.modificator)

            places_logic.save_building(building)

            return task.logic_result()


class AddPersonPower(ModificatorBase):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Person(data)

    @property
    def DESCRIPTION(self):
        return 'Моментально изменяет влияние Мастера на {} единиц в указанную в названии сторону. Влияние засчитывается так, как если бы герой имел Мастера в предпочтении.'.format(int(self.modificator))

    def use(self, task, storage, highlevel=None, **kwargs):  # pylint: disable=R0911,W0613

        card = objects.Card.deserialize(uuid.UUID(task.data['card']['id']), task.data['card']['data'])

        delta = card.data['direction'] * self.modificator

        person_id = task.data.get('value')

        if person_id not in persons_storage.persons:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Мастер не найден.')

        impacts = [game_tt_services.PowerImpact.hero_2_person(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                              hero_id=task.hero.id,
                                                              person_id=person_id,
                                                              amount=delta)]

        politic_power_logic.add_power_impacts(impacts)

        return task.logic_result(message='Влияние Мастера изменено')

    def allowed_directions(self):
        return (-1, 1)

    def create_card(self, type, available_for_auction, direction=None, uid=None):
        if direction is None:
            direction = random.choice(self.allowed_directions())

        return objects.Card(type=type,
                            available_for_auction=available_for_auction,
                            data={'direction': direction},
                            uid=uid if uid else uuid.uuid4())

    def _item_full_type(self, type, direction):
        return '{}-{:+d}'.format(type.value, direction)

    def item_full_type(self, card):
        return self._item_full_type(card.type, card.data['direction'])

    def full_type_names(self, card_type):
        names = {}

        for direction in self.allowed_directions():
            full_type = self._item_full_type(card_type, direction)
            names[full_type] = self._name_for_card(card_type, direction)

        return names

    def _name_for_card(self, type, direction):
        return '{}: {:+d}'.format(type.text, int(self.modificator * direction))

    def name_for_card(self, card):
        return self._name_for_card(card.type, card.data['direction'])


class AddPlacePower(ModificatorBase):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Place(data)

    @property
    def DESCRIPTION(self):
        return 'Моментально изменяет влияние города на {} единиц в указанную в названии сторону. Влияние засчитывается так, как если бы герой имел город в предпочтении.'.format(int(self.modificator))

    def use(self, task, storage, highlevel=None, **kwargs):  # pylint: disable=R0911,W0613

        card = objects.Card.deserialize(uuid.UUID(task.data['card']['id']), task.data['card']['data'])

        delta = card.data['direction'] * self.modificator

        place_id = task.data.get('value')

        if place_id not in places_storage.places:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Город не найден.')

        impacts = [game_tt_services.PowerImpact.hero_2_place(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                             hero_id=task.hero.id,
                                                             place_id=place_id,
                                                             amount=delta)]

        politic_power_logic.add_power_impacts(impacts)

        return task.logic_result(message='Влияние города изменено.')

    def allowed_directions(self):
        return (-1, 1)

    def create_card(self, type, available_for_auction, direction=None, uid=None):
        if direction is None:
            direction = random.choice(self.allowed_directions())

        return objects.Card(type=type,
                            available_for_auction=available_for_auction,
                            data={'direction': direction},
                            uid=uid if uid else uuid.uuid4())

    def _item_full_type(self, type, direction):
        return '{}-{:+d}'.format(type.value, direction)

    def item_full_type(self, card):
        return self._item_full_type(card.type, card.data['direction'])

    def full_type_names(self, card_type):
        names = {}

        for direction in self.allowed_directions():
            full_type = self._item_full_type(card_type, direction)
            names[full_type] = self._name_for_card(card_type, direction)

        return names

    def _name_for_card(self, type, direction):
        return '{}: {:+d}'.format(type.text, int(self.modificator * direction))

    def name_for_card(self, card):
        return self._name_for_card(card.type, card.data['direction'])


class PlaceFame(ModificatorBase):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Place(data)

    @property
    def DESCRIPTION(self):
        return 'Увеличивает известность героя в городе на {}'.format(int(self.modificator))

    @property
    def success_message(self):
        return 'Известность героя увеличена на {}'.format(int(self.modificator))

    def use(self, task, storage, **kwargs):
        place_id = task.data.get('value')

        if place_id not in places_storage.places:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Город не найден.')

        places_logic.add_fame(hero_id=task.hero_id, fames=[(place_id, self.modificator)])

        return task.logic_result(message=self.success_message)


class ShortTeleport(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Телепортирует героя до ближайшего города либо до ближайшей ключевой точки задания. Работает только во время движения по дорогам.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        if not task.hero.actions.current_action.TYPE.is_MOVE_TO:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Герой не находится в движении.')

        if not task.hero.actions.current_action.teleport_to_place(create_inplace_action=True):
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Телепортировать героя не получилось.')

        return task.logic_result()


class LongTeleport(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Телепортирует героя в конечную точку назначения либо до ближайшей ключевой точки задания. Работает только во время движения по дорогам.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613

        if not task.hero.actions.current_action.TYPE.is_MOVE_TO:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Герой не находится в движении.')

        if not task.hero.actions.current_action.teleport_to_end():
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Телепортировать героя не получилось.')

        return task.logic_result()


class SharpRandomArtifact(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Улучшает случайный артефакт из экипировки героя.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        artifact = random.choice(list(task.hero.equipment.values()))

        distribution = task.hero.preferences.archetype.power_distribution
        min_power, max_power = power.Power.artifact_power_interval(distribution, task.hero.level)

        artifact.sharp(distribution=distribution,
                       max_power=max_power,
                       force=True)

        return task.logic_result(message='Улучшена экипировка героя: %(artifact)s.' % {'artifact': artifact.html_label()})


class SharpAllArtifacts(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Улучшает все артефакты из экипировки героя.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613

        for artifact in list(task.hero.equipment.values()):
            distribution = task.hero.preferences.archetype.power_distribution
            min_power, max_power = power.Power.artifact_power_interval(distribution, task.hero.level)

            artifact.sharp(distribution=distribution,
                           max_power=max_power,
                           force=True)

        return task.logic_result(message='Вся экипировка героя улучшена.')


class GetCompanion(BaseEffect):
    __slots__ = ('rarity',)

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    def __init__(self, rarity, **kwargs):
        super().__init__(**kwargs)
        self.rarity = rarity

    @property
    def DESCRIPTION(self):
        return 'Герой получает спутника, указанного в названии карты. Если у героя уже есть спутник, он покинет героя.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        card = objects.Card.deserialize(uuid.UUID(task.data['card']['id']), task.data['card']['data'])

        companion = companions_logic.create_companion(companions_storage.companions[card.data['companion_id']])

        task.hero.set_companion(companion)

        return task.logic_result(message='Поздравляем! Ваш герой получил нового спутника.')

    def get_available_companions(self):
        available_companions = [companion
                                for companion in companions_storage.companions.enabled_companions()
                                if companion.rarity == self.rarity and companion.mode.is_AUTOMATIC]
        return available_companions

    def create_card(self, type, available_for_auction, companion=None, uid=None):
        if companion is None:
            available_companions = self.get_available_companions()
            companion = random.choice(available_companions)

        return objects.Card(type=type,
                            available_for_auction=available_for_auction,
                            data={'companion_id': companion.id},
                            uid=uid if uid else uuid.uuid4())

    def _item_full_type(self, type, companion_id):
        return '{}-{}'.format(type.value, companion_id)

    def item_full_type(self, card):
        return self._item_full_type(card.type, card.data['companion_id'])

    def full_type_names(self, card_type):
        names = {}

        # do not skip manual companions, since can be cards with them too
        # map every card rarity to every companions, since companions can change their rarity
        for companion in companions_storage.companions.enabled_companions():
            full_type = self._item_full_type(card_type, companion.id)
            names[full_type] = self._name_for_card(card_type, companion.id)

        return names

    def available(self, card):
        return bool(self.get_available_companions())

    def _name_for_card(self, type, companion_id):
        return type.text + ': ' + companions_storage.companions[companion_id].name

    def name_for_card(self, card):
        return self._name_for_card(card.type, card.data['companion_id'])


class ReleaseCompanion(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Спутник героя навсегда покидает его.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613

        if task.hero.companion is None:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='У героя сейчас нет спутника.')

        task.hero.add_message('companions_left', diary=True, companion_owner=task.hero, companion=task.hero.companion)
        task.hero.remove_companion()

        return task.logic_result(message='Спутник покинул героя.')


class FreezeCompanion(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Вы получаете карту призыва текущего спутника вашего героя. Спутник покидает героя. Слаженность спутника в карте не сохраняется. Возможность продать новую карту определяется возможностью продать текущую.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        if task.hero.companion is None:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='У героя сейчас нет спутника.')

        if not task.hero.companion.record.abilities.can_be_freezed():
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Текущий спутник не может вернуться в карту.')

        CARDS_BY_RARITIES = {companions_relations.RARITY.COMMON: types.CARD.GET_COMPANION_COMMON,
                             companions_relations.RARITY.UNCOMMON: types.CARD.GET_COMPANION_UNCOMMON,
                             companions_relations.RARITY.RARE: types.CARD.GET_COMPANION_RARE,
                             companions_relations.RARITY.EPIC: types.CARD.GET_COMPANION_EPIC,
                             companions_relations.RARITY.LEGENDARY: types.CARD.GET_COMPANION_LEGENDARY}

        card_type = CARDS_BY_RARITIES[task.hero.companion.record.rarity]

        used_card = objects.Card.deserialize(uuid.UUID(task.data['card']['id']), task.data['card']['data'])

        card = card_type.effect.create_card(type=card_type,
                                            available_for_auction=used_card.available_for_auction,
                                            companion=task.hero.companion.record)

        task.hero.add_message('companions_left', diary=True, companion_owner=task.hero, companion=task.hero.companion)
        task.hero.remove_companion()

        logic.change_cards(owner_id=task.hero.account_id,
                           operation_type='freeze-companion',
                           to_add=[card])

        return task.logic_result(message='Спутник покинул героя, вы получили карту спутника.')


class HealCompanion(ModificatorBase):
    __slots__ = ()

    @property
    def modificator(self):
        return int(math.ceil(super().modificator))

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    @property
    def DESCRIPTION(self):
        return 'Восстанавливает спутнику %(health)d здоровья.' % {'health': self.modificator}

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613

        if task.hero.companion is None:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='У героя нет спутника.')

        if task.hero.companion.health == task.hero.companion.max_health:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Спутник героя полностью здоров.')

        health = task.hero.companion.heal(self.modificator)

        return task.logic_result(message='Спутник вылечен на %(health)s HP.' % {'health': health})


class GiveCommonCards(ModificatorBase):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    @property
    def DESCRIPTION(self):
        return 'Даёт карты обычной редкости (%(number)d шт.). Если эту карту можно продавать, то: полученные карты можно будет продавать, могут быть получены карты, доступные только подписчикам.' % {'number': self.upper_modificator}

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        used_card = objects.Card.deserialize(uuid.UUID(task.data['card']['id']), task.data['card']['data'])

        logic.give_new_cards(account_id=task.hero.account_id,
                             operation_type='give-common-cards-card',
                             allow_premium_cards=used_card.available_for_auction,
                             available_for_auction=used_card.available_for_auction,
                             rarity=relations.RARITY.COMMON,
                             number=self.upper_modificator)

        return task.logic_result(message='Вы получили {number} новых карт. Можете забрать их на странице игры.'.format(number=self.upper_modificator))


class UpgradeArtifact(BaseEffect):
    __slots__ = ()

    def get_form(self, card, hero, data):
        return forms.Empty(data)

    DESCRIPTION = 'Заменяет случайный экипированный не эпический артефакт, на более редкий того же вида. Параметры нового артефакта могут быть ниже параметров старого.'

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613

        artifacts = [artifact for artifact in list(task.hero.equipment.values()) if not artifact.rarity.is_EPIC]

        if not artifacts:
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='У героя нет экипированных не эпических артефактов.')

        artifact = random.choice(artifacts)

        task.hero.increment_equipment_rarity(artifact)

        return task.logic_result(message='Качество артефакта %(artifact)s улучшено.' % {'artifact': artifact.html_label()})


class CreateClan(BaseEffect):
    __slots__ = ()

    FORM_TEMPLATE = 'cards/effect_form_create_clan.html'

    def get_form(self, card, hero, data):
        return forms.CreateClan(data)

    DESCRIPTION = 'Создаёт новую гильдию и делает игрока её лидером.'

    def use(self, task, storage, highlevel=None, **kwargs):  # pylint: disable=R0911,W0613
        name = task.data.get('name')
        abbr = task.data.get('abbr')

        if clans_models.Membership.objects.filter(account=task.hero_id).exists():
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Вы уже состоите в гильдии.')

        if clans_models.Clan.objects.filter(name=name).exists():
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Гильдия с таким названием уже существует.')

        if clans_models.Clan.objects.filter(abbr=abbr).exists():
            return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR, message='Гильдия с такой аббревиатурой уже существует.')

        clans_prototypes.ClanPrototype.create(owner=accounts_prototypes.AccountPrototype.get_by_id(task.hero_id),
                                              abbr=abbr,
                                              name=name,
                                              motto='Veni, vidi, vici!',
                                              description='')

        return task.logic_result(message='Поздравляем, гильдмастер! Ваша гильдия ждёт Вас! Задайте девиз и описание гильдии на её странице.')


class ChangeHistory(BaseEffect):
    __slots__ = ()

    class HISTORY_TYPE(rels_django.DjangoEnum):
        choices = rels.Column(single_type=False)
        form_class = rels.Column(single_type=False)

        records = (('UPBRINGING', 0, 'воспитание', tt_beings_relations.UPBRINGING, forms.Upbringing),
                   ('DEATH_AGE', 1, 'возраст смерти', tt_beings_relations.AGE, forms.DeathAge),
                   ('FIRST_DEATH', 2, 'способ смерти', tt_beings_relations.FIRST_DEATH, forms.DeathType))

    DESCRIPTION = 'Позволяет изменить часть истории героя, указанную в названии карты.'

    def get_form(self, card, hero, data):
        return self.HISTORY_TYPE(card.data['history_id']).form_class(data)

    def change_upbringing(self, storage, hero, value):
        upbringing = tt_beings_relations.UPBRINGING(value)

        if upbringing == hero.upbringing:
            return False

        hero.upbringing = upbringing

        storage.save_bundle_data(bundle_id=hero.actions.current_action.bundle_id)

        return True

    def change_death_age(self, storage, hero, value):
        age = tt_beings_relations.AGE(value)

        if age == hero.death_age:
            return False

        hero.death_age = age

        storage.save_bundle_data(bundle_id=hero.actions.current_action.bundle_id)

        return True

    def change_first_death(self, storage, hero, value):
        first_death = tt_beings_relations.FIRST_DEATH(value)

        if first_death == hero.first_death:
            return False

        hero.first_death = first_death

        storage.save_bundle_data(bundle_id=hero.actions.current_action.bundle_id)

        return True

    def use(self, task, storage, **kwargs):  # pylint: disable=R0911,W0613
        card = objects.Card.deserialize(uuid.UUID(task.data['card']['id']), task.data['card']['data'])

        history_type = self.HISTORY_TYPE(card.data['history_id'])

        if history_type.is_UPBRINGING:
            if not self.change_upbringing(storage, task.hero, task.data.get('value')):
                return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR,
                                         message='Герой уже имеет выбранное воспитание.')
            return task.logic_result(message='Воспитание героя изменено.')

        elif history_type.is_DEATH_AGE:
            if not self.change_death_age(storage, task.hero, task.data.get('value')):
                return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR,
                                         message='Герой уже имеет выбранный возраст смерти.')
            return task.logic_result(message='Возраст смерти героя изменён.')

        elif history_type.is_FIRST_DEATH:
            if not self.change_first_death(storage, task.hero, task.data.get('value')):
                return task.logic_result(next_step=postponed_tasks.UseCardTask.STEP.ERROR,
                                         message='Герой уже имеет выбранный способ первой смерти.')
            return task.logic_result(message='Способ первой смерти героя изменён.')

        raise NotImplementedError

    def allowed_history(self):
        return self.HISTORY_TYPE.records

    def create_card(self, type, available_for_auction, history=None, uid=None):
        if history is None:
            history = random.choice(self.allowed_history())

        return objects.Card(type=type,
                            available_for_auction=available_for_auction,
                            data={'history_id': history.value},
                            uid=uid if uid else uuid.uuid4())

    def _item_full_type(self, type, history_id):
        return '{}-{}'.format(type.value, history_id)

    def item_full_type(self, card):
        return self._item_full_type(card.type, card.data['history_id'])

    def full_type_names(self, card_type):
        names = {}

        for history in self.allowed_history():
            full_type = self._item_full_type(card_type, history.value)
            names[full_type] = self._name_for_card(card_type, history.value)

        return names

    def _name_for_card(self, type, history_id):
        return '{}: {}'.format(type.text, self.HISTORY_TYPE(history_id).text)

    def name_for_card(self, card):
        return self._name_for_card(card.type, card.data['history_id'])
