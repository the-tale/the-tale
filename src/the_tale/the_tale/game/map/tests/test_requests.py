
import smart_imports

smart_imports.all()


class RequestsTestsBase(utils_testcase.TestCase):
    def setUp(self):
        super(RequestsTestsBase, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.request_login(self.account.email)


class IndexTests(RequestsTestsBase):

    def test_success(self):
        self.check_html_ok(self.request_html(django_reverse('game:map:')))


class CellInfoTests(RequestsTestsBase):

    def test_place_info_logined(self):
        self.check_html_ok(self.request_html(django_reverse('game:map:cell-info') + '?x=2&y=3'), texts=[])

    def test_place_info_no_modifier(self):
        texts = [('pgf-current-modifier-marker', 0)]
        self.check_html_ok(self.request_html(django_reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    @mock.patch('the_tale.game.persons.objects.Person.on_move_timeout', False)
    def test_place_info_no_freeze_time_icon(self):
        texts = [('pgf-time-before-unfreeze', 0)]
        self.check_html_ok(self.request_html(django_reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    @mock.patch('the_tale.game.persons.objects.Person.on_move_timeout', True)
    def test_place_info_freeze_time_icon(self):
        texts = ['pgf-time-before-unfreeze']
        self.check_html_ok(self.request_html(django_reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    def test_place_new_place_message(self):
        self.assertTrue(self.place_1.is_new)
        self.check_html_ok(self.request_html(django_reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=['pgf-new-place-message'])

    def test_place_new_place_message__not_new(self):
        places_models.Place.objects.filter(id=self.place_1.id).update(created_at=datetime.datetime(2000, 1, 1))
        places_storage.places.refresh()

        self.check_html_ok(self.request_html(django_reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=[('pgf-new-place-message', 0)])

    @mock.patch('the_tale.game.places.objects.Place.is_frontier', True)
    def test_place_frontier_message(self):
        self.check_html_ok(self.request_html(django_reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=['pgf-frontier-message'])

    @mock.patch('the_tale.game.places.objects.Place.is_frontier', False)
    def test_place_frontier_message__not_new(self):
        self.check_html_ok(self.request_html(django_reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=[('pgf-frontier-message', 0)])

    def test_place_chronicle(self):
        texts = [jinja2.escape(record.text) for record in chronicle_prototypes.RecordPrototype.get_last_actor_records(self.place_1, 1000)]
        self.check_html_ok(self.request_html(django_reverse('game:map:cell-info') + ('?x=%d&y=%d' % (self.place_1.x, self.place_1.y))), texts=texts)

    def test_building(self):
        building = places_logic.create_building(self.place_1.persons[0], utg_name=game_names.generator().get_test_name('building-name'))
        texts = [building.type.text, jinja2.escape(building.person.name), jinja2.escape(self.place_1.name)]
        self.check_html_ok(self.request_html(django_reverse('game:map:cell-info') + ('?x=%d&y=%d' % (building.x, building.y))), texts=texts)

    def test_outside_map(self):
        self.check_html_ok(self.request_html(dext_urls.url('game:map:cell-info', x=0, y=0)), texts=[('outside_map', 0)])
        self.check_html_ok(self.request_html(dext_urls.url('game:map:cell-info', x=conf.settings.WIDTH - 1, y=conf.settings.HEIGHT - 1)), texts=[('outside_map', 0)])

        self.check_html_ok(self.request_html(dext_urls.url('game:map:cell-info', x=-1, y=0)), texts=[('outside_map', 1)])
        self.check_html_ok(self.request_html(dext_urls.url('game:map:cell-info', x=0, y=-1)), texts=[('outside_map', 1)])
        self.check_html_ok(self.request_html(dext_urls.url('game:map:cell-info', x=conf.settings.WIDTH, y=conf.settings.HEIGHT - 1)), texts=[('outside_map', 1)])
        self.check_html_ok(self.request_html(dext_urls.url('game:map:cell-info', x=conf.settings.WIDTH - 1, y=conf.settings.HEIGHT)), texts=[('outside_map', 1)])


class RegionTests(RequestsTestsBase):

    def setUp(self):
        super(RegionTests, self).setUp()
        generator.update_map(index=0)

    def test_last(self):
        self.check_ajax_ok(self.request_ajax_json(logic.region_url()))

    def test_no_region_for_turn(self):
        self.check_ajax_error(self.request_ajax_json(logic.region_url(666)), 'no_region_found')

    def test_region_for_turn(self):
        game_turn.increment()

        self.check_ajax_error(self.request_ajax_json(logic.region_url(game_turn.number())), 'no_region_found')

        generator.update_map(index=1)

        self.check_ajax_ok(self.request_ajax_json(logic.region_url(game_turn.number())))


class RegionVersionsTests(RequestsTestsBase):

    def setUp(self):
        super(RegionVersionsTests, self).setUp()
        generator.update_map(index=0)

    def test_region_for_turn(self):

        current_turn = game_turn.number()

        self.check_ajax_ok(self.request_ajax_json(logic.region_versions_url()), {'turns': [current_turn]})

        game_turn.increment()

        self.check_ajax_ok(self.request_ajax_json(logic.region_versions_url()), {'turns': [current_turn]})

        generator.update_map(index=1)

        self.check_ajax_ok(self.request_ajax_json(logic.region_versions_url()), {'turns': [current_turn, current_turn + 1]})
