
import smart_imports

smart_imports.all()


class MobsStorageTests(utils_testcase.TestCase):

    def setUp(self):
        super(MobsStorageTests, self).setUp()
        game_logic.create_test_map()

        self.mobs = list(storage.mobs.all())
        self.mobs_candidates = [(mob, 1) for mob in self.mobs]

        self.assertEqual(len(self.mobs), 3)

    def test_restrict_level(self):
        self.mobs[0].level = 3
        self.mobs[1].level = 2
        self.mobs[2].level = 1

        mobs = list(filters.restrict_level(self.mobs_candidates, 2))

        self.assertEqual({(self.mobs[1].id, 1), (self.mobs[2].id, 1)},
                         {(mob.id, priority) for mob, priority in mobs})

    def test_restrict_terrain(self):
        self.mobs[0].terrains = {map_relations.TERRAIN.PLANE_SAND, map_relations.TERRAIN.HILLS_MUD}
        self.mobs[1].terrains = {map_relations.TERRAIN.PLANE_SAND}
        self.mobs[2].terrains = {map_relations.TERRAIN.HILLS_MUD}

        mobs = list(filters.restrict_terrain(self.mobs_candidates, map_relations.TERRAIN.HILLS_MUD))

        self.assertEqual({(self.mobs[0].id, 1), (self.mobs[2].id, 1)},
                         {(mob.id, priority) for mob, priority in mobs})

    def test_restrict_mercenary(self):
        self.mobs[0].is_mercenary = False
        self.mobs[1].is_mercenary = True
        self.mobs[2].is_mercenary = False

        mobs = list(filters.restrict_mercenary(self.mobs_candidates, False))

        self.assertEqual({(self.mobs[0].id, 1), (self.mobs[2].id, 1)},
                         {(mob.id, priority) for mob, priority in mobs})

        mobs = list(filters.restrict_mercenary(self.mobs_candidates, True))

        self.assertEqual({(self.mobs[1].id, 1)},
                         {(mob.id, priority) for mob, priority in mobs})

    def test_change_type_priority(self):
        self.mobs[0].type = tt_beings_relations.TYPE.UNDEAD
        self.mobs[1].type = tt_beings_relations.TYPE.MECHANICAL
        self.mobs[2].type = tt_beings_relations.TYPE.DEMON

        mobs = list(filters.change_type_priority(self.mobs_candidates,
                                                 types=(tt_beings_relations.TYPE.UNDEAD, tt_beings_relations.TYPE.DEMON),
                                                 delta=10))

        self.assertEqual({(self.mobs[0].id, 11), (self.mobs[1].id, 1), (self.mobs[2].id, 11)},
                         {(mob.id, priority) for mob, priority in mobs})
