
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
