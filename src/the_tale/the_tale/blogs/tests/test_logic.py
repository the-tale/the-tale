
import smart_imports

smart_imports.all()


class BaseTestRequests(utils_testcase.TestCase):

    def setUp(self):
        super(BaseTestRequests, self).setUp()

        game_logic.create_test_map()

        helpers.prepair_forum()

        self.account = self.accounts_factory.create_account()

    def create_post(self, uid):
        return prototypes.PostPrototype.create(self.account, 'test folclor {}'.format(uid), uuid.uuid4().hex)

    def create_tag(self, meta_type, default=False):
        return models.Tag.objects.create(name=uuid.uuid4().hex,
                                         description=uuid.uuid4().hex,
                                         meta_type=meta_type,
                                         default=default)


class GetTagsTests(BaseTestRequests):

    def test(self):
        # posts = [self.create_post() for i in range(3)]

        tags = [self.create_tag(meta_type=None),
                self.create_tag(meta_type=None),
                self.create_tag(meta_type=places_meta_relations.Place.TYPE),
                self.create_tag(meta_type=clans_meta_relations.Clan.TYPE)]

        self.assertEqual({tag.id for tag in logic.get_technical_tags()},
                         {tags[2].id, tags[3].id})

        self.assertEqual({tag.id for tag in logic.get_manual_tags()},
                         {tags[0].id, tags[1].id})


class GetPostTagsTests(BaseTestRequests):

    def test_no_tags(self):
        post = self.create_post(1)
        models.Tagged.objects.all().delete()

        self.assertEqual(logic.get_post_tags(post.id), [])

    def test_has_tags(self):
        post = self.create_post(1)

        tags = [self.create_tag(meta_type=None) for _ in range(3)]

        logic.create_tag_relation(post.id, tags[0].id)
        logic.create_tag_relation(post.id, tags[2].id)

        self.assertEqual({tag.id for tag in logic.get_post_tags(post.id)},
                         {tags[0].id, tags[2].id})


class RemoveTagRelationTests(BaseTestRequests):

    def test_not_relation(self):
        post = self.create_post(1)

        logic.remove_tag_relation(post.id, 666)

    def test_has_relations(self):
        posts = [self.create_post(i) for i in range(3)]

        tags = [self.create_tag(meta_type=None) for _ in range(3)]

        logic.create_tag_relation(posts[0].id, tags[0].id)
        logic.create_tag_relation(posts[0].id, tags[2].id)
        logic.create_tag_relation(posts[1].id, tags[2].id)

        logic.remove_tag_relation(posts[0].id, tags[2].id)

        self.assertEqual({tag.id for tag in logic.get_post_tags(posts[0].id)},
                         {tags[0].id})

        self.assertEqual({tag.id for tag in logic.get_post_tags(posts[1].id)},
                         {tags[2].id})


class SyncTagsTests(BaseTestRequests):

    def test(self):
        posts = [self.create_post(i) for i in range(2)]

        tags = [self.create_tag(meta_type=None) for _ in range(5)]

        logic.create_tag_relation(posts[0].id, tags[0].id)
        logic.create_tag_relation(posts[0].id, tags[1].id)

        logic.create_tag_relation(posts[1].id, tags[1].id)
        logic.create_tag_relation(posts[1].id, tags[2].id)
        logic.create_tag_relation(posts[1].id, tags[3].id)

        logic.sync_tags(posts[1].id,
                        expected_tags_ids={tags[2].id, tags[4].id},
                        work_tags_ids={tags[0].id, tags[2].id, tags[3].id, tags[4].id})

        self.assertEqual({tag.id for tag in logic.get_post_tags(posts[1].id)},
                         {tags[1].id,
                          tags[2].id,
                          tags[4].id})


class SyncTechnicalTags(BaseTestRequests):

    def test(self):
        post = self.create_post(1)

        tags = [self.create_tag(meta_type=None),
                self.create_tag(meta_type=places_meta_relations.Place.TYPE),
                self.create_tag(meta_type=artifacts_meta_relations.Artifact.TYPE),
                self.create_tag(meta_type=persons_meta_relations.Person.TYPE)]

        place = places_storage.places.all()[0].meta_object()
        person = persons_storage.persons.all()[0].meta_object()
        artifact = artifacts_storage.artifacts.all()[0].meta_object()

        meta_relations_logic.create_relations_for_objects(meta_relations.IsAbout,
                                                          meta_relations.Post.create_from_object(post),
                                                          [place, person])

        logic.sync_technical_tags(post.id)

        self.assertEqual({tag.id for tag in logic.get_post_tags(post.id)},
                         {tags[1].id, tags[3].id})

        logic.create_tag_relation(post.id, tags[0].id)

        meta_relations_logic.remove_relations_from_object(meta_relations.IsAbout,
                                                          meta_relations.Post.create_from_object(post))

        meta_relations_logic.create_relations_for_objects(meta_relations.IsAbout,
                                                          meta_relations.Post.create_from_object(post),
                                                          [place, artifact])

        logic.sync_technical_tags(post.id)

        self.assertEqual({tag.id for tag in logic.get_post_tags(post.id)},
                         {tags[0].id, tags[1].id, tags[2].id})
