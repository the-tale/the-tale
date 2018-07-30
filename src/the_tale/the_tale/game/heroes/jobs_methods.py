
import smart_imports

smart_imports.all()


class JobsMethodsMixin(object):
    __slots__ = ()

    def get_job_variables(self, place_id, person_id):
        variables = {'place': places_storage.places[place_id]}
        if person_id is not None:
            variables['person'] = persons_storage.persons[person_id]
        return variables

    def job_message(self, place_id, person_id, message_type, job_power):
        self.add_message(message_type, diary=True, hero=self, **self.get_job_variables(place_id, person_id))

    def job_money(self, place_id, person_id, message_type, job_power):
        coins = max(1, int(math.ceil(f.normal_action_price(self.level) * job_power * c.NORMAL_JOB_LENGTH * c.JOB_HERO_REWARD_FRACTION)))
        self.change_money(relations.MONEY_SOURCE.EARNED_FROM_MASTERS, coins)

        self.add_message(message_type, diary=True, hero=self, coins=coins, **self.get_job_variables(place_id, person_id))

    def job_artifact(self, place_id, person_id, message_type, job_power):

        rarity = utils_logic.random_value_by_priority(((artifacts_relations.RARITY.RARE, c.RARE_ARTIFACT_PROBABILITY),
                                                       (artifacts_relations.RARITY.EPIC, c.EPIC_ARTIFACT_PROBABILITY * job_power)))

        artifact, unequipped, sell_price = self.receive_artifact(equip=False,
                                                                 better=True,
                                                                 prefered_slot=False,
                                                                 prefered_item=True,
                                                                 archetype=True,
                                                                 rarity_type=rarity)

        self.add_message(message_type, diary=True, hero=self, artifact=artifact, **self.get_job_variables(place_id, person_id))

    def job_experience(self, place_id, person_id, message_type, job_power):
        experience = max(1, int(math.ceil(f.experience_for_quest(c.QUEST_AREA_RADIUS) * job_power * c.NORMAL_JOB_LENGTH * c.JOB_HERO_REWARD_FRACTION)))
        self.add_experience(experience, without_modifications=True)

        self.add_message(message_type, diary=True, hero=self, experience=experience, **self.get_job_variables(place_id, person_id))

    def job_energy(self, place_id, person_id, message_type, job_power):
        energy = max(1, int(math.ceil(c.ANGEL_ENERGY_IN_DAY * job_power * c.NORMAL_JOB_LENGTH * c.JOB_HERO_REWARD_FRACTION)))

        game_tt_services.energy.cmd_change_balance(account_id=self.account_id,
                                                   type='job_energy',
                                                   energy=energy,
                                                   async=True,
                                                   autocommit=True)

        self.add_message(message_type, diary=True, hero=self, energy=energy, **self.get_job_variables(place_id, person_id))
