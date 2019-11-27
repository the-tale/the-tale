
import smart_imports

smart_imports.all()


class EmissariesTestsMixin(object):

    def create_emissary(self, clan, initiator, place_id, uid=None):
        if uid is None:
            uid = uuid.uuid4().hex

        return logic.create_emissary(initiator=initiator,
                                     clan=clan,
                                     place_id=place_id,
                                     gender=random.choice((game_relations.GENDER.FEMALE,
                                                           game_relations.GENDER.MALE)),
                                     race=random.choice(game_relations.RACE.records),
                                     utg_name=game_names.generator().get_test_name('emissary-{}'.format(uid)))

    def enable_emissary_pvp(self, emissary):
        upper = tt_emissaries_constants.ATTRIBUTES_FOR_PARTICIPATE_IN_PVP // len(relations.ABILITY.records) + 1

        for ability in relations.ABILITY.records:
            emissary.abilities[ability] = upper

        logic.save_emissary(emissary)

        self.assertTrue(emissary.can_participate_in_pvp())

    def disable_emissary_pvp(self, emissary):
        for ability in relations.ABILITY.records:
            emissary.abilities[ability] = 0

        logic.save_emissary(emissary)

        self.assertFalse(emissary.can_participate_in_pvp())
