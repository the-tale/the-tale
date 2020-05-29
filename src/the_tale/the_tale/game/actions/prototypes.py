
import smart_imports

smart_imports.all()


E = 0.0001


class ActionBase(object):

    __slots__ = ('hero',
                 'percents',
                 'bundle_id',
                 'description',
                 'state',
                 'removed',
                 'storage',
                 'created_at_turn',
                 'context',
                 'place_id',
                 'person_id',
                 'emissary_id',
                 'person_action',
                 'mob',
                 'data',
                 'break_at',
                 'percents_barier',
                 'extra_probability',
                 'mob_context',
                 'textgen_id',
                 'info_link',
                 'saved_meta_action',
                 'replane_required',
                 'path',
                 'inner_circle_places',
                 'inner_circle_persons')

    class STATE:
        UNINITIALIZED = 'uninitialized'
        PROCESSED = 'processed'

    TYPE = None
    SINGLE = True  # is action work with only one hero
    TEXTGEN_TYPE = NotImplemented
    CONTEXT_MANAGER = None
    HELP_CHOICES = set()
    APPROVED_FOR_STEPS_CHAIN = True
    HABIT_MODE = relations.ACTION_HABIT_MODE.PEACEFUL

    def __init__(self,
                 bundle_id,
                 state,
                 percents=0.0,
                 type=None,  # just for deserialization
                 created_at_turn=None,
                 context=None,
                 description=None,
                 place_id=None,
                 person_id=None,
                 emissary_id=None,
                 person_action=None,
                 mob=None,
                 data=None,
                 break_at=None,
                 percents_barier=None,
                 extra_probability=None,
                 mob_context=None,
                 textgen_id=None,
                 info_link=None,
                 meta_action=None,
                 replane_required=False,
                 hero=None,
                 path=None,
                 inner_circle_places=None,
                 inner_circle_persons=None):

        self.hero = hero

        self.description = description

        self.percents = percents

        self.bundle_id = bundle_id

        self.state = state

        self.removed = False
        self.storage = None

        self.created_at_turn = created_at_turn if created_at_turn is not None else game_turn.number()

        self.context = None
        self.mob_context = None

        if self.CONTEXT_MANAGER:
            self.context = context if context is None or isinstance(context, self.CONTEXT_MANAGER) else self.CONTEXT_MANAGER.deserialize(context)
            self.mob_context = mob_context if mob_context is None or isinstance(mob_context, self.CONTEXT_MANAGER) else self.CONTEXT_MANAGER.deserialize(mob_context)

        self.place_id = place_id
        self.person_id = person_id
        self.emissary_id = emissary_id

        self.person_action = None

        if person_action is not None:
            self.person_action = person_action if isinstance(person_action, rels.Record) else quests_relations.PERSON_ACTION(person_action)

        self.mob = None
        if mob:
            self.mob = mob if isinstance(mob, mobs_objects.Mob) else mobs_objects.Mob.deserialize(mob)

        self.data = data
        self.break_at = break_at
        self.percents_barier = percents_barier
        self.extra_probability = extra_probability
        self.textgen_id = textgen_id

        if meta_action is None or isinstance(meta_action, meta_actions.MetaAction):
            self.saved_meta_action = meta_action
        else:
            self.saved_meta_action = meta_actions.ACTION_TYPES[relations.ACTION_TYPE(meta_action['type'])].deserialize(meta_action)

        self.info_link = info_link

        self.replane_required = replane_required

        if path and isinstance(path, dict):
            self.path = navigation_path.Path.deserialize(path)
        else:
            self.path = path

        self.inner_circle_places = set(inner_circle_places) if inner_circle_places else set()
        self.inner_circle_persons = set(inner_circle_persons) if inner_circle_persons else set()

    def serialize(self):
        data = {'type': self.TYPE.value,
                'bundle_id': self.bundle_id,
                'state': self.state,
                'percents': self.percents,
                'description': self.description,
                'created_at_turn': self.created_at_turn}
        if self.replane_required:
            data['replane_required'] = self.replane_required
        if self.context:
            data['context'] = self.context.serialize()
        if self.place_id is not None:
            data['place_id'] = self.place_id
        if self.person_id is not None:
            data['person_id'] = self.person_id
        if self.emissary_id is not None:
            data['emissary_id'] = self.emissary_id
        if self.person_action is not None:
            data['person_action'] = self.person_action.value
        if self.mob:
            data['mob'] = self.mob.serialize()
        if self.data:
            data['data'] = self.data
        if self.break_at is not None:
            data['break_at'] = self.break_at
        if self.percents_barier is not None:
            data['percents_barier'] = self.percents_barier
        if self.extra_probability is not None:
            data['extra_probability'] = self.extra_probability
        if self.mob_context:
            data['mob_context'] = self.mob_context.serialize()
        if self.textgen_id is not None:
            data['textgen_id'] = self.textgen_id
        if self.meta_action is not None:
            data['meta_action'] = self.meta_action.serialize()
        if self.info_link is not None:
            data['info_link'] = self.info_link
        if self.path is not None:
            data['path'] = self.path.serialize()
        if self.inner_circle_places:
            data['inner_circle_places'] = list(self.inner_circle_places)
        if self.inner_circle_persons:
            data['inner_circle_persons'] = list(self.inner_circle_persons)

        return data

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @property
    def ui_type(self):
        return self.TYPE

    def ui_info(self):
        if self.description is None:
            self.description = self.get_description()

        if self.info_link is None:
            self.info_link = self.get_info_link()

        return {'percents': max(0.0, min(1.0, self.percents)),
                'type': self.ui_type.value,
                'description': self.description,
                'info_link': self.info_link,
                'is_boss': self.mob.is_boss if self.mob else None,
                'data': None}

    @property
    def leader(self):
        return (not self.removed) and (self.hero.actions.current_action is self)

    def set_storage(self, storage):
        self.storage = storage

    @property
    def place(self):
        return places_storage.places.get(self.place_id)

    @property
    def person(self):
        return persons_storage.persons.get(self.person_id)

    @property
    def meta_action(self):
        if self.saved_meta_action is None:
            return None
        if self.storage is None:  # if meta_action accessed from views (not from logic)
            return self.saved_meta_action
        return self.storage.meta_actions.get(self.saved_meta_action.uid)

    @property
    def help_choices(self):
        choices = copy.copy(self.HELP_CHOICES)

        if abilities_relations.HELP_CHOICES.HEAL in choices:
            if not self.hero.can_be_healed():
                choices.remove(abilities_relations.HELP_CHOICES.HEAL)

        if abilities_relations.HELP_CHOICES.HEAL_COMPANION in choices:
            if (self.hero.companion is None or
                self.hero.companion_heal_disabled() or
                    self.hero.companion.health == self.hero.companion.max_health):
                choices.remove(abilities_relations.HELP_CHOICES.HEAL_COMPANION)

        return choices

    def get_help_choice(self):

        choices = [(choice, choice.priority) for choice in self.help_choices]

        return utils_logic.random_value_by_priority(choices)

    @property
    def description_text_name(self):
        return '%s_description' % self.TEXTGEN_TYPE

    def get_info_link(self):
        return None

    def get_description(self):
        return linguistics_logic.get_text(self.description_text_name, self.get_description_arguments())

    def get_description_arguments(self):
        return {'hero': self.hero}

    def on_heal(self):
        pass

    def on_heal_companion(self):
        pass

    #####################################
    # management
    #####################################
    @classmethod
    def create(cls, hero, **kwargs):
        '''
        _storage argument used only in creating hero step
        '''

        bundle_id = None

        if hero.actions.has_actions:
            bundle_id = hero.actions.current_action.bundle_id

            # change description of current action
            # when new action ended, it will be illusion, that hero do other new action instead old one
            hero.actions.current_action.description = hero.actions.current_action.get_description()

        _storage = None
        if '_storage' in kwargs:
            _storage = kwargs['_storage']
            del kwargs['_storage']

        if '_bundle_id' in kwargs:
            bundle_id = kwargs['_bundle_id']
            del kwargs['_bundle_id']

        action = cls._create(hero, bundle_id, **kwargs)

        if _storage:
            _storage.add_action(action)

        elif hero.actions.has_actions:
            hero.actions.current_action.storage.add_action(action)

        hero.actions.push_action(action)

        return action

    def on_remove(self):
        pass

    def remove(self, force=False):
        '''
        force - if True, storages will be ignored (need for full remove of angel & hero)
        '''

        self.on_remove()

        if self.storage:
            self.storage.remove_action(self)

        self.hero.actions.pop_action()

        self.removed = True

    def on_save(self):
        pass

    def process_action(self):
        self.process()

        # remove only leader action
        # action can set PROCESSED state and create child action
        # is that case we should not remove action
        # it will be removed (by processing of chain actions in LogicStorage) when child action will be processed
        if self.leader and not self.removed and self.state == self.STATE.PROCESSED:
            self.remove()

    def process_turn(self):
        self.process_action()

    def choose_event_reward(self):
        return utils_logic.random_value_by_priority([(record, record.priority) for record in relations.ACTION_EVENT_REWARD.records])

    def do_events(self):

        habit_events = self.hero.habit_events()

        if not habit_events:
            return

        event = random.choice(list(habit_events))

        event_reward = self.choose_event_reward()

        message_type = 'action_event_habit_%s_%s_%s' % (self.TYPE.name.lower(), event.name.lower(), event_reward.name.lower())

        if event_reward.is_NOTHING:
            self.hero.add_message(message_type, diary=True, hero=self.hero, **self.action_event_message_arguments())
        elif event_reward.is_MONEY:
            coins = int(math.ceil(f.normal_loot_cost_at_lvl(self.hero.level)))
            self.hero.change_money(heroes_relations.MONEY_SOURCE.EARNED_FROM_HABITS, coins)
            self.hero.add_message(message_type, diary=True, hero=self.hero, coins=coins, **self.action_event_message_arguments())
        elif event_reward.is_ARTIFACT:
            artifact, unequipped, sell_price = self.hero.receive_artifact(equip=False, better=False, prefered_slot=False, prefered_item=False, archetype=False)
            self.hero.add_message(message_type, diary=True, hero=self.hero, artifact=artifact, **self.action_event_message_arguments())
        elif event_reward.is_EXPERIENCE:
            experience = self.hero.add_experience(int(c.HABIT_EVENT_EXPERIENCE * random.uniform(1.0 - c.HABIT_EVENT_EXPERIENCE_DELTA, 1.0 + c.HABIT_EVENT_EXPERIENCE_DELTA)))
            self.hero.add_message(message_type, diary=True, hero=self.hero, experience=experience, **self.action_event_message_arguments())

    def action_event_message_arguments(self):
        return {}

    searching_quest = False

    def setup_quest(self, quest):
        pass  # do nothing if there is not quest action

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, name) == getattr(other, name) for name in self.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)


class ActionIdlenessPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.IDLENESS
    TEXTGEN_TYPE = 'action_idleness'

    HELP_CHOICES = {abilities_relations.HELP_CHOICES.HEAL,
                    abilities_relations.HELP_CHOICES.MONEY,
                    abilities_relations.HELP_CHOICES.HEAL_COMPANION}

    class STATE(ActionBase.STATE):
        BEFORE_FIRST_STEPS = 'BEFORE_FIRST_STEPS'
        FIRST_STEPS = 'FIRST_STEPS'
        QUEST = 'QUEST'
        IN_PLACE = 'IN_PLACE'
        WAITING = 'WAITING'
        REGENERATE_ENERGY = 'regenerate_energy'
        RETURN = 'RETURN'
        RESURRECT = 'RESURRECT'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero=None, bundle_id=None):
        if hero.actions.has_actions:
            return cls(hero=hero,
                       bundle_id=bundle_id,
                       state=cls.STATE.WAITING)
        else:
            return cls(hero=hero,
                       bundle_id=bundle_id,
                       percents=1.0,
                       state=cls.STATE.BEFORE_FIRST_STEPS)

        return True

    def preprocess(self):
        if not self.hero.is_alive:
            ActionResurrectPrototype.create(hero=self.hero)
            self.state = self.STATE.RESURRECT
            return True

        return False

    def process_position(self):
        if self.hero.position.place is None:

            cell = self.hero.position.cell()

            places_cost_modifiers = heroes_logic.get_places_path_modifiers(hero=self.hero)

            path = map_storage.cells.find_path_to_place(from_x=self.hero.position.cell_x,
                                                        from_y=self.hero.position.cell_y,
                                                        to_place_id=cell.nearest_place_id,
                                                        cost_modifiers=places_cost_modifiers,
                                                        risk_level=self.hero.preferences.risk_level)
            path.set_start(self.hero.position.x,
                           self.hero.position.y)

            ActionMoveSimplePrototype.create(hero=self.hero,
                                             path=path,
                                             destination=cell.nearest_place(),
                                             break_at=None)

            self.state = self.STATE.RETURN
        else:
            self.state = self.STATE.IN_PLACE
            ActionInPlacePrototype.create(hero=self.hero)

        return self.state in (self.STATE.IN_PLACE, self.STATE.RETURN)

    def find_task_board_place(self):

        if self.hero.clan_id is None:
            return None

        for place in places_storage.places.all():

            if self.hero.clan_id not in place.attrs.task_board:
                continue

            if self.hero.position.place_id in {p.id for p in places_logic.task_board_places(place)}:
                return place

        return None

    def process(self):

        if self.preprocess():
            return

        if self.state == self.STATE.BEFORE_FIRST_STEPS:
            self.state = self.STATE.FIRST_STEPS
            ActionFirstStepsPrototype.create(hero=self.hero)
            return

        if self.state == self.STATE.FIRST_STEPS:
            self.state = self.STATE.WAITING
            self.percents = 1.0

        if self.state == self.STATE.RESURRECT:
            if self.process_position():
                return
            self.state = self.STATE.WAITING

        if self.state == self.STATE.RETURN:
            self.state = self.STATE.WAITING

        if self.state == self.STATE.IN_PLACE:
            self.state = self.STATE.WAITING

        if self.state == self.STATE.REGENERATE_ENERGY:
            self.state = self.STATE.WAITING

        if self.state == self.STATE.QUEST:
            self.percents = 0  # reset percents only on quest's ending
            if self.process_position():
                return
            self.state = self.STATE.WAITING

        if self.state == self.STATE.WAITING:

            if self.hero.position.place is None:
                self.process_position()
                return

            self.percents += 1.0 / self.hero.idle_length

            task_board_place = self.find_task_board_place()

            if task_board_place is not None:
                self.hero.add_message('action_idleness_task_board', hero=self.hero, clan=clans_storage.infos[self.hero.clan_id])
                self.percents = 1.0

                emissaries_logic.withdraw_event_points(clan_id=self.hero.clan_id,
                                                       place_id=task_board_place.id,
                                                       currency=emissaries_relations.EVENT_CURRENCY.TASK_BOARD)

            if self.percents >= 1.0:
                self.force_quest_action(quest_kwargs={})

            elif self.hero.need_regenerate_energy and not self.hero.preferences.energy_regeneration_type.is_SACRIFICE:
                ActionRegenerateEnergyPrototype.create(hero=self.hero)
                self.state = self.STATE.REGENERATE_ENERGY

            else:
                if random.uniform(0, 1) < 1.0 / c.TURNS_TO_IDLE / 2:  # 1 фраза на два уровня героя
                    self.hero.add_message('action_idleness_waiting', hero=self.hero)

    def force_quest_action(self, quest_kwargs):
        self.state = self.STATE.QUEST
        self.percents = 1.0
        self.hero.actions.current_action.percents = self.percents
        ActionQuestPrototype.create(hero=self.hero, **quest_kwargs)


class ActionQuestPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.QUEST
    TEXTGEN_TYPE = 'action_quest'
    HELP_CHOICES = set((abilities_relations.HELP_CHOICES.HEAL,
                        abilities_relations.HELP_CHOICES.MONEY,
                        abilities_relations.HELP_CHOICES.HEAL_COMPANION))
    APPROVED_FOR_STEPS_CHAIN = False  # all quest actions MUST be done on separated turns

    class STATE(ActionBase.STATE):
        SEARCHING = 'searching'
        PROCESSING = 'processing'
        EQUIPPING = 'equipping'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls,
                hero,
                bundle_id,
                emissary_id=None,
                place_id=None,
                person_id=None,
                person_action=None,
                inner_circle_places=None,
                inner_circle_persons=None):
        return cls(hero=hero,
                   bundle_id=bundle_id,
                   state=cls.STATE.SEARCHING,
                   emissary_id=emissary_id,
                   place_id=place_id,
                   person_id=person_id,
                   person_action=person_action,
                   inner_circle_places=inner_circle_places,
                   inner_circle_persons=inner_circle_persons)

    @property
    def searching_quest(self):
        return self.state == self.STATE.SEARCHING

    def setup_quest(self, quest):
        if self.state != self.STATE.SEARCHING:
            return

        quest.extend_inner_circle(inner_circle_places=self.inner_circle_places,
                                  inner_circle_persons=self.inner_circle_persons)

        self.hero.quests.push_quest(quest)

        self.state = self.STATE.PROCESSING

    def technical_setup_quest_required(self):
        return django_settings.TESTS_RUNNING

    def process(self):

        if self.state == self.STATE.SEARCHING:
            if self.hero.quests.has_quests:
                self.state = self.STATE.PROCESSING
            else:

                if self.emissary_id is not None and self.emissary_id not in emissaries_storage.emissaries:
                    self.state = self.STATE.PROCESSED
                    return

                # a lot of test depands on complete processing of this action
                # so it is easie to emulate quest generation here, then place everywhere mock objects
                if self.technical_setup_quest_required():
                    quests_helpers.setup_quest(self.hero,
                                               emissary_id=self.emissary_id,
                                               place_id=self.place_id,
                                               person_id=self.person_id,
                                               person_action=self.person_action)
                else:
                    quests_logic.request_quest_for_hero(self.hero,
                                                        emissary_id=self.emissary_id,
                                                        place_id=self.place_id,
                                                        person_id=self.person_id,
                                                        person_action=self.person_action)

        if self.state == self.STATE.EQUIPPING:
            self.state = self.STATE.PROCESSING

        if self.state == self.STATE.PROCESSING:

            if not self.hero.quests.has_quests:
                self.state = self.STATE.PROCESSED
                return

            if self.hero.need_equipping:
                self.state = self.STATE.EQUIPPING
                ActionEquippingPrototype.create(hero=self.hero)

            percents = self.hero.quests.current_quest.process()

            self.percents = percents

            if self.hero.quests.current_quest.is_processed:
                self.hero.quests.pop_quest()
                self.state = self.STATE.PROCESSED


class ActionBattlePvE1x1Prototype(ActionBase):

    TYPE = relations.ACTION_TYPE.BATTLE_PVE_1X1
    TEXTGEN_TYPE = 'action_battlepve1x1'
    CONTEXT_MANAGER = contexts.BattleContext
    HABIT_MODE = relations.ACTION_HABIT_MODE.AGGRESSIVE

    @property
    def HELP_CHOICES(self):  # pylint: disable=C0103
        if not self.hero.is_alive:
            return set((abilities_relations.HELP_CHOICES.RESURRECT,))

        if self.mob.health <= 0:
            return set((abilities_relations.HELP_CHOICES.MONEY,
                        abilities_relations.HELP_CHOICES.HEAL,
                        abilities_relations.HELP_CHOICES.HEAL_COMPANION))

        return set((abilities_relations.HELP_CHOICES.MONEY,
                    abilities_relations.HELP_CHOICES.LIGHTING,
                    abilities_relations.HELP_CHOICES.HEAL,
                    abilities_relations.HELP_CHOICES.HEAL_COMPANION))

    class STATE(ActionBase.STATE):
        BATTLE_RUNNING = 'battle_running'

    ###########################################
    # Object operations
    ###########################################

    def get_info_link(self):
        return utils_urls.url('guide:mobs:info', self.mob.record.id)

    @classmethod
    def _create(cls, hero, bundle_id, mob):

        kill_before_battle = hero.can_kill_before_battle()
        can_peacefull_battle = hero.can_peacefull_battle(mob.mob_type)
        can_leave_battle_in_fear = hero.can_leave_battle_in_fear()
        companions_is_exorcist = hero.companion and hero.can_companion_do_exorcism() and random.random() < hero.companion_do_exorcism_probability

        instant_kill_mob = False

        if kill_before_battle:
            percents = 1.0
            state = cls.STATE.PROCESSED
            hero.add_message('action_battlepve1x1_kill_before_start', hero=hero, mob=mob)
            instant_kill_mob = True
        elif can_peacefull_battle:
            percents = 1.0
            state = cls.STATE.PROCESSED
            hero.add_message('action_battlepve1x1_peacefull_battle', hero=hero, mob=mob)
        elif can_leave_battle_in_fear:
            percents = 1.0
            state = cls.STATE.PROCESSED
            hero.add_message('action_battlepve1x1_leave_battle_in_fear', hero=hero, mob=mob)
        elif companions_is_exorcist and (mob.mob_type.is_DEMON or mob.mob_type.is_SUPERNATURAL):
            percents = 1.0
            state = cls.STATE.PROCESSED
            hero.add_message('action_battlepve1x1_companion_do_exorcims', hero=hero, mob=mob, companion=hero.companion)
            instant_kill_mob = True
        else:
            percents = 0.0
            state = cls.STATE.BATTLE_RUNNING
            hero.add_message('action_battlepve1x1_start', hero=hero, mob=mob)

        prototype = cls(hero=hero,
                        bundle_id=bundle_id,
                        context=cls.CONTEXT_MANAGER(),
                        mob=mob,
                        mob_context=cls.CONTEXT_MANAGER(),
                        percents=percents,
                        state=state)

        if instant_kill_mob:
            prototype._kill_mob()

        return prototype

    def get_description_arguments(self):
        args = super(ActionBattlePvE1x1Prototype, self).get_description_arguments()
        args.update({'mob': self.mob})
        return args

    def mob_damage_percents_to_health(self, percents):
        if self.state != self.STATE.BATTLE_RUNNING:
            return 0

        return self.mob.damage_percents_to_health(percents)

    def bit_mob(self, damage):

        if self.state != self.STATE.BATTLE_RUNNING:
            return False

        self.mob.health = max(0, self.mob.health - damage)

        self.percents = 1.0 - self.mob.health_percents
        self.hero.actions.current_action.percents = self.percents

        if self.mob.health <= 0:
            self.on_mob_killed()

        return True

    def fast_resurrect(self):
        if self.state != self.STATE.PROCESSED:  # hero can be dead only if action already processed
            return False

        if self.hero.is_alive:
            return False

        self.hero.resurrect()

        return True

    def _kill_mob(self, hero_alive=True):
        self.mob.kill()
        self.hero.statistics.change_pve_kills(1)

        if not hero_alive:
            return

        loot = artifacts_storage.artifacts.generate_loot(self.hero, self.mob)

        if loot is not None:
            bag_uuid = self.hero.put_loot(loot)

            if bag_uuid is not None:
                if loot.is_useless:
                    self.hero.statistics.change_loot_had(1)
                else:
                    self.hero.statistics.change_artifacts_had(1)
                self.hero.add_message('action_battlepve1x1_put_loot', hero=self.hero, artifact=loot, mob=self.mob)
            else:
                self.hero.add_message('action_battlepve1x1_put_loot_no_space', hero=self.hero, artifact=loot, mob=self.mob)
        else:
            self.hero.add_message('action_battlepve1x1_no_loot', hero=self.hero, mob=self.mob)

        if self.hero.can_get_exp_for_kill():
            raw_experience = int(c.EXP_FOR_KILL * random.uniform(1.0 - c.EXP_FOR_KILL_DELTA, 1.0 + c.EXP_FOR_KILL_DELTA))
            real_experience = self.hero.add_experience(raw_experience)
            self.hero.add_message('action_battlepve1x1_exp_for_kill', hero=self.hero, mob=self.mob, diary=True, experience=real_experience)

        if (self.hero.companion and
            self.hero.companion.health < self.hero.companion.max_health and
            self.hero.can_companion_eat_corpses() and
            random.random() < self.hero.companion_eat_corpses_probability and
                self.mob.is_eatable):
            health = self.hero.companion.heal(c.COMPANIONS_EATEN_CORPSES_HEAL_AMOUNT)
            self.hero.add_message('companions_eat_corpse', companion_owner=self.hero, companion=self.hero.companion, health=health, mob=self.mob)

    def process_artifact_breaking(self):

        self.hero.damage_integrity()

        expected_power = power.Power.normal_total_power_to_level(self.hero.level)

        if random.uniform(0.0, 1.0) > c.ARTIFACTS_BREAKS_PER_BATTLE * (float(self.hero.power.total()) / expected_power)**2:
            return

        artifacts = self.hero.artifacts_to_break()

        if not len(artifacts):
            return

        artifact = utils_logic.random_value_by_priority([(artifact, 1 - artifact.integrity_fraction) for artifact in artifacts])

        artifact.break_it()
        self.hero.add_message('action_battlepve1x1_artifact_broken', hero=self.hero, mob=self.mob, diary=True, artifact=artifact)

    def on_mob_killed(self):
        self.hero.add_message('action_battlepve1x1_mob_killed', hero=self.hero, mob=self.mob)
        self._kill_mob()
        self.state = self.STATE.PROCESSED

    def on_hero_killed(self):
        self.hero.kill()
        self.hero.statistics.change_pve_deaths(1)
        self.hero.add_message('action_battlepve1x1_diary_hero_killed', diary=True, journal=False, hero=self.hero, mob=self.mob)
        self.hero.add_message('action_battlepve1x1_journal_hero_killed', hero=self.hero, mob=self.mob)
        self.state = self.STATE.PROCESSED

    def on_both_killed(self):
        self._kill_mob(hero_alive=False)
        self.hero.kill()
        self.hero.statistics.change_pve_deaths(1)
        self.hero.add_message('action_battlepve1x1_diary_hero_and_mob_killed', diary=True, journal=False, hero=self.hero, mob=self.mob)
        self.hero.add_message('action_battlepve1x1_journal_hero_and_mob_killed', hero=self.hero, mob=self.mob)
        self.state = self.STATE.PROCESSED

    def process(self):

        if self.state == self.STATE.BATTLE_RUNNING:

            # make turn only if mob still alive (it can be killed by angel)
            if self.mob.health > 0:
                battle.make_turn(battle.Actor(self.hero, self.context),
                                 battle.Actor(self.mob, self.mob_context),
                                 self.hero)
                self.percents = 1.0 - self.mob.health_percents

            if self.hero.health <= 0:
                if self.mob.health <= 0:
                    self.on_both_killed()
                else:
                    self.on_hero_killed()

            elif self.mob.health <= 0:
                self.on_mob_killed()

            if self.state == self.STATE.PROCESSED:
                self.process_artifact_breaking()


class ActionResurrectPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.RESURRECT
    TEXTGEN_TYPE = 'action_resurrect'
    HELP_CHOICES = set((abilities_relations.HELP_CHOICES.RESURRECT,))

    class STATE(ActionBase.STATE):
        RESURRECT = 'resurrect'

    @classmethod
    def _create(cls, hero, bundle_id):
        hero.add_message('action_resurrect_start', hero=hero)

        return cls(hero=hero,
                   bundle_id=bundle_id,
                   state=cls.STATE.RESURRECT)

    def fast_resurrect(self):
        if self.state != self.STATE.RESURRECT:
            return False

        self.hero.actions.current_action.percents = self.percents

        self.hero.resurrect()
        self.state = self.STATE.PROCESSED

        return True

    def process(self):

        if self.state == self.STATE.RESURRECT:

            self.percents += 1.0 / self.hero.resurrect_length

            if random.uniform(0, 1) < 1.0 / c.TURNS_TO_RESURRECT / 2:  # 1 фраза на два уровня героя
                self.hero.add_message('action_resurrect_resurrecting', hero=self.hero)

            if self.percents >= 1:
                self.hero.resurrect()
                self.state = self.STATE.PROCESSED
                self.hero.add_message('action_resurrect_finish', hero=self.hero)


class ActionFirstStepsPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.FIRST_STEPS
    TEXTGEN_TYPE = 'action_first_steps'
    HELP_CHOICES = set((abilities_relations.HELP_CHOICES.MONEY,))

    class STATE(ActionBase.STATE):
        THINK_ABOUT_INITIATION = 'THINK_ABOUT_INITIATION'
        THINK_ABOUT_FUTURE = 'THINK_ABOUT_FUTURE'
        THINK_ABOUT_HEROES = 'THINK_ABOUT_HEROES'

    @classmethod
    def _create(cls, hero, bundle_id):
        hero.add_message('action_first_steps_initiation_diary', diary=True, hero=hero, place=hero.position.place)
        hero.add_message('action_first_steps_initiation', hero=hero, place=hero.position.place)

        return cls(hero=hero,
                   bundle_id=bundle_id,
                   state=cls.STATE.THINK_ABOUT_INITIATION)

    def process(self):

        if self.state == self.STATE.THINK_ABOUT_INITIATION:
            self.percents = 0.33
            self.hero.add_message('action_first_steps_future', hero=self.hero, place=self.hero.position.place)
            self.state = self.STATE.THINK_ABOUT_FUTURE
            return

        if self.state == self.STATE.THINK_ABOUT_FUTURE:
            self.percents = 0.66
            self.hero.add_message('action_first_steps_heroes', hero=self.hero, place=self.hero.position.place)
            self.state = self.STATE.THINK_ABOUT_HEROES
            return

        if self.state == self.STATE.THINK_ABOUT_HEROES:
            self.percents = 1.0
            self.hero.add_message('action_first_steps_now', hero=self.hero, place=self.hero.position.place)
            self.state = self.STATE.PROCESSED
            return


class ActionInPlacePrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.IN_PLACE
    TEXTGEN_TYPE = 'action_inplace'
    HELP_CHOICES = set((abilities_relations.HELP_CHOICES.HEAL,
                        abilities_relations.HELP_CHOICES.MONEY,
                        abilities_relations.HELP_CHOICES.HEAL_COMPANION))

    class STATE(ActionBase.STATE):
        SPEND_MONEY = 'spend_money'
        REGENERATE_ENERGY = 'regenerate_energy'
        CHOOSING = 'choosing'
        TRADING = 'trading'
        RESTING = 'resting'
        EQUIPPING = 'equipping'
        HEALING_COMPANION = 'healing_companion'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        prototype = cls(hero=hero,
                        bundle_id=bundle_id,
                        state=cls.STATE.SPEND_MONEY)

        if hero.companion and hero.position.moved_out_place:
            # спутники, покидающие героя, должны уходить до входа в город
            if random.random() < hero.companion_leave_in_place_probability:
                hero.add_message('companions_left', diary=True, companion_owner=hero, companion=hero.companion)
                hero.remove_companion()

        if hero.health < hero.max_health and random.random() < hero.position.place.attrs.hero_regen_chance:
            hero.health = hero.max_health
            hero.add_message('action_inplace_instant_heal',
                             hero=hero,
                             place=hero.position.place)

        if hero.companion_need_heal() and random.random() < hero.position.place.attrs.companion_regen_chance:
            healed_health = hero.companion.heal(c.COMPANIONS_HEAL_AMOUNT)
            hero.add_message('action_inplace_companion_heal',
                             hero=hero,
                             place=hero.position.place,
                             companion=hero.companion,
                             health=healed_health)

        if hero.companion_need_heal() and hero.clan_id in hero.position.place.attrs.companions_support:
            healed_health = hero.companion.heal(c.COMPANIONS_HEAL_AMOUNT)

            hero.add_message('action_inplace_clan_companions_support',
                             hero=hero,
                             place=hero.position.place,
                             clan=clans_storage.infos[hero.clan_id],
                             companion=hero.companion,
                             health=healed_health)

            emissaries_logic.withdraw_event_points(clan_id=hero.clan_id,
                                                   place_id=hero.position.place_id,
                                                   currency=emissaries_relations.EVENT_CURRENCY.COMPANIONS_SUPPORT)

        # process variouse effects only if it is not repeated town visit
        if hero.position.place == hero.position.previous_place:
            return prototype

        hero.add_message('action_inplace_enter', hero=hero, place=hero.position.place)

        if (hero.can_regenerate_energy and
                random.random() < hero.position.place.attrs.energy_regen_chance):

            game_tt_services.energy.cmd_change_balance(account_id=hero.account_id,
                                                       type='inplace_regen',
                                                       amount=c.ANGEL_ENERGY_INSTANT_REGENERATION_IN_PLACE,
                                                       asynchronous=True,
                                                       autocommit=True)

            hero.add_message('action_inplace_instant_energy_regen',
                             hero=hero,
                             place=hero.position.place,
                             energy=c.ANGEL_ENERGY_INSTANT_REGENERATION_IN_PLACE)

        if hero.position.place.attrs.tax > 0:

            if hero.money > 0:
                tax = int(hero.money * hero.position.place.attrs.tax)
                hero.change_money(heroes_relations.MONEY_SOURCE.SPEND_FOR_TAX, -tax)
                hero.add_message('action_inplace_tax', hero=hero, place=hero.position.place, coins=tax, diary=True)
            else:
                hero.add_message('action_inplace_tax_no_money', hero=hero, place=hero.position.place, diary=True)

        if hero.position.place.can_habit_event():

            if random.uniform(0, 1) < 0.5:
                hero.add_message('action_inplace_habit_event_honor_%s' % hero.position.place.habit_honor.interval.name.lower(),
                                 hero=hero, place=hero.position.place, diary=True)
            else:
                hero.add_message('action_inplace_habit_event_peacefulness_%s' % hero.position.place.habit_peacefulness.interval.name.lower(),
                                 hero=hero, place=hero.position.place, diary=True)

        if hero.companion and hero.position.moved_out_place:
            if hero.can_companion_eat():
                expected_coins = (f.expected_gold_in_day(hero.level) *
                                  float(game_turn.number() - hero.position.last_place_visited_turn) / (c.TURNS_IN_HOUR * 24))
                coins = min(hero.money, int(expected_coins * hero.companion_money_for_food_multiplier))

                if coins > 0:
                    hero.change_money(heroes_relations.MONEY_SOURCE.SPEND_FOR_COMPANIONS, -coins)
                    hero.add_message('action_inplace_companion_money_for_food', hero=hero, place=hero.position.place, companion=hero.companion, coins=coins)

            if not hero.bag.is_empty and hero.can_companion_drink_artifact() and random.random() < hero.companion_drink_artifact_probability:
                artifact = random.choice(list(hero.bag.values()))
                hero.pop_loot(artifact)
                hero.add_message('action_inplace_companion_drink_artifact', hero=hero, place=hero.position.place, artifact=artifact, companion=hero.companion)

        hero.position.move_in_place()  # <- must be last method

        return prototype

    def action_event_message_arguments(self):
        return {'place': self.hero.position.place}

    def get_description_arguments(self):
        args = super(ActionInPlacePrototype, self).get_description_arguments()
        args.update({'place': self.hero.position.place})
        return args

    def process(self):
        return self.process_settlement()

    def spend_amount(self):
        return int(max(1, self.hero.spend_amount * self.hero.buy_price()))

    def try_to_spend_money(self):
        gold_amount = self.spend_amount()

        if gold_amount <= self.hero.money:
            self.hero.change_money(self.hero.next_spending.money_source, -gold_amount)
            self.hero.switch_spending()
            return gold_amount

        return None

    def spend_money__instant_heal(self):
        if self.hero.health > self.hero.max_health * c.SPEND_MONEY_FOR_HEAL_HEALTH_FRACTION:
            if self.spend_amount() <= self.hero.money:
                self.hero.switch_spending()
            return

        coins = self.try_to_spend_money()
        if coins is not None:
            healed_health = self.hero.heal(self.hero.max_health)
            self.hero.add_message('action_inplace_diary_instant_heal_for_money', diary=True, hero=self.hero, coins=coins, health=healed_health)

    def spend_money__buying_artifact(self):
        if self.hero.need_equipping:
            # delay money spenging, becouse hero can buy artifact better then equipped but worse then he has in bag
            return

        coins = self.try_to_spend_money()
        if coins is not None:

            artifact, unequipped, sell_price = self.hero.receive_artifact(equip=True,
                                                                          better=True,
                                                                          prefered_slot=True,
                                                                          prefered_item=True,
                                                                          archetype=True,
                                                                          power_bonus=self.hero.buy_artifact_power_bonus())

            if unequipped is not None:
                if artifact.id == unequipped.id:
                    self.hero.add_message('action_inplace_diary_buying_artifact_and_change_equal_items', diary=True,
                                          hero=self.hero, artifact=artifact, coins=coins, sell_price=sell_price)
                else:
                    self.hero.add_message('action_inplace_diary_buying_artifact_and_change', diary=True,
                                          hero=self.hero, artifact=artifact, coins=coins, old_artifact=unequipped, sell_price=sell_price)
            else:
                self.hero.add_message('action_inplace_diary_buying_artifact', diary=True, hero=self.hero, coins=coins, artifact=artifact)

    def spend_money__sharpening_artifact(self):
        coins = self.try_to_spend_money()
        if coins is not None:
            artifact = self.hero.sharp_artifact()

            self.hero.add_message('action_inplace_diary_sharpening_artifact', diary=True, hero=self.hero, coins=coins, artifact=artifact)

    def spend_money__repairing_artifact(self):
        coins = self.try_to_spend_money()
        if coins is not None:
            artifact = self.hero.repair_artifact()

            self.hero.add_message('action_inplace_diary_repairing_artifact', diary=True, hero=self.hero, coins=coins, artifact=artifact)

    def spend_money__useless(self):
        coins = self.try_to_spend_money()
        if coins is not None:
            self.hero.add_message('action_inplace_diary_spend_useless', diary=True, hero=self.hero, coins=coins)

    def spend_money__impact(self):
        coins = self.try_to_spend_money()

        if coins is None:
            return

        choices = []

        if self.hero.preferences.friend is not None and self.hero.preferences.friend.place.id == self.hero.position.place.id:
            choices.append((True, self.hero.preferences.friend))

        if self.hero.preferences.enemy is not None and self.hero.preferences.enemy.place.id == self.hero.position.place.id:
            choices.append((False, self.hero.preferences.enemy))

        if not choices:
            choices.append((random.choice([True, False]), random.choice(self.hero.position.place.persons)))

        impact_type, person = random.choice(choices)

        if impact_type:
            power_direction = 1
            self.hero.add_message('action_inplace_diary_impact_good', diary=True, hero=self.hero, coins=coins, person=person)
        else:
            power_direction = -1
            self.hero.add_message('action_inplace_diary_impact_bad', diary=True, hero=self.hero, coins=coins, person=person)

        if not self.hero.can_change_person_power(person):
            return

        power = power_direction * f.person_power_for_quest(places_storage.places.expected_minimum_quest_distance())

        impacts = list(persons_logic.impacts_from_hero(self.hero, person, power, inner_circle_places=set(), inner_circle_persons=set()))

        politic_power_logic.add_power_impacts(impacts)

    def spend_money__experience(self):
        coins = self.try_to_spend_money()

        if coins is not None:
            experience = int(c.BASE_EXPERIENCE_FOR_MONEY_SPEND * (1.0 + random.uniform(-c.EXPERIENCE_DELTA_FOR_MONEY_SPEND, c.EXPERIENCE_DELTA_FOR_MONEY_SPEND)) + 1)
            self.hero.add_experience(experience)
            self.hero.add_message('action_inplace_diary_experience', diary=True, hero=self.hero, coins=coins, experience=experience)

    def spend_money__heal_companion(self):
        if self.hero.companion is None:
            self.hero.switch_spending()
            return

        if self.hero.companion.health == self.hero.companion.max_health:
            if self.spend_amount() <= self.hero.money:
                self.hero.switch_spending()
            return

        coins = self.try_to_spend_money()
        if coins is not None:
            health = self.hero.companion.heal(c.COMPANIONS_REGEN_BY_MONEY_SPEND)
            self.hero.add_message('action_inplace_diary_heal_companion_healed',
                                  diary=True, place=self.hero.position.place, hero=self.hero, coins=coins, companion=self.hero.companion, health=health)

    def spend_money(self):

        if self.hero.next_spending.is_INSTANT_HEAL:
            self.spend_money__instant_heal()

        elif self.hero.next_spending.is_BUYING_ARTIFACT:
            self.spend_money__buying_artifact()
        elif self.hero.next_spending.is_SHARPENING_ARTIFACT:
            self.spend_money__sharpening_artifact()

        elif self.hero.next_spending.is_REPAIRING_ARTIFACT:
            self.spend_money__repairing_artifact()

        elif self.hero.next_spending.is_USELESS:
            self.spend_money__useless()

        elif self.hero.next_spending.is_IMPACT:
            self.spend_money__impact()

        elif self.hero.next_spending.is_EXPERIENCE:
            self.spend_money__experience()

        elif self.hero.next_spending.is_HEAL_COMPANION:
            self.spend_money__heal_companion()

        else:
            raise exceptions.WrongHeroMoneySpendType(spending=self.hero.next_spending)

    def process_companion_stealing(self):

        if self.hero.companion is None:
            return

        if self.hero.position.place == self.hero.position.previous_place:
            return

        if self.hero.can_companion_steal_money():
            money = int(f.normal_loot_cost_at_lvl(self.hero.level) * random.uniform(0.8, 1.2) * self.hero.companion_steal_money_modifier) + 1
            self.hero.change_money(heroes_relations.MONEY_SOURCE.EARNED_FROM_COMPANIONS, money)
            self.hero.add_message('action_inplace_companion_steal_money', hero=self.hero, place=self.hero.position.place, companion=self.hero.companion, coins=money)

        if self.hero.can_companion_steal_item() and not self.hero.bag_is_full:
            loot = artifacts_storage.artifacts.generate_any_artifact(self.hero, artifact_probability_multiplier=self.hero.companion_steal_artifact_probability_multiplier)

            self.hero.put_loot(loot)

            if loot.is_useless:
                self.hero.statistics.change_loot_had(1)
            else:
                self.hero.statistics.change_artifacts_had(1)

            self.hero.add_message('action_inplace_companion_steal_item', hero=self.hero, place=self.hero.position.place, artifact=loot, companion=self.hero.companion)

    def process_settlement(self):

        if self.state == self.STATE.SPEND_MONEY:
            self.state = self.STATE.CHOOSING
            self.spend_money()

        if self.state in [self.STATE.RESTING, self.STATE.HEALING_COMPANION, self.STATE.EQUIPPING, self.STATE.TRADING, self.STATE.REGENERATE_ENERGY]:
            self.state = self.STATE.CHOOSING

        if self.state == self.STATE.CHOOSING:

            if random.uniform(0, 1) < c.HABIT_IN_PLACE_EVENTS_IN_TURN:
                self.do_events()

            if self.hero.need_regenerate_energy and not self.hero.preferences.energy_regeneration_type.is_SACRIFICE:
                self.state = self.STATE.REGENERATE_ENERGY
                ActionRegenerateEnergyPrototype.create(hero=self.hero)

            elif self.hero.need_rest_in_settlement:
                self.state = self.STATE.RESTING
                ActionRestPrototype.create(hero=self.hero)

            elif self.hero.companion_need_heal_action():
                self.state = self.STATE.HEALING_COMPANION
                ActionHealCompanionPrototype.create(hero=self.hero)

            elif self.hero.need_equipping:
                self.state = self.STATE.EQUIPPING
                ActionEquippingPrototype.create(hero=self.hero)

            elif self.hero.need_trade_in_town:
                self.state = self.STATE.TRADING
                ActionTradingPrototype.create(hero=self.hero)

            else:
                self.state = self.STATE.PROCESSED

        if self.state == self.STATE.PROCESSED:
            self.process_companion_stealing()
            self.hero.position.update_previous_place()


class ActionRestPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.REST
    TEXTGEN_TYPE = 'action_rest'
    HELP_CHOICES = set((abilities_relations.HELP_CHOICES.HEAL,
                        abilities_relations.HELP_CHOICES.MONEY,
                        abilities_relations.HELP_CHOICES.HEAL_COMPANION))

    class STATE(ActionBase.STATE):
        RESTING = 'resting'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        prototype = cls(hero=hero,
                        bundle_id=bundle_id,
                        state=cls.STATE.RESTING)
        hero.add_message('action_rest_start', hero=hero)
        return prototype

    def on_heal(self):
        self.percents = float(self.hero.health) / self.hero.max_health
        self.hero.actions.current_action.percents = self.percents

        if self.hero.health >= self.hero.max_health:
            self.state = self.STATE.PROCESSED

    def process(self):

        if self.hero.health >= self.hero.max_health:
            self.state = self.STATE.PROCESSED

        if self.state == self.STATE.RESTING:

            heal_amount = int(round(float(self.hero.max_health) / self.hero.rest_length * (1 + random.uniform(-c.HEAL_STEP_FRACTION, c.HEAL_STEP_FRACTION))))

            heal_amount = self.hero.heal(heal_amount)

            if random.uniform(0, 1) < 0.2:
                self.hero.add_message('action_rest_resring', hero=self.hero, health=heal_amount)

            self.percents = float(self.hero.health) / self.hero.max_health

            if self.hero.health >= self.hero.max_health:
                self.state = self.STATE.PROCESSED

        if self.state == self.STATE.PROCESSED:
            self.hero.health = self.hero.max_health


class ActionEquippingPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.EQUIPPING
    TEXTGEN_TYPE = 'action_equipping'
    HELP_CHOICES = set((abilities_relations.HELP_CHOICES.HEAL,
                        abilities_relations.HELP_CHOICES.MONEY,
                        abilities_relations.HELP_CHOICES.HEAL_COMPANION))

    class STATE(ActionBase.STATE):
        EQUIPPING = 'equipping'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        return cls(hero=hero,
                   bundle_id=bundle_id,
                   state=cls.STATE.EQUIPPING)

    def process(self):

        if self.state == self.STATE.EQUIPPING:
            # TODO: calculate real percents
            self.percents = min(self.percents + 0.25, 1)

            slot, unequipped, equipped = self.hero.equip_from_bag()

            if equipped:
                if unequipped:
                    if equipped.id == unequipped.id:
                        self.hero.add_message('action_equipping_diary_change_equal_items', diary=True, hero=self.hero, item=equipped)
                    else:
                        self.hero.add_message('action_equipping_diary_change_item', diary=True, hero=self.hero, unequipped=unequipped, equipped=equipped)
                else:
                    self.hero.add_message('action_equipping_diary_equip_item', diary=True, hero=self.hero, equipped=equipped)
            else:
                self.state = self.STATE.PROCESSED


class ActionTradingPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.TRADING
    TEXTGEN_TYPE = 'action_trading'
    HELP_CHOICES = set((abilities_relations.HELP_CHOICES.HEAL,
                        abilities_relations.HELP_CHOICES.MONEY,
                        abilities_relations.HELP_CHOICES.HEAL_COMPANION))

    class STATE(ActionBase.STATE):
        TRADING = 'trading'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        prototype = cls(hero=hero,
                        bundle_id=bundle_id,
                        percents_barier=hero.bag.occupation,
                        state=cls.STATE.TRADING)
        hero.add_message('action_trading_start', hero=hero)
        return prototype

    def process(self):

        if self.replane_required:
            self.state = self.STATE.PROCESSED
            return

        if self.state == self.STATE.TRADING:

            if not self.hero.bag.is_empty:
                artifact = random.choice(list(self.hero.bag.values()))
                sell_price = self.hero.sell_artifact(artifact)
                self.hero.add_message('action_trading_sell_item', hero=self.hero, artifact=artifact, coins=sell_price)

            loot_items_count = self.hero.bag.occupation  # pylint: disable=W0612

            if loot_items_count:
                self.percents = 1 - float(loot_items_count - 1) / self.percents_barier
            else:
                self.state = self.STATE.PROCESSED


class ActionRegenerateEnergyPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.REGENERATE_ENERGY
    TEXTGEN_TYPE = 'action_regenerate_energy'
    HELP_CHOICES = set((abilities_relations.HELP_CHOICES.MONEY,
                        abilities_relations.HELP_CHOICES.HEAL,
                        abilities_relations.HELP_CHOICES.HEAL_COMPANION))

    class STATE(ActionBase.STATE):
        REGENERATE = 'REGENERATE'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        textgen_id = 'action_regenerate_energy_%s' % random.choice(hero.preferences.energy_regeneration_type.linguistics_slugs)

        prototype = cls(hero=hero,
                        bundle_id=bundle_id,
                        state=cls.STATE.REGENERATE,
                        textgen_id=textgen_id)

        hero.add_message('%s_start' % textgen_id, hero=hero)

        return prototype

    @property
    def description_text_name(self):
        return '%s_description' % self.textgen_id

    @property
    def regeneration_type(self):
        return self.hero.preferences.energy_regeneration_type

    def step_percents(self):
        return 1.0 / self.regeneration_type.length

    def process(self):

        if self.state == self.STATE.REGENERATE:

            self.percents += self.step_percents()

            if self.percents >= 1:
                self.hero.last_energy_regeneration_at_turn = game_turn.number()

                if self.hero.can_regenerate_energy:
                    multiplier = 2 if self.hero.can_regenerate_double_energy else 1

                    energy_delta = self.regeneration_type.amount * multiplier

                    game_tt_services.energy.cmd_change_balance(account_id=self.hero.account_id,
                                                               type='energy_regeneration',
                                                               amount=energy_delta,
                                                               asynchronous=True,
                                                               autocommit=True)

                    self.hero.add_message('%s_energy_received' % self.textgen_id, hero=self.hero, energy=energy_delta)
                else:
                    self.hero.add_message('%s_no_energy_received' % self.textgen_id, hero=self.hero, energy=0)

                self.state = self.STATE.PROCESSED


class ActionDoNothingPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.DO_NOTHING
    TEXTGEN_TYPE = 'no texgen type'
    HELP_CHOICES = set((abilities_relations.HELP_CHOICES.HEAL,
                        abilities_relations.HELP_CHOICES.MONEY,
                        abilities_relations.HELP_CHOICES.HEAL_COMPANION))

    class STATE(ActionBase.STATE):
        DO_NOTHING = 'DO_NOTHING'

    @property
    def description_text_name(self):
        return '%s_description' % self.textgen_id

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id, duration, messages_prefix, messages_probability):
        prototype = cls(hero=hero,
                        bundle_id=bundle_id,
                        percents_barier=duration,
                        extra_probability=messages_probability,
                        textgen_id=messages_prefix,
                        state=cls.STATE.DO_NOTHING)
        hero.add_message('%s_start' % messages_prefix, hero=hero)
        return prototype

    def process(self):

        if self.state == self.STATE.DO_NOTHING:

            self.percents += 1.0001 / self.percents_barier

            if self.extra_probability is not None and random.uniform(0, 1) < self.extra_probability:
                self.hero.add_message('%s_donothing' % self.textgen_id, hero=self.hero)

            if self.percents >= 1.0:
                self.state = self.STATE.PROCESSED


class ActionMetaProxyPrototype(ActionBase):

    SINGLE = False
    TYPE = relations.ACTION_TYPE.META_PROXY
    TEXTGEN_TYPE = 'no texgen type'
    APPROVED_FOR_STEPS_CHAIN = False

    @property
    def HELP_CHOICES(self):
        return self.meta_action.help_choices()

    @property
    def description_text_name(self):
        return self.meta_action.description_text_name

    def get_description_arguments(self):
        if self.meta_action.storage:
            hero_2 = self.meta_action.hero_2 if self.hero.id == self.meta_action.hero_1_id else self.meta_action.hero_1
        else:
            hero_2_id = self.meta_action.hero_2_id if self.hero.id == self.meta_action.hero_1_id else self.meta_action.hero_1_id
            hero_2 = heroes_logic.load_hero(hero_id=hero_2_id)

        return {'duelist_1': self.hero,
                'duelist_2': hero_2}

    @property
    def ui_type(self):
        return self.meta_action.TYPE

    def ui_info(self):
        info = super().ui_info()
        info['data'] = self.meta_action.ui_info(self.hero)
        return info

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id, meta_action):
        return cls(hero=hero,
                   bundle_id=bundle_id,
                   meta_action=meta_action,
                   state=meta_action.state)

    def process(self):

        if not self.meta_action.is_valid():
            # rollback action if we something go wrong
            # for example, we lost one of heroes (due user removed its account)
            self.meta_action.cancel()
        else:
            self.meta_action.process()

        self.state = self.meta_action.state
        self.percents = self.meta_action.percents


class ActionHealCompanionPrototype(ActionBase):

    TYPE = relations.ACTION_TYPE.HEAL_COMPANION
    TEXTGEN_TYPE = 'action_heal_companion'
    HELP_CHOICES = set((abilities_relations.HELP_CHOICES.HEAL_COMPANION, ))

    HABIT_MODE = relations.ACTION_HABIT_MODE.COMPANION

    class STATE(ActionBase.STATE):
        HEALING = 'healing'

    def get_description_arguments(self):
        args = super(ActionHealCompanionPrototype, self).get_description_arguments()
        if self.hero.companion:
            args.update({'companion': self.hero.companion})
        return args

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id):
        prototype = cls(hero=hero,
                        bundle_id=bundle_id,
                        state=cls.STATE.HEALING)
        hero.companion.on_heal_started()
        hero.add_message('action_heal_companion_start', hero=hero, companion=hero.companion)
        return prototype

    def after_processed(self):
        if self.hero.companion is None:
            return

        health = self.hero.companion.heal(c.COMPANIONS_HEALTH_PER_HEAL)
        if health > 0:
            self.hero.add_message('action_heal_companion_finish', hero=self.hero, companion=self.hero.companion, health=health)
        else:
            self.hero.add_message('action_heal_companion_finish_without_healing', hero=self.hero, companion=self.hero.companion)

        if self.hero.can_companion_exp_per_heal() and random.random() < self.hero.companion_exp_per_heal_probability:
            self.hero.add_experience(c.COMPANIONS_EXP_PER_HEAL, without_modifications=True)

        if (self.hero.companion.health < self.hero.companion.max_health and
            self.hero.can_companion_regenerate() and
                random.random() < self.hero.companion_regenerate_probability):
            health = self.hero.companion.heal(utils_logic.randint_from_1(c.COMPANIONS_REGEN_ON_HEAL_AMOUNT))
            self.hero.add_message('companions_regenerate', companion_owner=self.hero, companion=self.hero.companion, health=health)

        if (self.hero.companion.health < self.hero.companion.max_health and random.random() < self.hero.companion_heal_probability):
            health = self.hero.companion.heal(utils_logic.randint_from_1(c.COMPANIONS_REGEN_BY_HERO))
            self.hero.add_message('hero_ability_companion_healing', actor=self.hero, companion=self.hero.companion, health=health)

    def on_heal_companion(self):
        if self.hero.companion is None:
            self.state = self.STATE.PROCESSED
            return

        if self.hero.companion.health >= self.hero.companion.max_health:
            self.state = self.STATE.PROCESSED

        heal_length = f.companions_heal_length(self.hero.companion.health, self.hero.companion.max_health)

        self.percents += 1.0 / heal_length

        if self.percents >= 1.0 or self.hero.companion.health == self.hero.companion.max_health:
            self.percents = 1
            self.state = self.STATE.PROCESSED

    def process(self):

        if self.hero.companion is None:
            self.state = self.STATE.PROCESSED
            return

        if self.hero.companion.health >= self.hero.companion.max_health:
            self.hero.companion.health = self.hero.companion.max_health
            self.state = self.STATE.PROCESSED

        if self.state == self.STATE.HEALING:

            heal_length = f.companions_heal_length(self.hero.companion.health, self.hero.companion.max_health)

            self.percents += 1.0 / heal_length

            if random.uniform(0, 1) < 0.1:
                self.hero.add_message('action_heal_companion_healing', hero=self.hero, companion=self.hero.companion)

            if self.percents >= 1.0:
                self.percents = 1
                self.state = self.STATE.PROCESSED

        if self.state == self.STATE.PROCESSED:
            self.after_processed()


class ActionMoveSimplePrototype(ActionBase):
    TYPE = relations.ACTION_TYPE.MOVE_SIMPLE
    TEXTGEN_TYPE = 'no texgen type'

    @property
    def HELP_CHOICES(self):
        choices = set((abilities_relations.HELP_CHOICES.HEAL,
                       abilities_relations.HELP_CHOICES.MONEY,
                       abilities_relations.HELP_CHOICES.HEAL_COMPANION))

        if self.state == self.STATE.MOVING:
            choices.add(abilities_relations.HELP_CHOICES.TELEPORT)

        return choices

    class STATE(ActionBase.STATE):
        MOVING = 'MOVING'
        BATTLE = 'BATTLE'
        REGENERATE_ENERGY = 'REGENERATE_ENERGY'
        RESTING = 'RESTING'
        RESURRECT = 'RESURRECT'
        IN_CITY = 'IN_CITY'
        HEALING_COMPANION = 'HEALING_COMPANION'

    ###########################################
    # Object operations
    ###########################################

    @classmethod
    def _create(cls, hero, bundle_id, path, destination, break_at):
        prototype = cls(hero=hero,
                        bundle_id=bundle_id,
                        place_id=destination.id if destination else None,
                        break_at=break_at,
                        path=path,
                        state=cls.STATE.MOVING)

        leave_place = hero.position.place_id is not None and destination

        if leave_place:
            hero.add_message('action_move_simple_to_start', hero=hero, destination=destination)

        hero.position.move_out_place()

        teleported = False

        if leave_place:
            teleported = prototype.try_to_teleport_with_clan()

        if not teleported:
            teleported = prototype.try_to_teleport_with_companion()

        return prototype

    @property
    def destination_id(self):
        return self.place_id

    @property
    def destination(self):
        return self.place

    def stop_percents(self):
        return self.break_at if self.break_at else 1

    @property
    def description_text_name(self):
        if self.destination:
            return 'action_move_simple_to_description'

        return 'action_move_simple_near_description'

    def get_description_arguments(self):
        args = super().get_description_arguments()

        if self.destination:
            args['destination'] = self.destination
        else:
            x, y = self.path.destination_coordinates()
            args['place'] = map_storage.cells(x, y).nearest_place()

        return args

    def journal_message(self):
        cell = self.hero.position.cell()

        current_destination_percent, current_destination_id = self.path.next_place_at(self.percents)

        if not cell.roads_ids or self.destination is None or current_destination_id is None:
            # для фраз хождения в окрестностях города всегда используем доминирующий город либо ближайший, вместо точки назначения
            # так как герой может идти не по дороге очень далеко от неё.
            place = cell.dominant_place()

            if place is None:
                place = cell.nearest_place()

            self.hero.add_message('action_move_simple_near_walk', hero=self.hero, place=place)
            return

        current_destination = places_storage.places[current_destination_id]

        if self.destination_id != current_destination_id and random.uniform(0, 1) < 0.25:
            self.hero.add_message('action_move_simple_to_move_long_path',
                                  hero=self.hero,
                                  destination=self.destination,
                                  current_destination=current_destination)
        else:
            self.hero.add_message('action_move_simple_to_move',
                                  hero=self.hero,
                                  destination=self.destination,
                                  current_destination=current_destination)

    def _teleport_to(self, percents, create_inplace_action):
        self.percents = percents

        self.after_move(create_inplace_action=create_inplace_action)

        return True

    def teleport(self, distance, create_inplace_action):

        if self.state != self.STATE.MOVING:
            return False

        if self.path.length <= 0:
            return False

        new_percents = min(self.percents + distance / self.path.length, self.stop_percents())

        if create_inplace_action:
            current_destination_percent, current_destination_id = self.path.next_place_at(self.percents)

            if current_destination_id is not None:
                new_percents = min(new_percents, current_destination_percent)

        return self._teleport_to(new_percents, create_inplace_action)

    def teleport_to_place(self, create_inplace_action, check_moving_state=True):
        if check_moving_state and self.state != self.STATE.MOVING:
            return False

        current_destination_percents, current_destination_id = self.path.next_place_at(self.percents)

        if current_destination_id is None:
            return False

        new_percents = min(self.stop_percents(), current_destination_percents)

        return self._teleport_to(new_percents, create_inplace_action)

    def teleport_to_end(self):
        if self.state != self.STATE.MOVING:
            return False

        return self._teleport_to(self.stop_percents(), create_inplace_action=True)

    def picked_up_in_road(self):
        # save destination befor teleport, since it can be reseted after we perfom it
        current_destination_percents, current_destination_id = self.path.next_place_at(self.percents)

        if current_destination_id is None:
            return False

        current_destination = places_storage.places[current_destination_id]

        if self.teleport(c.PICKED_UP_IN_ROAD_TELEPORT_LENGTH, create_inplace_action=True):
            self.hero.add_message('action_move_simple_to_picked_up_in_road',
                                  hero=self.hero,
                                  destination=current_destination)

            return True

        return False

    def fly_with_companion(self):
        if self.teleport(c.ANGEL_HELP_TELEPORT_DISTANCE, create_inplace_action=True):
            self.hero.add_message('companions_fly',
                                  companion_owner=self.hero,
                                  companion=self.hero.companion)
            return True

        return False

    def teleport_with_companion(self):
        # save destination befor teleport, since it can be reseted after we perfom it
        current_destination_percents, current_destination_id = self.path.next_place_at(self.percents)

        if current_destination_id is None:
            return False

        current_destination = places_storage.places[current_destination_id]

        # store companion, since it can be removed at place
        companion = self.hero.companion

        if self.teleport_to_place(create_inplace_action=True, check_moving_state=False):
            self.hero.add_message('companions_teleport',
                                  companion_owner=self.hero,
                                  companion=companion,
                                  destination=current_destination)
            return True

        return False

    def teleport_with_clan(self):

        # save destination befor teleport, since it can be reseted after we perfom it
        current_destination_percents, current_destination_id = self.path.next_place_at(self.percents)

        if current_destination_id is None:
            return False

        current_destination = places_storage.places[current_destination_id]

        if self.teleport_to_place(create_inplace_action=True, check_moving_state=False):
            self.hero.add_message('action_move_simple_to_teleport_with_clan',
                                  hero=self.hero,
                                  clan=clans_storage.infos[self.hero.clan_id],
                                  current_destination=current_destination)
            return True

    def place_hero_in_current_place(self, create_action=True):
        self.hero.position.set_place(self.hero.position.cell().place())
        self.state = self.STATE.IN_CITY

        if create_action:
            ActionInPlacePrototype.create(hero=self.hero)
            return True

        return False

    def preprocess(self):

        if self.state == self.STATE.IN_CITY and self.percents == 1:
            self.state = self.STATE.PROCESSED
            return True

        if self.replane_required:
            self.state = self.STATE.PROCESSED
            return True

        if not self.hero.is_alive:
            ActionResurrectPrototype.create(hero=self.hero)
            self.state = self.STATE.RESURRECT
            return True

        if self.hero.need_rest_in_move:
            ActionRestPrototype.create(hero=self.hero)
            self.state = self.STATE.RESTING
            return True

        if self.hero.companion_need_heal_action():
            ActionHealCompanionPrototype.create(hero=self.hero)
            self.state = self.STATE.HEALING_COMPANION
            return True

        return False

    def process_battle(self):

        if self.hero.need_regenerate_energy:
            ActionRegenerateEnergyPrototype.create(hero=self.hero)
            self.state = self.STATE.REGENERATE_ENERGY
            return

        if self.hero.need_rest_in_move:
            ActionRestPrototype.create(hero=self.hero)
            self.state = self.STATE.RESTING
            return

        self.state = self.STATE.MOVING

    def move_speed(self):
        return self.hero.modify_move_speed(self.hero.move_speed)

    def process_moving(self):

        if self.hero.need_regenerate_energy and not self.hero.preferences.energy_regeneration_type.is_SACRIFICE:
            ActionRegenerateEnergyPrototype.create(hero=self.hero)
            self.state = self.STATE.REGENERATE_ENERGY
            return

        if self.hero.is_battle_start_needed():
            mob = mobs_storage.mobs.create_mob_for_hero(self.hero)
            ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)
            self.state = self.STATE.BATTLE
            return

        if random.uniform(0, 1) < c.HABIT_MOVE_EVENTS_IN_TURN:
            self.do_events()

        if (self.hero.companion and
            self.hero.can_companion_say_wisdom() and
            random.random() < c.COMPANIONS_EXP_PER_MOVE_PROBABILITY):

            self.hero.add_experience(c.COMPANIONS_EXP_PER_MOVE_GET_EXP, without_modifications=True)
            self.hero.add_message('companions_say_wisdom',
                                  companion_owner=self.hero,
                                  companion=self.hero.companion,
                                  experience=c.COMPANIONS_EXP_PER_MOVE_GET_EXP)

        if random.uniform(0, 1) < 0.33:
            self.journal_message()

        if self.hero.companion and random.random() < self.hero.companion_fly_probability:
            if self.fly_with_companion():
                return

        if self.hero.can_picked_up_in_road():
            if self.picked_up_in_road():
                return

        move_speed = self.move_speed()

        if self.path.length <= 1:
            self.percents = 1
        else:
            self.percents += move_speed / self.path.length

        self.after_move(create_inplace_action=True)

    def normalize_position_to_end(self, delta):
        destination_coordinates = self.path.destination_coordinates()

        if ((self.hero.position.cell_x, self.hero.position.cell_y) == destination_coordinates and # ???
            self.hero.position.is_near_cell_center(delta=delta)):
            self.hero.position.set_position(*destination_coordinates)

            self.percents = 1
            self.state = self.STATE.PROCESSED

    def after_move(self, create_inplace_action):

        move_speed = self.move_speed()

        stop_percents = self.stop_percents()

        if self.percents >= stop_percents:
            self.percents = stop_percents

        self.hero.position.set_position(*self.path.coordinates(self.percents))

        if self.break_at is not None and self.break_at <= self.percents:
            self.state = self.STATE.PROCESSED
            return

        self.normalize_position_to_end(delta=move_speed)

        if self.hero.position.should_visit_current_place(delta=move_speed):
            self.place_hero_in_current_place(create_action=create_inplace_action)

    def try_to_teleport_with_companion(self):
        if (self.hero.companion and
            random.random() < self.hero.companion_teleport_probability):

            if self.teleport_with_companion():
                return True

        return False

    def try_to_teleport_with_clan(self):

        start_place_id = self.hero.position.place_id

        if self.hero.clan_id not in self.hero.position.place.attrs.fast_transportation:
            return False

        if not self.teleport_with_clan():
            return False

        emissaries_logic.withdraw_event_points(clan_id=self.hero.clan_id,
                                               place_id=start_place_id,
                                               currency=emissaries_relations.EVENT_CURRENCY.FAST_TRANSPORTATION)
        return True

    def process(self):
        if self.preprocess():
            return

        if self.state in (self.STATE.RESTING,
                          self.STATE.RESURRECT,
                          self.STATE.REGENERATE_ENERGY,
                          self.STATE.HEALING_COMPANION):
            self.state = self.STATE.MOVING

        if self.state == self.STATE.IN_CITY:
            if self.try_to_teleport_with_companion():
                return

            self.state = self.STATE.MOVING

        if self.state == self.STATE.BATTLE:
            self.process_battle()

        if self.state == self.STATE.MOVING:
            self.process_moving()


ACTION_TYPES = {action_class.TYPE: action_class
                for action_class in utils_discovering.discover_classes(list(globals().values()), ActionBase)}
