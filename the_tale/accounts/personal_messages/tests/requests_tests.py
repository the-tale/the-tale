# coding: utf-8

from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from game.logic import create_test_map

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url

from accounts.personal_messages.prototypes import MessagePrototype
from accounts.personal_messages.models import Message
from accounts.personal_messages.conf import personal_messages_settings

class BaseRequestsTests(TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user3', 'test_user3@test.com', '111111')
        self.account3 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user4', 'test_user4@test.com', '111111')
        self.account4 = AccountPrototype.get_by_id(account_id)


class IndexRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(IndexRequestsTests, self).setUp()

        self.messages_1_2 = [MessagePrototype.create(self.account1, self.account2, 'message_1_2 1'),
                             MessagePrototype.create(self.account1, self.account2, 'message_1_2 2'),
                             MessagePrototype.create(self.account1, self.account2, 'message_1_2 3')]

        self.messages_2_1 = [MessagePrototype.create(self.account2, self.account1, 'message_2_1 1'),
                             MessagePrototype.create(self.account2, self.account1, 'message_2_1 2')]

        self.messages_3_1 = [MessagePrototype.create(self.account3, self.account1, 'message_3_1 1')]
        self.messages_3_2 = [MessagePrototype.create(self.account3, self.account2, 'message_3_2 1')]

    def test_initialize(self):
        self.assertEqual(Message.objects.all().count(), 7)

    def test_unlogined_index(self):
        request_url = reverse('accounts:messages:')
        self.assertRedirects(self.client.get(request_url), login_url(request_url), status_code=302, target_status_code=200)

    def test_unlogined_sent(self):
        request_url = reverse('accounts:messages:sent')
        self.assertRedirects(self.client.get(request_url), login_url(request_url), status_code=302, target_status_code=200)


    def test_index(self):
        self.request_login('test_user1@test.com')
        texts = [('message_2_1 1', 1),
                 ('message_2_1 2', 1),
                 ('message_3_1 1', 1),]

        self.check_html_ok(self.client.get(reverse('accounts:messages:')), texts=texts)

    def test_index_no_messages(self):
        self.request_login('test_user4@test.com')
        self.check_html_ok(self.client.get(reverse('accounts:messages:')), texts=[('pgf-no-messages', 1)])

    def test_sent(self):
        self.request_login('test_user1@test.com')
        texts = [('message_1_2 1', 1),
                 ('message_1_2 2', 1),
                 ('message_1_2 3', 1),]

        self.check_html_ok(self.client.get(reverse('accounts:messages:sent')), texts=texts)

    def test_sent_no_messages(self):
        self.request_login('test_user4@test.com')
        self.check_html_ok(self.client.get(reverse('accounts:messages:sent')), texts=[('pgf-no-messages', 1)])

    def test_index_second_page(self):
        for i in xrange(personal_messages_settings.MESSAGES_ON_PAGE):
            MessagePrototype.create(self.account2, self.account1, 'test message_2_1 %d' % i)

        texts = []
        for i in xrange(personal_messages_settings.MESSAGES_ON_PAGE):
            texts.append(('test message_2_1 %d' % i, 1))

        self.request_login('test_user1@test.com')
        self.check_html_ok(self.client.get(reverse('accounts:messages:')), texts=texts)

    def test_index_big_page_number(self):
        self.request_login('test_user1@test.com')
        self.assertRedirects(self.client.get(reverse('accounts:messages:')+'?page=2'),
                             reverse('accounts:messages:')+'?page=1', status_code=302, target_status_code=200)



class NewRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(NewRequestsTests, self).setUp()
        self.request_login('test_user1@test.com')

    def test_unlogined(self):
        self.request_logout()
        request_url = reverse('accounts:messages:new')
        self.assertRedirects(self.client.get(request_url), login_url(request_url), status_code=302, target_status_code=200)

    def test_wrong_recipient_id(self):
        self.check_html_ok(self.client.get(reverse('accounts:messages:new') + '?recipient=aaa'),
                           texts=[('personal_messages.new.wrong_recipient_id', 1)],
                           status_code=404)

    def test_recipient_not_found(self):
        self.check_html_ok(self.client.get(reverse('accounts:messages:new') + '?recipient=666'),
                           texts=[('personal_messages.new.recipient_not_found', 1)],
                           status_code=404)

    def test_answer_wrong_message_id(self):
        MessagePrototype.create(self.account2, self.account1, 'message_2_1 1')
        self.check_html_ok(self.client.get(reverse('accounts:messages:new') + ('?recipient=%d&answer_to=aaa' % self.account2.id)),
                           texts=[('personal_messages.new.wrong_answer_id', 1)],
                           status_code=404)

    def test_answer_to_not_found(self):
        MessagePrototype.create(self.account2, self.account1, 'message_2_1 1')
        self.check_html_ok(self.client.get(reverse('accounts:messages:new') + ('?recipient=%d&answer_to=666' % self.account2.id)),
                           texts=[('personal_messages.new.message_not_found', 1)],
                           status_code=404)

    def test_answer_to_no_permissionsd(self):
        message = MessagePrototype.create(self.account2, self.account3, 'message_2_3 1')
        self.check_html_ok(self.client.get(reverse('accounts:messages:new') + ('?recipient=%d&answer_to=%d' % (self.account2.id, message.id))),
                           texts=[('personal_messages.new.not_permissions_to_answer_to', 1)])

    def test_success(self):
        self.check_html_ok(self.client.get(reverse('accounts:messages:new') + ('?recipient=%d' % self.account2.id)),
                           texts=[('pgf-new-message-form', 4)])


    def test_answer_to(self):
        message = MessagePrototype.create(self.account2, self.account1, 'message_2_1 1')
        self.check_html_ok(self.client.get(reverse('accounts:messages:new') + ('?recipient=%d&answer_to=%d' % (self.account2.id, message.id))),
                           texts=[('pgf-new-message-form', 4),
                                  ('message_2_1 1', 1)])


class CreateRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(CreateRequestsTests, self).setUp()
        self.request_login('test_user1@test.com')

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('accounts:messages:create'), {'text': 'test-message'}), 'common.login_required')
        self.assertEqual(Message.objects.all().count(), 0)

    def test_wrong_recipient_id(self):
        self.check_ajax_error(self.client.post(reverse('accounts:messages:create') + '?recipient=aaa', {'text': 'test-message'}),
                              'personal_messages.create.wrong_recipient_id')
        self.assertEqual(Message.objects.all().count(), 0)

    def test_recipient_not_found(self):
        self.check_ajax_error(self.client.post(reverse('accounts:messages:create') + '?recipient=666', {'text': 'test-message'}),
                              'personal_messages.create.recipient_not_found')
        self.assertEqual(Message.objects.all().count(), 0)

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('accounts:messages:create') + ('?recipient=%d' % self.account2.id), {'text': ''}),
                              'personal_messages.create.form_errors')
        self.assertEqual(Message.objects.all().count(), 0)

    def test_success(self):
        self.check_ajax_ok(self.client.post(reverse('accounts:messages:create') + ('?recipient=%d' % self.account2.id), {'text': 'test-message'}))
        self.assertEqual(Message.objects.all().count(), 1)
        message = MessagePrototype(Message.objects.all()[0])
        self.assertEqual(message.text, 'test-message')
        self.assertEqual(message.sender_id, self.account1.id)
        self.assertEqual(message.recipient_id, self.account2.id)


class DeleteRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(DeleteRequestsTests, self).setUp()
        self.message = MessagePrototype.create(self.account1, self.account2, 'message_1_2 1')

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('accounts:messages:delete', args=[self.message.id])), 'common.login_required')

    def test_delete_no_permissions(self):
        self.request_login('test_user3@test.com')
        self.check_ajax_error(self.client.post(reverse('accounts:messages:delete', args=[self.message.id])), 'personal_messages.delete.no_permissions')

    def test_delete_from_sender(self):
        self.request_login('test_user1@test.com')
        self.check_ajax_ok(self.client.post(reverse('accounts:messages:delete', args=[self.message.id])))
        message = MessagePrototype.get_by_id(self.message.id)
        self.assertTrue(message.hide_from_sender)
        self.assertFalse(message.hide_from_recipient)

    def test_delete_from_recipient(self):
        self.request_login('test_user2@test.com')
        self.check_ajax_ok(self.client.post(reverse('accounts:messages:delete', args=[self.message.id])))
        message = MessagePrototype.get_by_id(self.message.id)
        self.assertFalse(message.hide_from_sender)
        self.assertTrue(message.hide_from_recipient)
