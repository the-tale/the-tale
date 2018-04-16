
import time
import datetime

from unittest import mock

from django.test import client
from django.core.urlresolvers import reverse

from dext.common.utils import s11n

from tt_logic.beings import relations as beings_relations

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.logic import login_page_url

from the_tale.game import logic

from the_tale.game import relations

from the_tale.game.pvp.models import BATTLE_1X1_STATE
from the_tale.game.pvp.tests.helpers import PvPTestsMixin

from the_tale.news import logic as news_logic

from the_tale.game.heroes import tt_api as heroes_tt_api
from the_tale.game.heroes import messages as heroes_messages

from the_tale.game import turn


class RequestTestsBase(TestCase, PvPTestsMixin):

    def setUp(self):
        super(RequestTestsBase, self).setUp()
        logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.client = client.Client()

        self.game_info_url_1 = logic.game_info_url(account_id=self.account_1.id)
        self.game_info_url_2 = logic.game_info_url(account_id=self.account_2.id)
        self.game_info_url_no_id = logic.game_info_url()

        self.request_login(self.account_1.email)


class GamePageRequestTests(RequestTestsBase):

    def test_game_page_unlogined(self):
        self.request_logout()
        self.check_redirect(reverse('game:'), login_page_url(reverse('game:')))

    def test_game_page_logined(self):
        response = self.client.get(reverse('game:'))
        self.assertEqual(response.status_code, 200)

    def test_game_page_when_pvp_in_queue(self):
        self.pvp_create_battle(self.account_1, self.account_2)
        self.pvp_create_battle(self.account_2, self.account_1)
        self.check_html_ok(self.client.get(reverse('game:')))

    def test_game_page_when_pvp_processing(self):
        self.pvp_create_battle(self.account_1, self.account_2, BATTLE_1X1_STATE.PROCESSING)
        self.pvp_create_battle(self.account_2, self.account_1, BATTLE_1X1_STATE.PROCESSING)
        self.check_redirect(reverse('game:'), reverse('game:pvp:'))


class InfoRequestTests(RequestTestsBase):

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_ok(self.request_ajax_json(self.game_info_url_1))

    def test_logined(self):
        response = self.client.get(self.game_info_url_1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(s11n.from_json(response.content.decode('utf-8'))['data'].keys()), set(('turn', 'mode', 'map_version', 'account', 'enemy', 'game_state')))

    def test_no_id__logined(self):
        with mock.patch('the_tale.game.logic.form_game_info', mock.Mock(return_value={})) as form_game_info:
            self.check_ajax_ok(self.client.get(self.game_info_url_no_id))

        self.assertEqual(form_game_info.call_count, 1)
        self.assertEqual(form_game_info.call_args_list[0][1]['account'].id, self.account_1.id)

    def test_no_id__unlogined(self):
        self.request_logout()

        with mock.patch('the_tale.game.logic.form_game_info', mock.Mock(return_value={})) as form_game_info:
            self.check_ajax_ok(self.client.get(self.game_info_url_no_id))

        self.assertEqual(form_game_info.call_count, 1)
        self.assertEqual(form_game_info.call_args_list[0][1]['account'], None)

    def test_account_not_exists(self):
        response = self.request_ajax_json(logic.game_info_url(account_id=666))
        self.check_ajax_error(response, 'account.wrong_value')

    def test_wrong_account_id(self):
        response = self.request_ajax_json(logic.game_info_url(account_id='sdsd'))
        self.check_ajax_error(response, 'account.wrong_format')

    def test_client_turns(self):
        self.check_ajax_error(self.request_ajax_json(logic.game_info_url(client_turns=['dds'])), 'client_turns.wrong_format')
        self.check_ajax_error(self.request_ajax_json(logic.game_info_url(client_turns=['1', ''])), 'client_turns.wrong_format')
        self.check_ajax_ok(self.request_ajax_json(logic.game_info_url(client_turns=['1'])))
        self.check_ajax_ok(self.request_ajax_json(logic.game_info_url(client_turns=['1, 2, 3 ,4'])))
        self.check_ajax_ok(self.request_ajax_json(logic.game_info_url(client_turns=[1, 2, 3 ,4])))
        self.check_ajax_ok(self.request_ajax_json(logic.game_info_url(client_turns=['1',' 2',' 3 ','4'])))

    def test_client_turns_passed_to_data_receiver(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.cached_ui_info_for_hero',
                        mock.Mock(return_value={'actual_on_turn': 666})) as cached_ui_info_for_hero:
            self.check_ajax_ok(self.request_ajax_json(logic.game_info_url(client_turns=[1, 2, 3 ,4])))

        self.assertEqual(cached_ui_info_for_hero.call_args_list,
                         [mock.call(account_id=self.account_1.id,
                                    recache_if_required=True,
                                    patch_turns=[1, 2, 3, 4],
                                    for_last_turn=False)])


class NewsAlertsTests(TestCase):

    def setUp(self):
        super(NewsAlertsTests, self).setUp()
        logic.create_test_map()
        self.client = client.Client()

        self.news = news_logic.create_news(caption='news-caption', description='news-description', content='news-content')

        self.account = self.accounts_factory.create_account()

        self.request_login(self.account.email)

    def check_reminder(self, url, caption, description, block):
        self.check_html_ok(self.client.get(url), texts=[('news-caption', caption),
                                                        ('news-description', description),
                                                        ('news-content', 0),
                                                        ('pgf-last-news-reminder', block)])

    def test_news_alert_for_new_account(self):
        self.check_reminder(reverse('game:'), 0, 0, 0)

    def test_news_alert(self):
        self.account.last_news_remind_time -= datetime.timedelta(seconds=666)
        self.account.save()

        self.check_reminder(reverse('game:'), 1, 1, 2)

    def test_no_news_alert(self):
        self.account.last_news_remind_time = datetime.datetime.now()
        self.account.save()
        self.check_reminder(reverse('game:'), 0, 0, 0)


class DiaryRequestTests(RequestTestsBase):

    def setUp(self):
        super(DiaryRequestTests, self).setUp()

        heroes_tt_api.push_message_to_diary(account_id=self.account_1.id, message=self.create_message(1), is_premium=False)
        heroes_tt_api.push_message_to_diary(account_id=self.account_1.id, message=self.create_message(2), is_premium=False)
        heroes_tt_api.push_message_to_diary(account_id=self.account_1.id, message=self.create_message(3), is_premium=False)

    def create_message(self, uid):
        return heroes_messages.MessageSurrogate(turn_number=turn.number(),
                                                timestamp=time.time(),
                                                key=None,
                                                externals=None,
                                                message='message {}'.format(uid),
                                                position='position {}'.format(uid))

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.request_ajax_json(logic.game_diary_url()), 'common.login_required')

    def test_logined(self):
        data = self.check_ajax_ok(self.request_ajax_json(logic.game_diary_url()))

        self.assertIn('version', data)

        for message in data['messages']:
            self.assertEqual(set(message), {'timestamp',
                                            'game_time',
                                            'game_date',
                                            'message',
                                            'type',
                                            'variables',
                                            'position'})


class HeroHistoryTests(RequestTestsBase):

    def get_random_properties(self):
        properties_1 = {'gender': relations.GENDER.random(),
                        'race': relations.RACE.random(),
                        'archetype': relations.ARCHETYPE.random(),
                        'upbringing': beings_relations.UPBRINGING.random(),
                        'first_death': beings_relations.FIRST_DEATH.random(),
                        'age': beings_relations.AGE.random(),
                        'honor': relations.HABIT_HONOR_INTERVAL.LEFT_1,
                        'peacefulness': relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_1}

        properties_2 = {'gender': relations.GENDER.random(exclude=[properties_1['gender']]),
                        'race': relations.RACE.random(exclude=[properties_1['race']]),
                        'archetype': relations.ARCHETYPE.random(exclude=[properties_1['archetype']]),
                        'upbringing': beings_relations.UPBRINGING.random(exclude=[properties_1['upbringing']]),
                        'first_death': beings_relations.FIRST_DEATH.random(exclude=[properties_1['first_death']]),
                        'age': beings_relations.AGE.random(exclude=[properties_1['age']]),
                        'honor': relations.HABIT_HONOR_INTERVAL.RIGHT_1,
                        'peacefulness': relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_1}

        return properties_1, properties_2

    def get_restrictions(self, properties):
        from the_tale.linguistics.storage import restrictions_storage as s
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP as G

        return {s.get_restriction(G.GENDER, properties['gender'].value).id,
                s.get_restriction(G.RACE, properties['race'].value).id,
                s.get_restriction(G.ARCHETYPE, properties['archetype'].value).id,
                s.get_restriction(G.UPBRINGING, properties['upbringing'].value).id,
                s.get_restriction(G.FIRST_DEATH, properties['first_death'].value).id,
                s.get_restriction(G.AGE, properties['age'].value).id,
                s.get_restriction(G.HABIT_HONOR, properties['honor'].value).id,
                s.get_restriction(G.HABIT_PEACEFULNESS, properties['peacefulness'].value).id}

    def setUp(self):
        super().setUp()

        self.properties_1, self.properties_2 = self.get_random_properties()

        restrictions_1 = self.get_restrictions(self.properties_1)
        restrictions_2 = self.get_restrictions(self.properties_2)

        self.templates = [self.create_template(key='HERO_HISTORY_BIRTH',
                                               text='history.1',
                                               restrictions=restrictions_1),

                          self.create_template(key='HERO_HISTORY_BIRTH',
                                               text='history.2',
                                               restrictions={}),

                          self.create_template(key='HERO_HISTORY_CHILDHOOD',
                                               text='history.3',
                                               restrictions=restrictions_1),

                          self.create_template(key='HERO_HISTORY_DEATH',
                                               text='history.4',
                                               restrictions=restrictions_1),

                          self.create_template(key='HERO_HISTORY_DEATH',
                                               text='history.5',
                                               restrictions=restrictions_2)]

    def create_template(self, key, text, restrictions):
        from utg import templates as utg_templates

        from the_tale.linguistics.lexicon import keys
        from the_tale.linguistics import prototypes as linguistics_prototypes
        from the_tale.linguistics import relations as linguistics_relations
        from the_tale.linguistics.storage import game_lexicon

        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])

        template = linguistics_prototypes.TemplatePrototype.create(key=getattr(keys.LEXICON_KEY, key),
                                                                   raw_template=text,
                                                                   utg_template=utg_template,
                                                                   verificators=[],
                                                                   restrictions={('hero', restriction) for restriction in restrictions},
                                                                   state=linguistics_relations.TEMPLATE_STATE.IN_GAME,
                                                                   author=self.account_1)

        linguistics_prototypes.TemplatePrototype._db_all().update(errors_status=linguistics_relations.TEMPLATE_ERRORS_STATUS.NO_ERRORS)

        game_lexicon.refresh()

        return template

    def test_success__full_restrictions(self):
        post_data = {key: value.value for key, value in self.properties_1.items()}
        post_data['name'] = 'x,x,x,x,x,x'

        data = self.check_ajax_ok(self.post_ajax_json(logic.game_hero_history_url(), data=post_data))

        self.assertEqual(data['story'], ['history.1', 'history.3', 'history.4'])

    def test_success__missed_tempaltes(self):
        post_data = {key: value.value for key, value in self.properties_2.items()}
        post_data['name'] = 'x,x,x,x,x,x'

        data = self.check_ajax_ok(self.post_ajax_json(logic.game_hero_history_url(), data=post_data))

        self.assertEqual(data['story'], ['history.2', None, 'history.5'])


class HeroHistoryStatusTests(RequestTestsBase):

    def test_success(self):
        self.check_html_ok(self.client.get(reverse('game:hero-history-status')))
