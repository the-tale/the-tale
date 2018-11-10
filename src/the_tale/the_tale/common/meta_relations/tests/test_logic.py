
import smart_imports

smart_imports.all()


class LogicTests(utils_testcase.TestCase):

    def setUp(self):
        pass

    def test_create_uid(self):
        self.assertEqual(logic.create_uid(666, 777), '666#777')

    def test_create_tag(self):
        self.assertEqual(logic.create_tag(666, 777), (666 << 32) + 777)

    def test_get_object(self):
        self.assertEqual(logic.get_object(-1, 33), meta_relations.TestType_1(33))
        self.assertEqual(logic.get_object(-2, 34), meta_relations.TestType_2(34))

    def test_get_object__wrong_type(self):
        self.assertRaises(exceptions.WrongTypeError, logic.get_object, -666, 33)

    def test_get_object__no_object(self):
        self.assertRaises(exceptions.WrongObjectError, logic.get_object, -2, -33)

    def test_get_object_by_uid(self):
        self.assertEqual(logic.get_object_by_uid('-1#33'), meta_relations.TestType_1(33))
        self.assertEqual(logic.get_object_by_uid('-2#34'), meta_relations.TestType_2(34))

    def test_get_object_by_uid__wrong_format(self):
        self.assertRaises(exceptions.WrongUIDFormatError, logic.get_object_by_uid, 'ds1#33')
        self.assertRaises(exceptions.WrongUIDFormatError, logic.get_object_by_uid, '133')
        self.assertRaises(exceptions.WrongUIDFormatError, logic.get_object_by_uid, '1#')
        self.assertRaises(exceptions.WrongUIDFormatError, logic.get_object_by_uid, '#')
        self.assertRaises(exceptions.WrongUIDFormatError, logic.get_object_by_uid, '')

    def test_get_object_by_tag(self):
        self.assertEqual(logic.get_object_by_tag(logic.create_tag(-1, 33)), meta_relations.TestType_1(33))
        self.assertEqual(logic.get_object_by_tag(logic.create_tag(-2, 34)), meta_relations.TestType_2(34))

    def test_get_object_by_tag__wrong_format(self):
        self.assertRaises(exceptions.WrongTagFormatError, logic.get_object_by_tag, 'ds1#33')
        self.assertRaises(exceptions.WrongTagFormatError, logic.get_object_by_tag, '133')
        self.assertRaises(exceptions.WrongTagFormatError, logic.get_object_by_tag, 23.3)

    def test_create_relation(self):
        with self.check_delta(models.Relation.objects.count, 3):
            logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_1(6), meta_relations.TestType_2(7))
            logic.create_relation(meta_relations.TestRelation_2, meta_relations.TestType_1(5), meta_relations.TestType_2(4))
            logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_2(8), meta_relations.TestType_1(1))

        self.assertTrue(models.Relation.objects.filter(relation=meta_relations.TestRelation_1.TYPE,
                                                       from_type=meta_relations.TestType_1.TYPE,
                                                       from_object=6,
                                                       to_type=meta_relations.TestType_2.TYPE,
                                                       to_object=7).exists())
        self.assertTrue(models.Relation.objects.filter(relation=meta_relations.TestRelation_1.TYPE,
                                                       from_type=meta_relations.TestType_2.TYPE,
                                                       from_object=8,
                                                       to_type=meta_relations.TestType_1.TYPE,
                                                       to_object=1).exists())
        self.assertTrue(models.Relation.objects.filter(relation=meta_relations.TestRelation_2.TYPE,
                                                       from_type=meta_relations.TestType_1.TYPE,
                                                       from_object=5,
                                                       to_type=meta_relations.TestType_2.TYPE,
                                                       to_object=4).exists())

    def test_remove_relation(self):
        with self.check_delta(models.Relation.objects.count, 2):
            removed_relation = logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_1(6), meta_relations.TestType_2(7))
            logic.create_relation(meta_relations.TestRelation_2, meta_relations.TestType_1(5), meta_relations.TestType_2(4))
            logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_2(8), meta_relations.TestType_1(1))

            logic.remove_relation(removed_relation.id)

        self.assertTrue(models.Relation.objects.filter(relation=meta_relations.TestRelation_1.TYPE,
                                                       from_type=meta_relations.TestType_2.TYPE,
                                                       from_object=8,
                                                       to_type=meta_relations.TestType_1.TYPE,
                                                       to_object=1).exists())
        self.assertTrue(models.Relation.objects.filter(relation=meta_relations.TestRelation_2.TYPE,
                                                       from_type=meta_relations.TestType_1.TYPE,
                                                       from_object=5,
                                                       to_type=meta_relations.TestType_2.TYPE,
                                                       to_object=4).exists())

    def test_create_relations_for_objects(self):
        with self.check_delta(models.Relation.objects.count, 3):
            logic.create_relations_for_objects(meta_relations.TestRelation_2, meta_relations.TestType_2(666),
                                               [meta_relations.TestType_1(7), meta_relations.TestType_2(8), meta_relations.TestType_1(11)])

        self.assertTrue(models.Relation.objects.filter(relation=meta_relations.TestRelation_2.TYPE,
                                                       from_type=meta_relations.TestType_2.TYPE,
                                                       from_object=666,
                                                       to_type=meta_relations.TestType_1.TYPE,
                                                       to_object=7).exists())
        self.assertTrue(models.Relation.objects.filter(relation=meta_relations.TestRelation_2.TYPE,
                                                       from_type=meta_relations.TestType_2.TYPE,
                                                       from_object=666,
                                                       to_type=meta_relations.TestType_2.TYPE,
                                                       to_object=8).exists())
        self.assertTrue(models.Relation.objects.filter(relation=meta_relations.TestRelation_2.TYPE,
                                                       from_type=meta_relations.TestType_2.TYPE,
                                                       from_object=666,
                                                       to_type=meta_relations.TestType_1.TYPE,
                                                       to_object=11).exists())

    def test_remove_relations_from_object(self):
        logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_1(6), meta_relations.TestType_2(7))
        logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_2(8), meta_relations.TestType_1(1))
        logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_1(6), meta_relations.TestType_2(4))

        with self.check_delta(models.Relation.objects.count, -2):
            logic.remove_relations_from_object(meta_relations.TestRelation_1, meta_relations.TestType_1(6))

        self.assertTrue(models.Relation.objects.filter(relation=meta_relations.TestRelation_1.TYPE,
                                                       from_type=meta_relations.TestType_2.TYPE,
                                                       from_object=8,
                                                       to_type=meta_relations.TestType_1.TYPE,
                                                       to_object=1).exists())

    def test_get_objects_related_from(self):
        logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_1(6), meta_relations.TestType_2(7))
        logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_2(8), meta_relations.TestType_1(1))
        logic.create_relation(meta_relations.TestRelation_2, meta_relations.TestType_1(6), meta_relations.TestType_1(4))

        self.assertEqual(set((relation.id, obj.id) for relation, obj in logic.get_objects_related_from(meta_relations.TestType_1(6))),
                         set(((meta_relations.TestRelation_1.id, 7), (meta_relations.TestRelation_2.id, 4))))

        self.assertEqual(set((relation.id, obj.id) for relation, obj in logic.get_objects_related_from(meta_relations.TestType_1(6), relation=meta_relations.TestRelation_2)),
                         set(((meta_relations.TestRelation_2.id, 4),)))

    def test_get_uids_related_from(self):
        logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_1(6), meta_relations.TestType_2(7))
        logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_2(8), meta_relations.TestType_1(1))
        logic.create_relation(meta_relations.TestRelation_2, meta_relations.TestType_1(6), meta_relations.TestType_1(4))

        self.assertEqual(set(logic.get_uids_related_from(meta_relations.TestType_1(6))),
                         set(('-2#7', '-1#4')))

        self.assertEqual(set(logic.get_uids_related_from(meta_relations.TestType_1(6), relation=meta_relations.TestRelation_2)),
                         set(('-1#4',)))

    def test_get_objects_related_to(self):
        logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_2(7), meta_relations.TestType_1(6))
        logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_1(1), meta_relations.TestType_2(8))
        logic.create_relation(meta_relations.TestRelation_2, meta_relations.TestType_1(4), meta_relations.TestType_1(6))

        self.assertEqual(set((relation.id, obj.id) for relation, obj in logic.get_objects_related_to(meta_relations.TestType_1(6))),
                         set(((meta_relations.TestRelation_1.id, 7), (meta_relations.TestRelation_2.id, 4))))

        self.assertEqual(set((relation.id, obj.id) for relation, obj in logic.get_objects_related_to(meta_relations.TestType_1(6), relation=meta_relations.TestRelation_2)),
                         set(((meta_relations.TestRelation_2.id, 4),)))

    def test_get_uids_related_to(self):
        logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_2(7), meta_relations.TestType_1(6))
        logic.create_relation(meta_relations.TestRelation_1, meta_relations.TestType_1(1), meta_relations.TestType_2(8))
        logic.create_relation(meta_relations.TestRelation_2, meta_relations.TestType_1(4), meta_relations.TestType_1(6))

        self.assertEqual(set(logic.get_uids_related_to(meta_relations.TestType_1(6))),
                         set(('-2#7', '-1#4')))

        self.assertEqual(set(logic.get_uids_related_to(meta_relations.TestType_1(6), relation=meta_relations.TestRelation_2)),
                         set(('-1#4',)))
