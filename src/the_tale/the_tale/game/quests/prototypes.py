
import smart_imports

smart_imports.all()


E = 0.001


class QuestInfo(object):
    __slots__ = ('type', 'uid', 'name', 'action', 'choice', 'choice_alternatives', 'experience', 'power', 'experience_bonus', 'power_bonus', 'actors', 'used_markers')

    def __init__(self, type, uid, name, action, choice, choice_alternatives, experience, power, actors, used_markers, experience_bonus=0, power_bonus=0,):
        self.type = type
        self.uid = uid
        self.name = name
        self.action = action
        self.choice = choice
        self.choice_alternatives = choice_alternatives
        self.experience = experience
        self.power = power
        self.experience_bonus = experience_bonus
        self.power_bonus = power_bonus
        self.actors = actors
        self.used_markers = used_markers

    @property
    def total_experience(self):
        return self.experience + self.experience_bonus

    def serialize(self):
        return {'type': self.type,
                'uid': self.uid,
                'name': self.name,
                'action': self.action,
                'choice': self.choice,
                'choice_alternatives': self.choice_alternatives,
                'experience': self.experience,
                'power': self.power,
                'experience_bonus': self.experience_bonus,
                'power_bonus': self.power_bonus,
                'actors': self.actors,
                'used_markers': self.used_markers}

    def ui_info(self, hero):
        # show experience modified by hero level and abilities
        experience = int(self.experience * hero.experience_modifier) if hero is not None else self.experience

        # show power modified by hero level and abilities
        power = int((self.power + self.power_bonus) * hero.politics_power_multiplier()) if hero is not None else self.power

        return {'type': self.type,
                'uid': self.uid,
                'name': self.name,
                'action': self.action,
                'choice': self.choice,
                'choice_alternatives': self.choice_alternatives,
                'experience': experience + self.experience_bonus,
                'power': power,
                'actors': self.actors_ui_info()}

    def prepair_actor_ui_info(self, role, actor_type):
        if role not in self.actors:
            return None

        if len(self.actors[role]) == 2:
            # suport of old quests
            # can be removed after 0.3.30
            actor_internal_type = None
            actor_id, actor_name = self.actors[role]
        else:
            actor_internal_type, actor_id, actor_name = self.actors[role]

        if actor_type.is_PLACE:
            return (actor_name, actor_type.value, {'id': actor_id,
                                                   'name': places_storage.places[actor_id].name})
        if actor_type.is_PERSON:
            if actor_internal_type is None:
                actor_internal_type = game_relations.ACTOR.PERSON
            else:
                actor_internal_type = game_relations.ACTOR(actor_internal_type)

            if actor_internal_type.is_PERSON:
                return (actor_name, actor_type.value, persons_storage.persons[actor_id].ui_info())
            elif actor_internal_type.is_EMISSARY:
                return (actor_name, actor_type.value, emissaries_storage.emissaries.get_or_load(actor_id).ui_info())
            else:
                raise NotImplementedError

        if actor_type.is_MONEY_SPENDING:
            return (actor_name, actor_type.value, {'goal': actor_id.text,
                                                   'description': actor_id.description})

    def actors_ui_info(self):
        if self.type == 'no-quest':
            return []

        if self.type == 'next-spending':
            return [self.prepair_actor_ui_info('goal', relations.ACTOR_TYPE.MONEY_SPENDING)]

        return [_f for _f in [self.prepair_actor_ui_info(questgen_quests_base_quest.ROLES.INITIATOR, relations.ACTOR_TYPE.PERSON),
                              self.prepair_actor_ui_info(questgen_quests_base_quest.ROLES.INITIATOR_POSITION, relations.ACTOR_TYPE.PLACE),
                              self.prepair_actor_ui_info(questgen_quests_base_quest.ROLES.RECEIVER, relations.ACTOR_TYPE.PERSON),
                              self.prepair_actor_ui_info(questgen_quests_base_quest.ROLES.RECEIVER_POSITION, relations.ACTOR_TYPE.PLACE),
                              self.prepair_actor_ui_info(questgen_quests_base_quest.ROLES.ANTAGONIST, relations.ACTOR_TYPE.PERSON),
                              self.prepair_actor_ui_info(questgen_quests_base_quest.ROLES.ANTAGONIST_POSITION, relations.ACTOR_TYPE.PLACE)] if _f]

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @classmethod
    def construct(cls, type, uid, knowledge_base, hero, experience, power):

        writer = writers.get_writer(hero=hero, type=type, message=None, substitution=cls.substitution(uid, knowledge_base, hero))

        actors = {participant.role: (knowledge_base[participant.participant].externals.get('type'),
                                     knowledge_base[participant.participant].externals['id'],
                                     writer.actor(participant.role))
                  for participant in knowledge_base.filter(questgen_facts.QuestParticipant)
                  if participant.start == uid}

        return cls(type=type,
                   uid=uid,
                   name=writer.name(),
                   action='',
                   choice=None,
                   choice_alternatives=[],
                   experience=experience,
                   power=power,
                   experience_bonus=0,
                   power_bonus=0,
                   actors=actors,
                   used_markers={})

    @classmethod
    def substitution(cls, uid, knowledge_base, hero):
        data = {'hero': hero}
        for participant in knowledge_base.filter(questgen_facts.QuestParticipant):
            if participant.start != uid:
                continue

            actor = knowledge_base[participant.participant]

            if isinstance(actor, questgen_facts.Person):
                person_type = logic.extract_person_type(actor)

                if person_type.is_PERSON:
                    person = persons_storage.persons[actor.externals['id']]

                elif person_type.is_EMISSARY:
                    person = emissaries_storage.emissaries.get_or_load(actor.externals['id'])

                else:
                    raise NotImplementedError

                data[participant.role] = person
                data[participant.role + '_position'] = person.place

            elif isinstance(actor, questgen_facts.Place):
                data[participant.role] = places_storage.places[actor.externals['id']]

        return data

    def process_message(self, knowledge_base, hero, message, ext_substitution={}):

        substitution = self.substitution(self.uid, knowledge_base, hero)
        substitution.update(ext_substitution)

        writer = writers.get_writer(hero=hero, type=self.type, message=message, substitution=substitution)

        action_msg = writer.action()
        if action_msg:
            self.action = action_msg

        diary_msg = writer.diary()
        if diary_msg:
            hero.push_message(diary_msg, diary=True, journal=True)
            return

        journal_msg = writer.journal()
        if journal_msg:
            hero.push_message(journal_msg, diary=False, journal=True)

    def sync_choices(self, knowledge_base, hero, choice, options, defaults):

        if choice is None:
            self.choice = None
            self.choice_alternatives = ()
            return

        substitution = self.substitution(self.uid, knowledge_base, hero)
        writer = writers.get_writer(hero=hero, type=self.type, message='choice', substitution=substitution)

        choosen_option = knowledge_base[defaults[0].option]

        self.choice = writer.current_choice(choosen_option.type)

        if defaults[0].default:
            self.choice_alternatives = [(option.uid, writer.choice_variant(option.type))
                                        for option in options
                                        if option.uid != choosen_option.uid]
        else:
            self.choice_alternatives = ()

    def get_real_reward_scale(self, hero, scale):

        scale *= hero.quest_money_reward_multiplier()

        markers_bonuses = hero.quest_markers_rewards_bonus()
        for marker in self.used_markers:
            scale += markers_bonuses.get(marker, 0)

        return scale


NO_QUEST_INFO__IN_PLACE = QuestInfo(type='no-quest',
                                    uid='no-quest',
                                    name='безделье',
                                    action='имитирует бурную деятельность',
                                    choice=None,
                                    choice_alternatives=(),
                                    experience=0,
                                    experience_bonus=0,
                                    power_bonus=0,
                                    power=0,
                                    actors={},
                                    used_markers=set())

NO_QUEST_INFO__OUT_PLACE = QuestInfo(type='no-quest',
                                     uid='no-quest',
                                     name='безделье',
                                     action='идёт в ближайший город',
                                     choice=None,
                                     choice_alternatives=(),
                                     experience=0,
                                     power=0,
                                     experience_bonus=0,
                                     power_bonus=0,
                                     actors={},
                                     used_markers=set())


class QuestPrototype(object):
    __slots__ = ('knowledge_base',
                 'quests_stack',
                 'created_at',
                 'states_to_percents',
                 'hero',
                 'paths_cache',
                 'machine',
                 'inner_circle_places',
                 'inner_circle_persons')

    def __init__(self,
                 knowledge_base,
                 quests_stack=None,
                 created_at=None,
                 states_to_percents=None,
                 hero=None,
                 paths_cache=None,
                 inner_circle_places=None,
                 inner_circle_persons=None):
        self.hero = hero
        self.quests_stack = [] if quests_stack is None else quests_stack
        self.knowledge_base = knowledge_base
        self.machine = questgen_machine.Machine(knowledge_base=knowledge_base,
                                                interpreter=self)
        self.created_at = datetime.datetime.now() if created_at is None else created_at
        self.states_to_percents = states_to_percents if states_to_percents is not None else {}
        self.paths_cache = paths_cache if paths_cache is not None else {}

        self.inner_circle_places = set(inner_circle_places) if inner_circle_places else set()
        self.inner_circle_persons = set(inner_circle_persons) if inner_circle_persons else set()

    def extend_inner_circle(self, inner_circle_places, inner_circle_persons):
        if not inner_circle_places:
            inner_circle_places = set()

        if not inner_circle_persons:
            inner_circle_persons = set()

        self.inner_circle_places = inner_circle_places
        self.inner_circle_persons = inner_circle_persons

    @property
    def current_info(self):
        return self.quests_stack[-1]

    def serialize(self):
        return {'quests_stack': [info.serialize() for info in self.quests_stack],
                'knowledge_base': self.knowledge_base.serialize(short=True),
                'created_at': time.mktime(self.created_at.timetuple()),
                'states_to_percents': self.states_to_percents,
                'paths_cache': {key: path.serialize() for key, path in self.paths_cache.items()},
                'inner_circle_places': list(self.inner_circle_places),
                'inner_circle_persons': list(self.inner_circle_persons)}

    @classmethod
    def deserialize(cls, data):
        return cls(knowledge_base=questgen_knowledge_base.KnowledgeBase.deserialize(data['knowledge_base'], fact_classes=questgen_facts.FACTS),
                   quests_stack=[QuestInfo.deserialize(info_data) for info_data in data['quests_stack']],
                   created_at=datetime.datetime.fromtimestamp(data['created_at']),
                   states_to_percents=data['states_to_percents'],
                   paths_cache={key: navigation_path.Path.deserialize(path) for key, path in data.get('paths_cache', {}).items()},
                   inner_circle_places=set(data.get('inner_circle_places', ())),
                   inner_circle_persons=set(data.get('inner_circle_persons', ())))

    @property
    def percents(self):
        return self.states_to_percents.get(self.machine.pointer.state, 0.0)

    @property
    def is_processed(self):
        return self.machine.is_processed

    def get_nearest_choice(self):
        return self.machine.get_nearest_choice()

    def make_choice(self, option_uid):
        choice, options, defaults = self.get_nearest_choice()

        if self.knowledge_base[option_uid].state_from != choice.uid:
            return False

        if not any(option.uid == option_uid for option in options):
            return False

        if not defaults[0].default:
            return False

        if not questgen_transformators.change_choice(knowledge_base=self.knowledge_base, new_option_uid=option_uid, default=False):
            return False

        self.machine.sync_pointer()

        if self.quests_stack:
            self.current_info.sync_choices(self.knowledge_base, self.hero, *self.get_nearest_choice())

        self.hero.actions.request_replane()
        return True

    ###########################################
    # Object operations
    ###########################################

    def process(self):
        self.hero.quests.mark_updated()

        step_result = self.machine.do_step()

        if self.quests_stack:
            self.current_info.sync_choices(self.knowledge_base, self.hero, *self.get_nearest_choice())

        if step_result:
            return self.percents

        return 1

    def _move_hero_to(self, destination):
        places_cost_modifiers = heroes_logic.get_places_path_modifiers(hero=self.hero)

        path = map_storage.cells.find_path_to_place(from_x=self.hero.position.cell_x,
                                                    from_y=self.hero.position.cell_y,
                                                    to_place_id=destination.id,
                                                    cost_modifiers=places_cost_modifiers,
                                                    risk_level=self.hero.preferences.risk_level)
        path.set_start(self.hero.position.x, self.hero.position.y)

        actions_prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                            path=path,
                                                            destination=destination,
                                                            break_at=None)

    def _move_hero_near(self, destination, terrains=None):
        to_x, to_y = places_logic.choose_place_cell_by_terrain(destination.id, terrains, exclude_place_if_can=True)

        path = navigation_path.simple_path(from_x=self.hero.position.cell_x,
                                           from_y=self.hero.position.cell_y,
                                           to_x=to_x,
                                           to_y=to_y)
        path.set_start(self.hero.position.x, self.hero.position.y)

        actions_prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                            path=path,
                                                            destination=destination,
                                                            break_at=None)

    def _get_fixed_path(self, place_from, place_to):
        key = '{}_{}'.format(place_from.id, place_to.id)

        if key not in self.paths_cache:
            places_cost_modifiers = heroes_logic.get_places_path_modifiers(hero=self.hero)

            path = map_storage.cells.get_path_between_places(from_place_id=place_from.id,
                                                             to_place_id=place_to.id,
                                                             cost_modifiers=places_cost_modifiers,
                                                             risk_level=self.hero.preferences.risk_level)

            self.paths_cache[key] = path

        return self.paths_cache[key]

    def _move_hero_on_road(self, place_from, place_to, percents):
        path = self._get_fixed_path(place_from, place_to)

        nearest_percents, x, y = path.nearest_coordinates(self.hero.position.x, self.hero.position.y)

        path_to = path.subpath_from_percents(nearest_percents)

        # так как мы пересчитали путь (уменьшили его, начав от текущего положения героя)
        # то следует нормировать точку останова (увеличить процент пропорционально уменьшению пути)
        if 1 < nearest_percents + sys.float_info.epsilon:
            real_break_at = percents
        else:
            real_break_at = (percents - nearest_percents) / (1 - nearest_percents)

        # log_data = {'hero_id': self.hero.id,
        #             'percents': percents,
        #             'nearest_percents': nearest_percents,
        #             'hero_coordinates': (self.hero.position.x, self.hero.position.y),
        #             'path_coordinates': (x, y),
        #             'place_from': place_from.id,
        #             'place_to': place_to.id,
        #             'path_to': path_to.serialize(),
        #             'real_break_at': real_break_at}

        # logger.info('_move_hero_on_road for hero %s, properties: %s', self.hero.id, log_data)

        actions_prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                            path=path_to,
                                                            destination=place_to,
                                                            break_at=real_break_at)

    def get_current_power(self, power):
        return power * self.current_info.power

    def modify_person_power(self, power, person):
        power += (1 if power > 0 else -1) * self.current_info.power_bonus

        person_uid = uids.person(person.id)
        has_profession_marker = [marker for marker in self.knowledge_base.filter(questgen_facts.ProfessionMarker) if marker.person == person_uid]

        if has_profession_marker:
            power /= len(persons_relations.PERSON_TYPE.records)

        return power

    def _fight(self, action):
        if action.mob is not None:
            mob = mobs_storage.mobs[self.knowledge_base[action.mob].externals['id']].create_mob(self.hero, is_boss=True)
        else:
            mob = mobs_storage.mobs.get_random_mob(self.hero, mercenary=action.mercenary, is_boss=True)

            if mob is None:
                mobs_storage.mobs.get_random_mob(self.hero, is_boss=True)

        actions_prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)

    def give_power_to_person(self, hero, object_fact, result):
        person_id = object_fact.externals['id']

        if result == questgen_quests_base_quest.RESULTS.FAILED:
            hero.quests.add_interfered_person(person_id)

        person_habits_change_source = persons_storage.persons[person_id].attrs.on_quest_habits.get(result)

        if person_habits_change_source:
            hero.update_habits(person_habits_change_source)

        power = self.finish_quest_person_power(result, object_fact.uid)

        return persons_logic.impacts_from_hero(hero,
                                               person=persons_storage.persons[person_id],
                                               power=power,
                                               inner_circle_persons=self.inner_circle_persons,
                                               inner_circle_places=self.inner_circle_places)

    def give_power_to_emissary(self, hero, object_fact, result):
        emissary_id = object_fact.externals['id']

        emissary = emissaries_storage.emissaries.get_or_load(emissary_id)

        power = self.finish_quest_emissary_power(result, object_fact.uid)

        return emissaries_logic.impacts_from_hero(hero, emissary, power)

    def give_power_to_place(self, hero, object_fact, result):
        power = self.finish_quest_place_power(result, object_fact.uid)

        return places_logic.impacts_from_hero(hero,
                                              place=places_storage.places[object_fact.externals['id']],
                                              power=power,
                                              inner_circle_places=self.inner_circle_places)

    def _finish_quest(self, finish, hero):

        experience = self.current_info.experience
        experience_bonus = self.current_info.experience_bonus

        hero.add_experience(experience)
        hero.add_experience(experience_bonus, without_modifications=True)

        hero.statistics.change_quests_done(1)

        if hero.companion:
            expected_quest_path = places_storage.places.expected_minimum_quest_distance()
            hero.companion.add_experience(companions_logic.coherence_exp_per_quest(expected_quest_path))

        power_impacts = []

        for object_uid, result in finish.results.items():

            object_fact = self.knowledge_base[object_uid]

            if isinstance(object_fact, questgen_facts.Person):
                person_type = logic.extract_person_type(object_fact)

                if person_type.is_PERSON:
                    impacts = self.give_power_to_person(hero, object_fact, result)
                elif person_type.is_EMISSARY:
                    impacts = self.give_power_to_emissary(hero, object_fact, result)
                else:
                    raise exceptions.UnknownPowerRecipientError(recipient=object_fact)

                power_impacts.extend(impacts)

            elif isinstance(object_fact, questgen_facts.Place):
                power_impacts.extend(self.give_power_to_place(hero, object_fact, result))

            else:
                raise exceptions.UnknownPowerRecipientError(recipient=object_fact)

        politic_power_logic.add_power_impacts(power_impacts)

        for marker, default in self.current_info.used_markers.items():
            for change_source in heroes_relations.HABIT_CHANGE_SOURCE.records:
                if change_source.quest_marker == marker and change_source.quest_default == default:
                    self.hero.update_habits(change_source)

        self.quests_stack.pop()

    def finish_quest_power(self, result):
        if result == questgen_quests_base_quest.RESULTS.SUCCESSED:
            object_politic_power = 1
        elif result == questgen_quests_base_quest.RESULTS.FAILED:
            object_politic_power = -1
        else:
            object_politic_power = 0

        object_politic_power = self.get_current_power(object_politic_power)

        power_bonus = 0

        if result != questgen_quests_base_quest.RESULTS.NEUTRAL:
            power_bonus = (1 if object_politic_power > 0 else -1) * self.current_info.power_bonus

        return object_politic_power, power_bonus

    def finish_quest_person_power(self, result, object_uid):
        object_politic_power, power_bonus = self.finish_quest_power(result)

        has_profession_marker = [marker
                                 for marker in self.knowledge_base.filter(questgen_facts.ProfessionMarker)
                                 if marker.person == object_uid]

        if has_profession_marker:
            object_politic_power /= len(persons_relations.PERSON_TYPE.records)

        return object_politic_power + power_bonus

    def finish_quest_emissary_power(self, result, object_uid):
        object_politic_power, power_bonus = self.finish_quest_power(result)
        return object_politic_power + power_bonus

    def finish_quest_place_power(self, result, object_uid):
        object_politic_power, power_bonus = self.finish_quest_power(result)
        return object_politic_power + power_bonus

    def get_state_by_jump_pointer(self):
        return self.knowledge_base[self.knowledge_base[self.machine.pointer.jump].state_to]

    def positive_results_masters(self):

        finish_state = self.get_state_by_jump_pointer()

        for object_uid, result in finish_state.results.items():

            if result != questgen_quests_base_quest.RESULTS.SUCCESSED:
                continue

            object_fact = self.knowledge_base[object_uid]

            if not isinstance(object_fact, questgen_facts.Person):
                continue

            if not logic.extract_person_type(object_fact).is_PERSON:
                continue

            person_id = object_fact.externals['id']

            yield persons_storage.persons[person_id]

    def modify_reward_scale(self, scale):
        for person in self.positive_results_masters():
            scale += person.attrs.on_profite_reward_bonus

        return scale

    def give_energy_on_reward(self):
        if not self.hero.can_regenerate_energy:
            return

        energy = sum(person.attrs.on_profite_energy
                     for person in self.positive_results_masters())

        if energy == 0:
            return

        game_tt_services.energy.cmd_change_balance(account_id=self.hero.account_id,
                                                   type='for_quest',
                                                   amount=energy,
                                                   asynchronous=True,
                                                   autocommit=True)

    def _give_reward(self, hero, reward_type, scale):

        quest_info = self.current_info

        scale = quest_info.get_real_reward_scale(hero, scale)
        scale = self.modify_reward_scale(scale)

        self.give_energy_on_reward()

        # hero receive artifact
        if hero.can_get_artifact_for_quest():

            level_delta = int(math.ceil(abs(scale)))

            if scale < 0:
                level_delta = -level_delta

            artifact, unequipped, sell_price = self.hero.receive_artifact(equip=False,
                                                                          better=False,
                                                                          prefered_slot=False,
                                                                          prefered_item=False,
                                                                          archetype=True,
                                                                          level_delta=level_delta)

            if artifact is not None:
                quest_info.process_message(knowledge_base=self.knowledge_base,
                                           hero=self.hero,
                                           message='%s_artifact' % reward_type,
                                           ext_substitution={'artifact': artifact})
                return

        # here does not receive artifac (receive money instead)

        money = int(max(1, f.sell_artifact_price(hero.level) * scale))

        hero.change_money(heroes_relations.MONEY_SOURCE.EARNED_FROM_QUESTS, money)

        quest_info.process_message(knowledge_base=self.knowledge_base,
                                   hero=self.hero,
                                   message='%s_money' % reward_type,
                                   ext_substitution={'coins': money})

    def _donothing(self, donothing_type):
        donothing = relations.DONOTHING_TYPE.index_value[donothing_type]

        writer = writers.get_writer(hero=self.hero, type=self.current_info.type, message=donothing_type, substitution={})

        actions_prototypes.ActionDoNothingPrototype.create(hero=self.hero,
                                                           duration=donothing.duration,
                                                           messages_prefix=writer.journal_id(),
                                                           messages_probability=donothing.messages_probability)

    @classmethod
    def _get_upgrdade_choice(cls, hero):
        choices = [relations.UPGRADE_EQUIPMENT_VARIANTS.BUY]

        if hero.preferences.equipment_slot and hero.equipment.get(hero.preferences.equipment_slot) is not None:
            choices.append(relations.UPGRADE_EQUIPMENT_VARIANTS.SHARP)

            if hero.equipment.get(hero.preferences.equipment_slot).can_be_broken():
                choices.append(relations.UPGRADE_EQUIPMENT_VARIANTS.REPAIR)

        return random.choice(choices)

    @classmethod
    def upgrade_equipment_cost(cls, hero_info):
        return int(f.normal_action_price(hero_info.level) * heroes_relations.ITEMS_OF_EXPENDITURE.get_quest_upgrade_equipment_fraction())

    @classmethod
    def _upgrade_equipment(cls, process_message, hero, knowledge_base, cost):

        if cost is not None:
            cost = min(cost, hero.money)

        upgrade_choice = cls._get_upgrdade_choice(hero)

        if upgrade_choice.is_BUY:
            artifact, unequipped, sell_price = hero.receive_artifact(equip=True, better=True, prefered_slot=True, prefered_item=True, archetype=True)

            if cost is not None:
                hero.change_money(heroes_relations.MONEY_SOURCE.SPEND_FOR_ARTIFACTS, -cost)
                if artifact is None:
                    process_message(knowledge_base, hero, message='upgrade__fail', ext_substitution={'coins': cost})
                elif unequipped:
                    process_message(knowledge_base, hero, message='upgrade__buy_and_change', ext_substitution={'coins': cost,
                                                                                                               'artifact': artifact,
                                                                                                               'unequipped': unequipped,
                                                                                                               'sell_price': sell_price})
                else:
                    process_message(knowledge_base, hero, message='upgrade__buy', ext_substitution={'coins': cost,
                                                                                                    'artifact': artifact})
            else:
                if artifact is None:
                    process_message(knowledge_base, hero, message='upgrade_free__fail', ext_substitution={})
                elif unequipped:
                    process_message(knowledge_base, hero, message='upgrade_free__buy_and_change', ext_substitution={'artifact': artifact,
                                                                                                                    'unequipped': unequipped,
                                                                                                                    'sell_price': sell_price})
                else:
                    process_message(knowledge_base, hero, message='upgrade_free__buy', ext_substitution={'artifact': artifact})

        elif upgrade_choice.is_SHARP:
            artifact = hero.sharp_artifact()

            if cost is not None:
                hero.change_money(heroes_relations.MONEY_SOURCE.SPEND_FOR_SHARPENING, -cost)
                process_message(knowledge_base, hero, message='upgrade__sharp', ext_substitution={'coins': cost,
                                                                                                  'artifact': artifact})
            else:
                process_message(knowledge_base, hero, message='upgrade_free__sharp', ext_substitution={'artifact': artifact})

        elif upgrade_choice.is_REPAIR:
            artifact = hero.repair_artifact()

            if cost is not None:
                hero.change_money(heroes_relations.MONEY_SOURCE.SPEND_FOR_REPAIRING, -cost)
                process_message(knowledge_base, hero, message='upgrade__repair', ext_substitution={'coins': cost,
                                                                                                   'artifact': artifact})
            else:
                process_message(knowledge_base, hero, message='upgrade_free__repair', ext_substitution={'artifact': artifact})

        else:
            raise exceptions.UnknownUpgadeEquipmentTypeError(type=upgrade_choice)

    def _start_quest(self, start, hero):
        hero.quests.update_history(start.type, game_turn.number())
        self.quests_stack.append(QuestInfo.construct(type=start.type,
                                                     uid=start.uid,
                                                     knowledge_base=self.machine.knowledge_base,
                                                     experience=self.get_expirience_for_quest(start.uid, hero),
                                                     power=self.get_politic_power_for_quest(start.uid, hero),
                                                     hero=hero))

    def quest_participants(self, quest_uid):
        for participant in self.knowledge_base.filter(questgen_facts.QuestParticipant):

            if quest_uid != participant.start:
                continue

            yield participant

    def get_expirience_for_quest(self, quest_uid, hero):

        if hero.statistics.quests_done == 0:
            # для первого задания даём столько опыта, чтобы почти получить уровень, но не получить
            return hero.experience_to_next_level - 1

        experience = f.experience_for_quest(places_storage.places.expected_minimum_quest_distance())

        place_experience_bonuses = {}
        person_experience_bonuses = {}
        emissaries_experience_bonuses = {}

        for participant in self.quest_participants(quest_uid):

            fact = self.knowledge_base[participant.participant]

            if isinstance(fact, questgen_facts.Person):

                person_type = logic.extract_person_type(fact)

                if person_type.is_PERSON:
                    person = persons_storage.persons.get(fact.externals['id'])
                    person_experience_bonuses[person.id] = person.attrs.experience_bonus

                elif person_type.is_EMISSARY:
                    person = emissaries_storage.emissaries.get_or_load(fact.externals['id'])
                    emissaries_experience_bonuses[person.id] = person.attrs.experience_bonus
                else:
                    raise NotImplementedError

                place = person.place

            elif isinstance(fact, questgen_facts.Place):
                place = places_storage.places.get(fact.externals['id'])

            place_experience_bonuses[place.id] = place.attrs.experience_bonus

        experience += experience * (sum(place_experience_bonuses.values()) +
                                    sum(person_experience_bonuses.values()) +
                                    sum(emissaries_experience_bonuses.values()))

        return max(1, experience)

    def get_politic_power_for_quest(self, quest_uid, hero):
        base_politic_power = f.person_power_for_quest(places_storage.places.expected_minimum_quest_distance())

        for participant in self.quest_participants(quest_uid):

            fact = self.knowledge_base[participant.participant]

            if not isinstance(fact, questgen_facts.Person):
                continue

            person_type = logic.extract_person_type(fact)

            if person_type.is_PERSON:
                person = persons_storage.persons.get(fact.externals['id'])
                base_politic_power += person.attrs.politic_power_bonus

            elif person_type.is_EMISSARY:
                pass

            else:
                raise NotImplementedError

        return base_politic_power

    ################################
    # general callbacks
    ################################

    def on_state__before_actions(self, state):

        if isinstance(state, questgen_facts.Start):
            self._start_quest(state, hero=self.hero)

    def on_state__after_actions(self, state):
        if isinstance(state, questgen_facts.Finish):
            self._finish_quest(state, hero=self.hero)

    def on_jump_start__before_actions(self, jump):
        pass

    def on_jump_start__after_actions(self, jump):
        pass

    def on_jump_end__before_actions(self, jump):
        pass

    def on_jump_end__after_actions(self, jump):
        if not isinstance(jump, questgen_facts.Option):
            return

        path = next((path for path in self.knowledge_base.filter(questgen_facts.ChoicePath) if path.option == jump.uid))

        used_markers = self.current_info.used_markers
        for marker in jump.markers:
            for markers_group in questgen_relations.OPTION_MARKERS_GROUPS:
                if marker not in markers_group:
                    continue

                for removed_marker in markers_group:
                    if removed_marker in used_markers:
                        del used_markers[removed_marker]

            used_markers[marker] = path.default

    ################################
    # do action callbacks
    ################################

    def do_message(self, action):
        self.current_info.process_message(self.knowledge_base, self.hero, action.type)

    def do_give_reward(self, action):
        self._give_reward(self.hero, action.type, action.scale)

    def do_fight(self, action):
        self._fight(action)

    def do_do_nothing(self, action):
        self._donothing(action.type)

    def do_upgrade_equipment(self, action):
        self._upgrade_equipment(self.current_info.process_message, self.hero, self.knowledge_base, cost=action.cost)

    def do_move_near(self, action):
        if action.place:
            destination = places_storage.places.get(self.knowledge_base[action.place].externals['id'])

        else:
            destination = self.hero.position.cell().nearest_place()

        self._move_hero_near(destination=destination, terrains=action.terrains)

    ################################
    # check requirements callbacks
    ################################

    def check_located_in(self, requirement):
        object_fact = self.knowledge_base[requirement.object]
        place_fact = self.knowledge_base[requirement.place]

        place = places_storage.places[place_fact.externals['id']]

        if isinstance(object_fact, questgen_facts.Person):
            person_type = logic.extract_person_type(object_fact)

            if person_type.is_PERSON:
                person = persons_storage.persons[object_fact.externals['id']]

            elif person_type.is_EMISSARY:
                person = emissaries_storage.emissaries.get_or_load(object_fact.externals['id'])

            else:
                raise NotImplementedError

            return person.place.id == place.id

        if isinstance(object_fact, questgen_facts.Hero):
            return bool(self.hero.id == object_fact.externals['id'] and self.hero.position.place and self.hero.position.place.id == place.id)

        raise exceptions.UnknownRequirementError(requirement=requirement)

    def check_located_near(self, requirement):
        object_fact = self.knowledge_base[requirement.object]
        place_fact = self.knowledge_base[requirement.place]

        place = places_storage.places[place_fact.externals['id']]

        if isinstance(object_fact, questgen_facts.Person):
            return False

        if not isinstance(object_fact, questgen_facts.Hero):
            raise exceptions.UnknownRequirementError(requirement=requirement)

        if self.hero.id != object_fact.externals['id']:
            return False

        # если городу принадлежит только одна клетка, на которой он находится,
        # то прогулкой в его окрестностях считается и нахождение в нём самом
        if self.hero.position.place and map_storage.cells.place_area(self.hero.position.place_id) > 1:
            return False

        hero_place = self.hero.position.cell().nearest_place()
        return place.id == hero_place.id

    def check_located_on_road(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if isinstance(object_fact, questgen_facts.Person):
            return False

        if not isinstance(object_fact, questgen_facts.Hero):
            raise exceptions.UnknownRequirementError(requirement=requirement)

        if self.hero.id != object_fact.externals['id']:
            return False

        path = self._get_fixed_path(place_from=places_storage.places[self.knowledge_base[requirement.place_from].externals['id']],
                                    place_to=places_storage.places[self.knowledge_base[requirement.place_to].externals['id']])

        percents, x, y = path.nearest_coordinates(self.hero.position.x, self.hero.position.y)

        return requirement.percents <= percents + 0.01

    def check_has_money(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if isinstance(object_fact, questgen_facts.Person):
            return False

        if isinstance(object_fact, questgen_facts.Hero):
            if self.hero.id != object_fact.externals['id']:
                return False
            return self.hero.money >= requirement.money

        raise exceptions.UnknownRequirementError(requirement=requirement)

    def check_is_alive(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if isinstance(object_fact, questgen_facts.Person):
            return True

        if isinstance(object_fact, questgen_facts.Hero):
            if self.hero.id != object_fact.externals['id']:
                return False

            return self.hero.is_alive

        raise exceptions.UnknownRequirementError(requirement=requirement)

    ################################
    # satisfy requirements callbacks
    ################################

    def satisfy_located_in(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if isinstance(object_fact, questgen_facts.Person):

            person_uid = object_fact.uid

            person_type = logic.extract_person_type(object_fact)

            if person_type.is_PERSON:
                person = persons_storage.persons[object_fact.externals['id']]

            elif person_type.is_EMISSARY:
                person = emissaries_storage.emissaries.get_or_load(object_fact.externals['id'])

            else:
                raise NotImplementedError

            new_place_uid = uids.place(person.place.id)

            if new_place_uid not in self.knowledge_base:
                self.knowledge_base += logic.fact_place(person.place)

            # переписываем все ограничения в базе
            for fact in self.knowledge_base.filter(questgen_facts.State):
                for state_requirement in fact.require:
                    if isinstance(state_requirement, questgen_requirements.LocatedIn) and state_requirement.object == person_uid:
                        state_requirement.place = new_place_uid

            return

        if not isinstance(object_fact, questgen_facts.Hero) or self.hero.id != object_fact.externals['id']:
            raise exceptions.UnknownRequirementError(requirement=requirement)

        self._move_hero_to(destination=places_storage.places[self.knowledge_base[requirement.place].externals['id']])

    def satisfy_located_near(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if not isinstance(object_fact, questgen_facts.Hero) or self.hero.id != object_fact.externals['id']:
            raise exceptions.UnknownRequirementError(requirement=requirement)

        destination = None

        if requirement.place is not None:
            destination = places_storage.places.get(self.knowledge_base[requirement.place].externals['id'])

        self._move_hero_near(destination=destination, terrains=requirement.terrains)

    def satisfy_located_on_road(self, requirement):
        object_fact = self.knowledge_base[requirement.object]

        if not isinstance(object_fact, questgen_facts.Hero) or self.hero.id != object_fact.externals['id']:
            raise exceptions.UnknownRequirementError(requirement=requirement)

        self._move_hero_on_road(place_from=places_storage.places[self.knowledge_base[requirement.place_from].externals['id']],
                                place_to=places_storage.places[self.knowledge_base[requirement.place_to].externals['id']],
                                percents=requirement.percents)

    def satisfy_has_money(self, requirement):
        raise exceptions.UnknownRequirementError(requirement=requirement)

    def satisfy_is_alive(self, requirement):
        raise exceptions.UnknownRequirementError(requirement=requirement)

    ################################
    # ui info
    ################################

    def ui_info(self):
        return {'line': [info.ui_info(self.hero) for info in self.quests_stack]}

    @classmethod
    def no_quests_ui_info(cls, in_place):
        if in_place:
            return {'line': [NO_QUEST_INFO__IN_PLACE.ui_info(None)]}
        else:
            return {'line': [NO_QUEST_INFO__OUT_PLACE.ui_info(None)]}

    @classmethod
    def next_spending_ui_info(cls, spending):
        NEXT_SPENDING_INFO = QuestInfo(type='next-spending',
                                       uid='next-spending',
                                       name='Накопить золото',
                                       action='копит',
                                       choice=None,
                                       choice_alternatives=(),
                                       experience=0,
                                       power=0,
                                       experience_bonus=0,
                                       power_bonus=0,
                                       actors={'goal': (spending, 'цель')},
                                       used_markers=set())
        return {'line': [NEXT_SPENDING_INFO.ui_info(None)]}
