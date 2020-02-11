
import smart_imports

smart_imports.all()


class JobsMethodsMixin(object):
    __slots__ = ()

    def get_job_variables(self, place_id, person_id):
        variables = {'place': places_storage.places[place_id]}
        if person_id is not None:
            variables['person'] = persons_storage.persons[person_id]
        return variables

    def job_message(self, place_id, person_id, message_type, **kwargs):
        self.add_message(message_type, diary=True, hero=self, **self.get_job_variables(place_id, person_id))

    def job_money(self, place_id, person_id, message_type, effect_value):
        self.change_money(relations.MONEY_SOURCE.EARNED_FROM_MASTERS, effect_value)

        self.add_message(message_type, diary=True, hero=self, coins=effect_value, **self.get_job_variables(place_id, person_id))

    def job_artifact(self, place_id, person_id, message_type, effect_value):

        rarity_value = utils_logic.random_value_by_priority(list(effect_value.items()))

        rarity = artifacts_relations.RARITY(rarity_value)

        artifact, unequipped, sell_price = self.receive_artifact(equip=False,
                                                                 better=True,
                                                                 prefered_slot=False,
                                                                 prefered_item=True,
                                                                 archetype=True,
                                                                 rarity_type=rarity)

        self.add_message(message_type, diary=True, hero=self, artifact=artifact, **self.get_job_variables(place_id, person_id))

    def job_experience(self, place_id, person_id, message_type, effect_value):
        self.add_experience(effect_value, without_modifications=True)

        self.add_message(message_type, diary=True, hero=self, experience=effect_value, **self.get_job_variables(place_id, person_id))

    def job_cards(self, place_id, person_id, message_type, effect_value):

        account = accounts_prototypes.AccountPrototype.get_by_id(self.id)

        cards_logic.give_new_cards(account_id=account.id,
                                   operation_type='job-card',
                                   allow_premium_cards=account.cards_receive_mode().is_ALL,
                                   available_for_auction=account.is_premium,
                                   number=effect_value)

        self.add_message(message_type, diary=True, hero=self, **self.get_job_variables(place_id, person_id))
