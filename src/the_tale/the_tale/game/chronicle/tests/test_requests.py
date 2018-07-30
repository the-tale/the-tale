
import smart_imports

smart_imports.all()


class IndexRequestsTest(utils_testcase.TestCase):

    def setUp(self):
        super(IndexRequestsTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        models.Record.objects.all().delete()

    def create_record(self, index, turn_number=0, type_=relations.RECORD_TYPE.PLACE_CHANGE_RACE, actors={}):
        helpers.FakeRecord(type_=type_, index=index, turn_number=turn_number, actors=actors).create_record()

    def test_no_records(self):
        self.check_html_ok(self.client.get(django_reverse('game:chronicle:')), texts=['pgf-no-records-message'])

    def test_success(self):
        self.create_record(0)
        self.check_html_ok(self.client.get(django_reverse('game:chronicle:')), texts=['record_text_0_0'])

    def test_full_page(self):
        texts = []
        for i in range(conf.settings.RECORDS_ON_PAGE):
            self.create_record(i)
            texts.append('record_text_%d_%d' % (0, i))

        self.check_html_ok(self.client.get(django_reverse('game:chronicle:')), texts=texts)
        self.check_redirect(django_reverse('game:chronicle:') + '?page=2', django_reverse('game:chronicle:') + '?page=1')

    def test_second_page(self):
        for i in range(conf.settings.RECORDS_ON_PAGE + 1):
            self.create_record(i)

        texts = ['record_text_%d_%d' % (0, conf.settings.RECORDS_ON_PAGE)]

        self.check_html_ok(self.client.get(django_reverse('game:chronicle:') + '?page=2'), texts=texts)

    def test_filter_by_place_no_records(self):
        self.create_record(0, actors=[(relations.ACTOR_ROLE.PLACE, prototypes.ExternalPlace(self.place_1))])
        self.create_record(1, actors=[(relations.ACTOR_ROLE.PLACE, prototypes.ExternalPlace(self.place_1))])
        self.check_html_ok(self.client.get(django_reverse('game:chronicle:') + ('?place=%d' % self.place_2.id)), texts=['pgf-no-records-message'])

    def test_filter_by_place(self):
        self.create_record(0, actors=[(relations.ACTOR_ROLE.PLACE, prototypes.ExternalPlace(self.place_1))])
        self.create_record(1, actors=[(relations.ACTOR_ROLE.PLACE, prototypes.ExternalPlace(self.place_1))])
        self.create_record(2, actors=[(relations.ACTOR_ROLE.PLACE, prototypes.ExternalPlace(self.place_2))])
        self.check_html_ok(self.client.get(django_reverse('game:chronicle:') + ('?place=%d' % self.place_1.id)), texts=[('pgf-no-records-message', 0),
                                                                                                                        ('record_text_0_0', 1),
                                                                                                                        ('record_text_0_1', 1),
                                                                                                                        ('record_text_0_2', 0)])
