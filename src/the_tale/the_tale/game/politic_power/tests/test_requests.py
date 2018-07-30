

import smart_imports

smart_imports.all()


class HistoryTests(utils_testcase.TestCase):

    def setUp(self):
        super(HistoryTests, self).setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.person_1 = self.place_1.persons[0]
        self.person_2 = self.place_2.persons[0]

        self.account_1_id = self.accounts_factory.create_account().id
        self.account_2_id = self.accounts_factory.create_account().id

        game_tt_services.debug_clear_service()

    def url(self, power_type=views.POWER_TYPE_FILTER.ALL.value, account_id=None, place_id=None, person_id=None):

        arguments = {}

        if power_type is not None:
            arguments['power_type'] = power_type

        if account_id is not None:
            arguments['account'] = account_id

        if place_id is not None:
            arguments['place'] = place_id

        if person_id is not None:
            arguments['person'] = person_id

        return dext_urls.url('game:politic-power:history', **arguments)

    def test_wrong_account(self):
        self.check_html_ok(self.request_html(self.url(account_id='saasda')), texts=[('pgf-error-account.wrong_format', 1)])

    def test_wrong_power_type(self):
        self.check_html_ok(self.request_html(self.url(power_type='adasd')), texts=[('pgf-error-power_type.wrong_format', 1)])

    def test_wrong_place(self):
        self.check_html_ok(self.request_html(self.url(place_id='saasda')), texts=[('pgf-error-place.wrong_format', 1)])

    def test_wrong_person(self):
        self.check_html_ok(self.request_html(self.url(person_id='saasda')), texts=[('pgf-error-person.wrong_format', 1)])

    def test_no_records_found(self):
        self.check_html_ok(self.request_html(self.url()), texts=[('pgf-no-impacts', 1)])

    def test_places_and_person_error_message(self):
        self.check_html_ok(self.request_html(self.url(place_id=self.place_1.id, person_id=self.place_1.persons[0].id)),
                           texts=[('pgf-cannot-filter-by-place-and-master', 1)])

    def prepair_filter_data(self):

        impacts = []

        for impact_type in (game_tt_services.IMPACT_TYPE.INNER_CIRCLE, game_tt_services.IMPACT_TYPE.OUTER_CIRCLE):
            for account_id in (self.account_1_id, self.account_2_id):

                for person_id in (self.person_1.id, self.person_2.id):
                    impacts.append(game_tt_services.PowerImpact.hero_2_person(type=impact_type,
                                                                              hero_id=account_id,
                                                                              person_id=person_id,
                                                                              amount=random.randint(1000000, 10000000)))
                    impacts.append(game_tt_services.PowerImpact(type=impact_type,
                                                                actor_type=tt_api_impacts.OBJECT_TYPE.ACCOUNT,
                                                                actor_id=account_id,
                                                                target_type=tt_api_impacts.OBJECT_TYPE.PERSON,
                                                                target_id=person_id,
                                                                amount=random.randint(1000000, 10000000),
                                                                turn=None,
                                                                transaction=None))

                for place_id in (self.place_1.id, self.place_2.id):
                    impacts.append(game_tt_services.PowerImpact.hero_2_place(type=impact_type,
                                                                             hero_id=account_id,
                                                                             place_id=place_id,
                                                                             amount=random.randint(1000000, 10000000)))
                    impacts.append(game_tt_services.PowerImpact(type=impact_type,
                                                                actor_type=tt_api_impacts.OBJECT_TYPE.ACCOUNT,
                                                                actor_id=account_id,
                                                                target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                                target_id=place_id,
                                                                amount=random.randint(1000000, 10000000),
                                                                turn=None,
                                                                transaction=None))

        for impact in impacts:
            logic.add_power_impacts([impact])

        return impacts

    def test_filter_by_power_type(self):
        impacts = self.prepair_filter_data()

        self.check_html_ok(self.request_html(self.url(power_type=views.POWER_TYPE_FILTER.ALL.value)),
                           texts=[impact.amount for impact in impacts])

        self.check_html_ok(self.request_html(self.url(power_type=views.POWER_TYPE_FILTER.PERSONAL.value)),
                           texts=[impact.amount if impact.type.is_INNER_CIRCLE else (impact.amount, 0)
                                  for impact in impacts if impact.type.is_INNER_CIRCLE])

        self.check_html_ok(self.request_html(self.url(power_type=views.POWER_TYPE_FILTER.CROWD.value)),
                           texts=[impact.amount if impact.type.is_OUTER_CIRCLE else (impact.amount, 0)
                                  for impact in impacts])

    def test_filter_by_account_or_hero(self):
        impacts = self.prepair_filter_data()

        self.check_html_ok(self.request_html(self.url(account_id=self.account_1_id)),
                           texts=[impact.amount if impact.actor_id == self.account_1_id else (impact.amount, 0)
                                  for impact in impacts])

    def test_filter_by_place(self):
        impacts = self.prepair_filter_data()

        self.check_html_ok(self.request_html(self.url(place_id=self.place_1.id)),
                           texts=[impact.amount if impact.target_id == self.place_1.id and impact.target_type.is_PLACE else (impact.amount, 0)
                                  for impact in impacts])

    def test_filter_by_person(self):
        impacts = self.prepair_filter_data()

        self.check_html_ok(self.request_html(self.url(person_id=self.person_1.id)),
                           texts=[impact.amount if impact.target_id == self.person_1.id and impact.target_type.is_PERSON else (impact.amount, 0)
                                  for impact in impacts])

    def test_limit(self):
        N = 10

        for i in range(conf.settings.MAX_HISTORY_LENGTH + N):
            logic.add_power_impacts([game_tt_services.PowerImpact.hero_2_place(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                               hero_id=self.account_1_id,
                                                                               place_id=self.place_1.id,
                                                                               amount=1000000 + i)])

        texts = ['{}'.format(1000000 + i) for i in range(N, conf.settings.MAX_HISTORY_LENGTH + N)]
        texts.extend(('{}'.format(1000000 + i), 0) for i in range(N))

        self.check_html_ok(self.request_html(self.url()), texts=texts)
