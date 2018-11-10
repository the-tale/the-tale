
import smart_imports

smart_imports.all()


class BaseRequestsTests(utils_testcase.TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()
        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()
        self.account_4 = self.accounts_factory.create_account()


class IndexRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(IndexRequestsTests, self).setUp()

        tt_services.personal_messages.cmd_debug_clear_service()

        logic.send_message(self.account_1.id, [self.account_2.id], 'message_1_2 1')
        logic.send_message(self.account_1.id, [self.account_2.id], 'message_1_2 2')
        logic.send_message(self.account_1.id, [self.account_2.id], 'message_1_2 3')

        logic.send_message(self.account_2.id, [self.account_1.id], 'message_2_1 1')
        logic.send_message(self.account_2.id, [self.account_1.id], 'message_2_1 2')

        logic.send_message(self.account_3.id, [self.account_1.id], 'message_3_1 1')
        logic.send_message(self.account_3.id, [self.account_2.id], 'message_3_2 1')

    def test_unlogined_index(self):
        request_url = dext_urls.url('accounts:messages:')
        self.check_redirect(request_url, accounts_logic.login_page_url(request_url))

    def test_fast_account(self):
        self.request_login(self.account_1.email)
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_html_ok(self.request_html(dext_urls.url('accounts:messages:')), texts=['common.fast_account'])

    def test_index(self):
        self.request_login(self.account_1.email)
        texts = [('message_2_1 1', 1),
                 ('message_2_1 2', 1),
                 ('message_3_1 1', 1), ]

        self.check_html_ok(self.request_html(dext_urls.url('accounts:messages:')), texts=texts)

    def test_index_no_messages(self):
        self.request_login(self.account_4.email)
        self.check_html_ok(self.request_html(dext_urls.url('accounts:messages:')), texts=[('pgf-no-messages', 1)])

    def test_index_second_page(self):
        for i in range(conf.settings.MESSAGES_ON_PAGE):
            logic.send_message(self.account_2.id, [self.account_1.id], 'test message_2_1 %d' % i)

        texts = []
        for i in range(conf.settings.MESSAGES_ON_PAGE):
            texts.append(('test message_2_1 %d' % i, 1))

        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(dext_urls.url('accounts:messages:')), texts=texts)

    def test_index_big_page_number(self):
        self.request_login(self.account_1.email)
        self.check_redirect(dext_urls.url('accounts:messages:') + '?page=2', dext_urls.url('accounts:messages:') + '?page=1')


class SentRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(SentRequestsTests, self).setUp()

        tt_services.personal_messages.cmd_debug_clear_service()

        logic.send_message(self.account_1.id, [self.account_2.id], 'message_1_2 1')
        logic.send_message(self.account_1.id, [self.account_2.id], 'message_1_2 2')
        logic.send_message(self.account_1.id, [self.account_2.id], 'message_1_2 3')

        logic.send_message(self.account_2.id, [self.account_1.id], 'message_2_1 1')
        logic.send_message(self.account_2.id, [self.account_1.id], 'message_2_1 2')

        logic.send_message(self.account_3.id, [self.account_1.id], 'message_3_1 1')
        logic.send_message(self.account_3.id, [self.account_2.id], 'message_3_2 1')

    def test_fast_account(self):
        self.request_login(self.account_1.email)
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_html_ok(self.request_html(dext_urls.url('accounts:messages:sent')), texts=['common.fast_account'])

    def test_unlogined_sent(self):
        request_url = dext_urls.url('accounts:messages:sent')
        self.check_redirect(request_url, accounts_logic.login_page_url(request_url))

    def test_sent(self):
        self.request_login(self.account_1.email)
        texts = [('message_1_2 1', 1),
                 ('message_1_2 2', 1),
                 ('message_1_2 3', 1), ]

        self.check_html_ok(self.request_html(dext_urls.url('accounts:messages:sent')), texts=texts)

    def test_sent_no_messages(self):
        self.request_login(self.account_4.email)
        self.check_html_ok(self.request_html(dext_urls.url('accounts:messages:sent')), texts=[('pgf-no-messages', 1)])


class ConversationRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(ConversationRequestsTests, self).setUp()

        tt_services.personal_messages.cmd_debug_clear_service()

        logic.send_message(self.account_1.id, [self.account_2.id], 'message_1_2 1')
        logic.send_message(self.account_1.id, [self.account_2.id], 'message_1_2 2')
        logic.send_message(self.account_1.id, [self.account_2.id], 'message_1_2 3')

        logic.send_message(self.account_2.id, [self.account_1.id], 'message_2_1 1')
        logic.send_message(self.account_2.id, [self.account_1.id], 'message_2_1 2')

        logic.send_message(self.account_3.id, [self.account_1.id], 'message_3_1 1')
        logic.send_message(self.account_3.id, [self.account_2.id], 'message_3_2 1')

    def test_fast_account(self):
        self.request_login(self.account_1.email)
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_html_ok(self.request_html(dext_urls.url('accounts:messages:conversation', contact=self.account_2.id)), texts=['common.fast_account'])

    def test_unlogined_sent(self):
        request_url = dext_urls.url('accounts:messages:conversation', contact=self.account_2.id)
        self.check_redirect(request_url, accounts_logic.login_page_url(request_url))

    def test_sent(self):
        self.request_login(self.account_1.email)
        texts = [('message_1_2 1', 1),
                 ('message_1_2 2', 1),
                 ('message_1_2 3', 1),
                 ('message_2_1 1', 1),
                 ('message_2_1 2', 1)]

        self.check_html_ok(self.request_html(dext_urls.url('accounts:messages:conversation', contact=self.account_2.id)), texts=texts)

    def test_sent_no_messages(self):
        self.request_login(self.account_4.email)
        self.check_html_ok(self.request_html(dext_urls.url('accounts:messages:conversation', contact=self.account_2.id)), texts=[('pgf-no-messages', 1)])


class NewRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(NewRequestsTests, self).setUp()
        self.request_login(self.account_1.email)

    def test_unlogined(self):
        self.request_logout()
        request_url = dext_urls.url('accounts:messages:new')
        self.check_redirect(request_url, accounts_logic.login_page_url(request_url))

    def test_fast_account(self):
        self.request_login(self.account_1.email)
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new'), {'recipients': self.account_2.id}), texts=['common.fast_account'])

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_banned_account(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new'), {'recipients': self.account_2.id}), texts=['common.ban_forum'])

    def test_wrong_recipient_id(self):
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new'), {'recipients': 'aaa'}),
                           texts=[('pgf-error-form_errors', 1)])

    def test_recipient_not_found(self):
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new'), {'recipients': 666}),
                           texts=[('pgf-error-unexisted_account', 1)])

    def test_recipient_is_sender(self):
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new'), {'recipients': self.account_1.id}),
                           texts=[('pgf-error-current_user', 1)])

    def test_answer_wrong_message_id(self):
        logic.send_message(self.account_2.id, [self.account_1.id], 'message_2_1 1')
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new', answer_to='aaa'), {'recipients': self.account_2.id}),
                           texts=[('pgf-error-answer_to.wrong_format', 1)])

    def test_answer_to_not_found(self):
        logic.send_message(self.account_2.id, [self.account_1.id], 'message_2_1 1')
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new', answer_to=666), {'recipients': self.account_2.id}),
                           texts=[('pgf-error-answer_to.wrong_value', 1)])

    def test_answer_to_no_permissions(self):
        message_id = logic.send_message(self.account_2.id, [self.account_3.id], 'message_2_3 1')
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new', answer_to=message_id), {'recipients': self.account_2.id}),
                           texts=[('pgf-error-answer_to.wrong_value', 1)])

    def test_success(self):
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new'), {'recipients': self.account_2.id}),
                           texts=[('pgf-new-message-form', 1)])

    def test_success_multiply_accoutns(self):
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new'), {'recipients': ('%d,%d' % (self.account_2.id, self.account_3.id))}),
                           texts=[('pgf-new-message-form', 1),
                                  (self.account_2.nick, 1),
                                  (self.account_3.nick, 1)])

    def test_answer_to(self):
        message_id = logic.send_message(self.account_2.id, [self.account_1.id], 'message_2_1 1')
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new', answer_to=message_id), {'recipients': self.account_2.id}),
                           texts=[('pgf-new-message-form', 1),
                                  ('message_2_1 1', 1)])

    def test_sent_to_system_user(self):
        recipients = '%d,%d' % (self.account_2.id, accounts_logic.get_system_user().id)
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new'), {'recipients': recipients}),
                           texts=[('pgf-error-system_user', 1)])

    def test_sent_to_fast_user(self):
        self.account_3.is_fast = True
        self.account_3.save()
        recipients = '%d,%d' % (self.account_2.id, self.account_3.id)
        self.check_html_ok(self.post_ajax_html(dext_urls.url('accounts:messages:new'), {'recipients': recipients}),
                           texts=[('pgf-error-fast_account', 1)])


class CreateRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(CreateRequestsTests, self).setUp()
        self.request_login(self.account_1.email)
        tt_services.personal_messages.cmd_debug_clear_service()

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message'}), 'common.login_required')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 0)

    def test_fast_account(self):
        self.request_login(self.account_1.email)
        self.account_1.is_fast = True
        self.account_1.save()

        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message'}), 'common.fast_account')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 0)

    @mock.patch('the_tale.accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_banned_account(self):
        self.request_login(self.account_1.email)

        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message'}), 'common.ban_forum')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 0)

    def test_wrong_recipient_id(self):
        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message', 'recipients': 'aaa'}),
                              'form_errors')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 0)

    def test_recipient_not_found(self):
        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message', 'recipients': '666'}),
                              'unexisted_account')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 0)

    def test_recipient_is_owner(self):
        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message', 'recipients': self.account_1.id}),
                              'current_user')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 0)

    def test_form_errors(self):
        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': '', 'recipients': self.account_2.id}),
                              'form_errors')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 0)

    def test_success(self):
        with self.check_delta(post_service_prototypes.MessagePrototype._db_count, 1):
            self.check_ajax_ok(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message', 'recipients': self.account_2.id}))

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 1)

        self.assertEqual(messages[0].body, 'test-message')
        self.assertEqual(messages[0].sender_id, self.account_1.id)
        self.assertEqual(messages[0].recipients_ids, [self.account_2.id])

    def test_success_multiply_accoutns(self):
        self.check_ajax_ok(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message', 'recipients': ('%d,%d' % (self.account_2.id, self.account_3.id))}))

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 1)

        self.assertEqual(messages[0].body, 'test-message')
        self.assertEqual(messages[0].sender_id, self.account_1.id)
        self.assertEqual(set(messages[0].recipients_ids), {self.account_2.id, self.account_3.id})

    def test_sent_to_system_user(self):
        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message', 'recipients': ('%d,%d' % (self.account_2.id, accounts_logic.get_system_user().id))}),
                              'system_user')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 0)

    def test_sent_to_fast_user(self):
        self.account_3.is_fast = True
        self.account_3.save()

        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message', 'recipients': ('%d,%d' % (self.account_2.id, self.account_3.id))}),
                              'fast_account')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 0)


class DeleteRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(DeleteRequestsTests, self).setUp()
        tt_services.personal_messages.cmd_debug_clear_service()
        self.message_id = logic.send_message(self.account_1.id, [self.account_2.id], 'message_1_2 1')

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:delete', self.message_id)), 'common.login_required')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 1)

    def test_fast_account(self):
        self.request_login(self.account_1.email)
        self.account_1.is_fast = True
        self.account_1.save()

        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:delete', self.message_id)), 'common.fast_account')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 1)

    def test_delete_no_permissions(self):
        self.request_login(self.account_3.email)

        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:delete', self.message_id)), 'message_id.wrong_value')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 1)

    def test_delete_from_sender(self):
        self.request_login(self.account_1.email)

        self.check_ajax_ok(self.post_ajax_json(dext_urls.url('accounts:messages:delete', self.message_id)))

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 0)

        total, messages = tt_services.personal_messages.cmd_get_received_messages(self.account_2.id)
        self.assertEqual(total, 1)

    def test_delete_from_recipient(self):
        self.request_login(self.account_2.email)

        self.check_ajax_ok(self.post_ajax_json(dext_urls.url('accounts:messages:delete', self.message_id)))

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 1)

        total, messages = tt_services.personal_messages.cmd_get_received_messages(self.account_2.id)
        self.assertEqual(total, 0)


class DeleteAllRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(DeleteAllRequestsTests, self).setUp()
        tt_services.personal_messages.cmd_debug_clear_service()
        self.messages_ids = [logic.send_message(self.account_1.id, [self.account_2.id], '1'),
                             logic.send_message(self.account_2.id, [self.account_1.id, self.account_3.id], '2'),
                             logic.send_message(self.account_1.id, [self.account_3.id], '3')]

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:delete-all')), 'common.login_required')

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 2)

        total, messages = tt_services.personal_messages.cmd_get_received_messages(self.account_1.id)
        self.assertEqual(total, 1)

    def test_fast_account(self):
        self.request_login(self.account_1.email)
        self.account_1.is_fast = True
        self.account_1.save()

        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:delete-all')), 'common.fast_account')

    def test_delete(self):
        self.request_login(self.account_1.email)

        self.check_ajax_ok(self.post_ajax_json(dext_urls.url('accounts:messages:delete-all')))

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_1.id)
        self.assertEqual(total, 0)

        total, messages = tt_services.personal_messages.cmd_get_received_messages(self.account_1.id)
        self.assertEqual(total, 0)

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_2.id)
        self.assertEqual(total, 1)

        total, messages = tt_services.personal_messages.cmd_get_received_messages(self.account_2.id)
        self.assertEqual(total, 1)

        total, messages = tt_services.personal_messages.cmd_get_sent_messages(self.account_3.id)
        self.assertEqual(total, 0)

        total, messages = tt_services.personal_messages.cmd_get_received_messages(self.account_3.id)
        self.assertEqual(total, 2)


class DeleteConversationRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(DeleteConversationRequestsTests, self).setUp()
        tt_services.personal_messages.cmd_debug_clear_service()
        self.messages_ids = [logic.send_message(self.account_1.id, [self.account_2.id], '1'),
                             logic.send_message(self.account_2.id, [self.account_1.id, self.account_3.id], '2'),
                             logic.send_message(self.account_1.id, [self.account_3.id], '3')]

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:delete-conversation', contact=self.account_2.id)), 'common.login_required')

        total, messages = tt_services.personal_messages.cmd_get_conversation(self.account_1.id, self.account_2.id)
        self.assertEqual(total, 2)

        total, messages = tt_services.personal_messages.cmd_get_conversation(self.account_2.id, self.account_1.id)
        self.assertEqual(total, 2)

        total, messages = tt_services.personal_messages.cmd_get_conversation(self.account_1.id, self.account_3.id)
        self.assertEqual(total, 1)

        total, messages = tt_services.personal_messages.cmd_get_conversation(self.account_3.id, self.account_1.id)
        self.assertEqual(total, 1)

    def test_fast_account(self):
        self.request_login(self.account_1.email)
        self.account_1.is_fast = True
        self.account_1.save()

        self.check_ajax_error(self.post_ajax_json(dext_urls.url('accounts:messages:delete-conversation', contact=self.account_2.id)), 'common.fast_account')

    def test_delete(self):
        self.request_login(self.account_1.email)

        self.check_ajax_ok(self.post_ajax_json(dext_urls.url('accounts:messages:delete-conversation', contact=self.account_2.id)))

        total, messages = tt_services.personal_messages.cmd_get_conversation(self.account_1.id, self.account_2.id)
        self.assertEqual(total, 0)

        total, messages = tt_services.personal_messages.cmd_get_conversation(self.account_2.id, self.account_1.id)
        self.assertEqual(total, 2)

        total, messages = tt_services.personal_messages.cmd_get_conversation(self.account_1.id, self.account_3.id)
        self.assertEqual(total, 1)

        total, messages = tt_services.personal_messages.cmd_get_conversation(self.account_3.id, self.account_1.id)
        self.assertEqual(total, 1)


class NewMessagesNumberTests(BaseRequestsTests):

    def setUp(self):
        super(NewMessagesNumberTests, self).setUp()
        self.request_login(self.account_1.email)
        tt_services.personal_messages.cmd_debug_clear_service()

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(logic.new_messages_number_url()), 'common.login_required')

    def test_success__no_messages(self):
        data = self.check_ajax_ok(self.request_ajax_json(logic.new_messages_number_url()))
        self.assertEqual(data, {'number': 0})

    def test_success__has_messages(self):
        self.check_ajax_ok(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message', 'recipients': ('%d,%d' % (self.account_2.id, self.account_3.id))}))

        self.request_logout()
        self.request_login(self.account_2.email)

        self.check_ajax_ok(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message', 'recipients': ('%d,%d' % (self.account_1.id, self.account_3.id))}))
        self.check_ajax_ok(self.post_ajax_json(dext_urls.url('accounts:messages:create'), {'text': 'test-message', 'recipients': ('%d,%d' % (self.account_1.id, self.account_3.id))}))

        self.request_logout()
        self.request_login(self.account_1.email)

        data = self.check_ajax_ok(self.request_ajax_json(logic.new_messages_number_url()))
        self.assertEqual(data, {'number': 2})
