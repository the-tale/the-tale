
import datetime

from aiohttp import test_utils

from tt_protocol.protocol import data_protector_pb2
from tt_protocol.protocol import personal_messages_pb2

from tt_web import s11n
from tt_web import postgresql as db

from .. import protobuf
from .. import relations
from .. import operations

from . import helpers


async def load_protocol_messages_by_bodies(bodies):
    messages = []

    for body in bodies:
        result = await db.sql('''SELECT messages.*, v.visible as visible FROM messages
                                 JOIN visibilities AS v ON messages.id = v.message
                                 WHERE body LIKE %(body)s''', {'body': '%{}%'.format(body)})
        messages.append(protobuf.from_message(operations.message_from_row(result[0])))

    return messages


class Mixin(object):

    async def create_messages(self):
        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=1,
                                                                                                        recipients_ids=[2, 3],
                                                                                                        body='message 1').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=2,
                                                                                                        recipients_ids=[3],
                                                                                                        body='message 2').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)


class NewMessagesNumberTests(Mixin, helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_messages(self):
        request = await self.client.post('/new-messages-number', data=personal_messages_pb2.NewMessagesNumberRequest(account_id=1).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.NewMessagesNumberResponse)
        self.assertEqual(data.number, 0)

    @test_utils.unittest_run_loop
    async def test_has_messages(self):
        await self.create_messages()

        request = await self.client.post('/new-messages-number', data=personal_messages_pb2.NewMessagesNumberRequest(account_id=1).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.NewMessagesNumberResponse)
        self.assertEqual(data.number, 0)

        request = await self.client.post('/new-messages-number', data=personal_messages_pb2.NewMessagesNumberRequest(account_id=2).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.NewMessagesNumberResponse)
        self.assertEqual(data.number, 1)

        request = await self.client.post('/new-messages-number', data=personal_messages_pb2.NewMessagesNumberRequest(account_id=3).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.NewMessagesNumberResponse)
        self.assertEqual(data.number, 2)


class GetContactsTests(Mixin, helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_contacts(self):
        request = await self.client.post('/get-contacts', data=personal_messages_pb2.GetContactsRequest(account_id=1).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetContactsResponse)
        self.assertEqual(data.accounts_ids, [])

    @test_utils.unittest_run_loop
    async def test_has_contacts(self):
        await self.create_messages()

        request = await self.client.post('/get-contacts', data=personal_messages_pb2.GetContactsRequest(account_id=1).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetContactsResponse)
        self.assertCountEqual(data.accounts_ids, [2, 3])

        request = await self.client.post('/get-contacts', data=personal_messages_pb2.GetContactsRequest(account_id=2).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetContactsResponse)
        self.assertCountEqual(data.accounts_ids, [1, 3])

        request = await self.client.post('/get-contacts', data=personal_messages_pb2.GetContactsRequest(account_id=3).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetContactsResponse)
        self.assertCountEqual(data.accounts_ids, [1, 2])


class ReadMessagesTests(Mixin, helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_messages(self):
        request = await self.client.post('/read-messages', data=personal_messages_pb2.ReadMessagesRequest(account_id=1).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.ReadMessagesResponse)

        request = await self.client.post('/read-messages', data=personal_messages_pb2.ReadMessagesRequest(account_id=1).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.NewMessagesNumberResponse)
        self.assertEqual(data.number, 0)

    @test_utils.unittest_run_loop
    async def test_has_messages(self):
        await self.create_messages()

        request = await self.client.post('/read-messages', data=personal_messages_pb2.ReadMessagesRequest(account_id=1).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.ReadMessagesResponse)

        request = await self.client.post('/read-messages', data=personal_messages_pb2.ReadMessagesRequest(account_id=2).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.ReadMessagesResponse)

        request = await self.client.post('/read-messages', data=personal_messages_pb2.ReadMessagesRequest(account_id=3).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.ReadMessagesResponse)

        request = await self.client.post('/new-messages-number', data=personal_messages_pb2.NewMessagesNumberRequest(account_id=1).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.NewMessagesNumberResponse)
        self.assertEqual(data.number, 0)

        request = await self.client.post('/new-messages-number', data=personal_messages_pb2.NewMessagesNumberRequest(account_id=2).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.NewMessagesNumberResponse)
        self.assertEqual(data.number, 0)

        request = await self.client.post('/new-messages-number', data=personal_messages_pb2.NewMessagesNumberRequest(account_id=3).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.NewMessagesNumberResponse)
        self.assertEqual(data.number, 0)


class SendMessageTests(Mixin, helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_send(self):
        await self.create_messages()

        result = await db.sql('SELECT sender, recipients, body FROM messages')

        self.assertEqual({(row['sender'], tuple(row['recipients']), row['body']) for row in result},
                          {(1, (2, 3), 'message 1'),
                           (2, (3,), 'message 2')})

        result = await db.sql('SELECT v.account as account, m.body as body, v.visible as visible FROM visibilities AS v JOIN messages AS m ON v.message=m.id')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account': 1, 'body': 'message 1', 'visible': True},
                               {'account': 2, 'body': 'message 1', 'visible': True},
                               {'account': 3, 'body': 'message 1', 'visible': True},
                               {'account': 2, 'body': 'message 2', 'visible': True},
                               {'account': 3, 'body': 'message 2', 'visible': True}])

        result = await db.sql('SELECT c.account_1 as account_1, c.account_2 as account_2, m.body as body FROM conversations AS c JOIN messages AS m ON c.message=m.id')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account_1': 1, 'account_2': 2, 'body': 'message 1'},
                               {'account_1': 1, 'account_2': 3, 'body': 'message 1'},
                               {'account_1': 2, 'account_2': 3, 'body': 'message 2'}])


class HideMessageTests(Mixin, helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_hide(self):
        await self.create_messages()

        result = await db.sql('SELECT id, body, body FROM messages')
        messages_ids = {row['body']: row['id'] for row in result}

        request = await self.client.post('/hide-message', data=personal_messages_pb2.HideMessageRequest(account_id=1, message_id=messages_ids['message 1']).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.HideMessageResponse)

        request = await self.client.post('/hide-message', data=personal_messages_pb2.HideMessageRequest(account_id=1, message_id=messages_ids['message 2']).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.HideMessageResponse)

        request = await self.client.post('/hide-message', data=personal_messages_pb2.HideMessageRequest(account_id=1, message_id=1000500).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.HideMessageResponse)

        request = await self.client.post('/hide-message', data=personal_messages_pb2.HideMessageRequest(account_id=2, message_id=messages_ids['message 1']).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.HideMessageResponse)

        request = await self.client.post('/hide-message', data=personal_messages_pb2.HideMessageRequest(account_id=2, message_id=messages_ids['message 2']).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.HideMessageResponse)

        result = await db.sql('SELECT v.account as account, m.body as body, v.visible as visible FROM visibilities AS v JOIN messages AS m ON v.message=m.id')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account': 1, 'body': 'message 1', 'visible': False},
                               {'account': 2, 'body': 'message 1', 'visible': False},
                               {'account': 3, 'body': 'message 1', 'visible': True},
                               {'account': 2, 'body': 'message 2', 'visible': False},
                               {'account': 3, 'body': 'message 2', 'visible': True}])


class HideAllMessagesTests(Mixin, helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_hide(self):
        await self.create_messages()

        request = await self.client.post('/hide-all-messages', data=personal_messages_pb2.HideAllMessagesRequest(account_id=3).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.HideAllMessagesResponse)

        result = await db.sql('SELECT v.account as account, m.body as body, v.visible as visible FROM visibilities AS v JOIN messages AS m ON v.message=m.id')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account': 1, 'body': 'message 1', 'visible': True},
                               {'account': 2, 'body': 'message 1', 'visible': True},
                               {'account': 3, 'body': 'message 1', 'visible': False},
                               {'account': 2, 'body': 'message 2', 'visible': True},
                               {'account': 3, 'body': 'message 2', 'visible': False}])


class HideConversationTests(Mixin, helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_hide(self):
        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=1,
                                                                                                        recipients_ids=[2, 3],
                                                                                                        body='message 1').SerializeToString())
        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=2,
                                                                                                        recipients_ids=[3],
                                                                                                        body='message 2').SerializeToString())
        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=3,
                                                                                                        recipients_ids=[2, 1],
                                                                                                        body='message 3').SerializeToString())

        request = await self.client.post('/hide-conversation', data=personal_messages_pb2.HideConversationRequest(account_id=1, partner_id=3).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.HideConversationResponse)

        result = await db.sql('SELECT v.account as account, m.body as body, v.visible as visible FROM visibilities AS v JOIN messages AS m ON v.message=m.id')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account': 1, 'body': 'message 1', 'visible': False},
                               {'account': 2, 'body': 'message 1', 'visible': True},
                               {'account': 3, 'body': 'message 1', 'visible': True},

                               {'account': 2, 'body': 'message 2', 'visible': True},
                               {'account': 3, 'body': 'message 2', 'visible': True},

                               {'account': 1, 'body': 'message 3', 'visible': False},
                               {'account': 2, 'body': 'message 3', 'visible': True},
                               {'account': 3, 'body': 'message 3', 'visible': True},])


class RemoveOldMessagesTests(Mixin, helpers.BaseTests):

    async def prepair_data(self):
        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=1,
                                                                                                        recipients_ids=[2, 3],
                                                                                                        body='message 1').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=2,
                                                                                                        recipients_ids=[3],
                                                                                                        body='message 2').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=3,
                                                                                                        recipients_ids=[1, 2],
                                                                                                        body='message 3').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        now = datetime.datetime.now()

        time_1 = now - datetime.timedelta(days=2)
        time_2 = now - datetime.timedelta(days=1)
        time_3 = now

        await db.sql("UPDATE messages SET created_at=%(time)s WHERE body='message 1'", {'time': time_1})
        await db.sql("UPDATE messages SET created_at=%(time)s WHERE body='message 2'", {'time': time_2})
        await db.sql("UPDATE messages SET created_at=%(time)s WHERE body='message 3'", {'time': time_3})

        return time_2

    @test_utils.unittest_run_loop
    async def test_remove__all(self):
        barrier = await self.prepair_data()

        request = await self.client.post('/remove-old-messages', data=personal_messages_pb2.RemoveOldMessagesRequest(accounts_ids=[1, 2, 3],
                                                                                                                     barrier=barrier.timestamp()+1).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.RemoveOldMessagesResponse)

        result = await db.sql('SELECT body FROM messages')
        self.assertEqual({row['body'] for row in result},
                         {'message 3'})

    @test_utils.unittest_run_loop
    async def test_remove(self):
        barrier = await self.prepair_data()

        request = await self.client.post('/remove-old-messages', data=personal_messages_pb2.RemoveOldMessagesRequest(accounts_ids=[1, 3],
                                                                                                                     barrier=barrier.timestamp()+1).SerializeToString())
        await self.check_answer(request, personal_messages_pb2.RemoveOldMessagesResponse)

        result = await db.sql('SELECT body FROM messages')
        self.assertEqual({row['body'] for row in result},
                         {'message 2', 'message 3'})


class GetMessagesTests(Mixin, helpers.BaseTests):

    async def prepair_data(self):
        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=1,
                                                                                                        recipients_ids=[2, 3],
                                                                                                        body='a message 1').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=2,
                                                                                                        recipients_ids=[3],
                                                                                                        body='a message 2').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=3,
                                                                                                        recipients_ids=[1, 2],
                                                                                                        body='b message 3').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=1,
                                                                                                        recipients_ids=[2, 4],
                                                                                                        body='b message 4').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

    @test_utils.unittest_run_loop
    async def test_no_messages(self):
        await self.prepair_data()
        request = await self.client.post('/get-messages', data=personal_messages_pb2.GetMessagesRequest(account_id=666,
                                                                                                        type=relations.OWNER_TYPE.random().protocol_value,
                                                                                                        text=None,
                                                                                                        offset=None,
                                                                                                        limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetMessagesResponse)

        self.assertEqual(data.total, 0)
        self.assertEqual(list(data.messages), [])

    @test_utils.unittest_run_loop
    async def test_sender_type(self):
        await self.prepair_data()
        request = await self.client.post('/get-messages', data=personal_messages_pb2.GetMessagesRequest(account_id=1,
                                                                                                        type=relations.OWNER_TYPE.SENDER.protocol_value,
                                                                                                        text=None,
                                                                                                        offset=None,
                                                                                                        limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetMessagesResponse)

        self.assertEqual(data.total, 2)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 4', 'message 1']))

    @test_utils.unittest_run_loop
    async def test_recipient_type(self):
        await self.prepair_data()
        request = await self.client.post('/get-messages', data=personal_messages_pb2.GetMessagesRequest(account_id=2,
                                                                                                        type=relations.OWNER_TYPE.RECIPIENT.protocol_value,
                                                                                                        text=None,
                                                                                                        offset=None,
                                                                                                        limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetMessagesResponse)

        self.assertEqual(data.total, 3)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 4', 'message 3', 'message 1']))

    @test_utils.unittest_run_loop
    async def test_text_filter__single(self):
        await self.prepair_data()
        request = await self.client.post('/get-messages', data=personal_messages_pb2.GetMessagesRequest(account_id=2,
                                                                                                        type=relations.OWNER_TYPE.RECIPIENT.protocol_value,
                                                                                                        text='3',
                                                                                                        offset=None,
                                                                                                        limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetMessagesResponse)

        self.assertEqual(data.total, 1)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 3']))

    @test_utils.unittest_run_loop
    async def test_text_filter__multiple(self):
        await self.prepair_data()
        request = await self.client.post('/get-messages', data=personal_messages_pb2.GetMessagesRequest(account_id=2,
                                                                                                        type=relations.OWNER_TYPE.RECIPIENT.protocol_value,
                                                                                                        text='b message',
                                                                                                        offset=None,
                                                                                                        limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetMessagesResponse)

        self.assertEqual(data.total, 2)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 4', 'message 3']))

    @test_utils.unittest_run_loop
    async def test_offset(self):
        await self.prepair_data()
        request = await self.client.post('/get-messages', data=personal_messages_pb2.GetMessagesRequest(account_id=2,
                                                                                                        type=relations.OWNER_TYPE.RECIPIENT.protocol_value,
                                                                                                        text=None,
                                                                                                        offset=1,
                                                                                                        limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetMessagesResponse)

        self.assertEqual(data.total, 3)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 3', 'message 1']))

    @test_utils.unittest_run_loop
    async def test_limit(self):
        await self.prepair_data()
        request = await self.client.post('/get-messages', data=personal_messages_pb2.GetMessagesRequest(account_id=2,
                                                                                                        type=relations.OWNER_TYPE.RECIPIENT.protocol_value,
                                                                                                        text=None,
                                                                                                        offset=None,
                                                                                                        limit=2).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetMessagesResponse)

        self.assertEqual(data.total, 3)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 4', 'message 3']))


class GetConversationTests(Mixin, helpers.BaseTests):

    async def prepair_data(self):
        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=1,
                                                                                                        recipients_ids=[2, 3],
                                                                                                        body='a message 1').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=2,
                                                                                                        recipients_ids=[3],
                                                                                                        body='a message 2').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=3,
                                                                                                        recipients_ids=[1, 2],
                                                                                                        body='b message 3').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=2,
                                                                                                        recipients_ids=[1, 4],
                                                                                                        body='b message 4').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=1,
                                                                                                        recipients_ids=[2, 4],
                                                                                                        body='b message 5').SerializeToString())
        await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

    @test_utils.unittest_run_loop
    async def test_no_messages(self):
        await self.prepair_data()
        request = await self.client.post('/get-conversation', data=personal_messages_pb2.GetConversationRequest(account_id=666,
                                                                                                                partner_id=1,
                                                                                                                text=None,
                                                                                                                offset=None,
                                                                                                                limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetConversationResponse)

        self.assertEqual(data.total, 0)
        self.assertEqual(list(data.messages), [])

    @test_utils.unittest_run_loop
    async def test_reversed(self):
        await self.prepair_data()
        request = await self.client.post('/get-conversation', data=personal_messages_pb2.GetConversationRequest(account_id=1,
                                                                                                                partner_id=2,
                                                                                                                text=None,
                                                                                                                offset=None,
                                                                                                                limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetConversationResponse)

        self.assertEqual(data.total, 3)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 5', 'message 4', 'message 1']))

        request = await self.client.post('/get-conversation', data=personal_messages_pb2.GetConversationRequest(account_id=2,
                                                                                                                partner_id=1,
                                                                                                                text=None,
                                                                                                                offset=None,
                                                                                                                limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetConversationResponse)

        self.assertEqual(data.total, 3)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 5', 'message 4', 'message 1']))

    @test_utils.unittest_run_loop
    async def test_text_filter__single(self):
        await self.prepair_data()
        request = await self.client.post('/get-conversation', data=personal_messages_pb2.GetConversationRequest(account_id=2,
                                                                                                                partner_id=1,
                                                                                                                text='4',
                                                                                                                offset=None,
                                                                                                                limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetConversationResponse)

        self.assertEqual(data.total, 1)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 4']))

    @test_utils.unittest_run_loop
    async def test_text_filter__multiple(self):
        await self.prepair_data()
        request = await self.client.post('/get-conversation', data=personal_messages_pb2.GetConversationRequest(account_id=2,
                                                                                                                partner_id=1,
                                                                                                                text='b message',
                                                                                                                offset=None,
                                                                                                                limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetConversationResponse)

        self.assertEqual(data.total, 2)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 5', 'message 4']))

    @test_utils.unittest_run_loop
    async def test_offset(self):
        await self.prepair_data()
        request = await self.client.post('/get-conversation', data=personal_messages_pb2.GetConversationRequest(account_id=2,
                                                                                                                partner_id=1,
                                                                                                                text=None,
                                                                                                                offset=1,
                                                                                                                limit=None).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetConversationResponse)

        self.assertEqual(data.total, 3)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 4', 'message 1']))

    @test_utils.unittest_run_loop
    async def test_limit(self):
        await self.prepair_data()
        request = await self.client.post('/get-conversation', data=personal_messages_pb2.GetConversationRequest(account_id=2,
                                                                                                                partner_id=1,
                                                                                                                text=None,
                                                                                                                offset=None,
                                                                                                                limit=2).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetConversationResponse)

        self.assertEqual(data.total, 3)
        self.assertEqual(list(data.messages), await load_protocol_messages_by_bodies(['message 5', 'message 4']))


class GetMessageTests(Mixin, helpers.BaseTests):

    async def prepair_data(self):
        request = await self.client.post('/send-message', data=personal_messages_pb2.SendMessageRequest(sender_id=1,
                                                                                                        recipients_ids=[2],
                                                                                                        body='a message 1').SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.SendMessageResponse)

        self.message_id = data.message_id

    @test_utils.unittest_run_loop
    async def test_sender(self):
        await self.prepair_data()

        request = await self.client.post('/get-message', data=personal_messages_pb2.GetMessageRequest(account_id=1, message_id=self.message_id).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetMessageResponse)

        self.assertEqual(data.message.body, 'a message 1')

    @test_utils.unittest_run_loop
    async def test_recipient(self):
        await self.prepair_data()

        request = await self.client.post('/get-message', data=personal_messages_pb2.GetMessageRequest(account_id=2, message_id=self.message_id).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetMessageResponse)

        self.assertEqual(data.message.body, 'a message 1')

    @test_utils.unittest_run_loop
    async def test_no_relation(self):
        await self.prepair_data()

        request = await self.client.post('/get-message', data=personal_messages_pb2.GetMessageRequest(account_id=3, message_id=self.message_id).SerializeToString())
        data = await self.check_answer(request, personal_messages_pb2.GetMessageResponse)

        self.assertFalse(data.HasField('message'))


class DataProtectionCollectDataTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_wrong_secret(self):
        secret = 'wrong.secret'

        request = await self.client.post('/data-protection-collect-data',
                                         data=data_protector_pb2.PluginReportRequest(account_id='777',
                                                                                      secret=secret).SerializeToString())
        await self.check_error(request, 'personal_messages.data_protection_collect_data.wrong_secret')

    @test_utils.unittest_run_loop
    async def test_no_data(self):

        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-collect-data',
                                         data=data_protector_pb2.PluginReportRequest(account_id='777',
                                                                                      secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginReportResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginReportResponse.ResultType.Value('SUCCESS'))

        report = s11n.from_json(response.data)

        self.assertEqual(report, [])

    @test_utils.unittest_run_loop
    async def test_has_data(self):
        # prepair data
        message_1_id = await operations.send_message(sender_id=1, recipients_ids=[2, 3, 4], body='1')
        message_2_id = await operations.send_message(sender_id=2, recipients_ids=[3, 4, 5], body='2')
        message_3_id = await operations.send_message(sender_id=3, recipients_ids=[4, 5, 6], body='3')
        message_4_id = await operations.send_message(sender_id=4, recipients_ids=[2], body='4')

        messages_ids = [message_1_id, message_2_id, message_3_id, message_4_id]

        for message_id, account_id in [(messages_ids[0], 1),
                                       (messages_ids[0], 2),
                                       (messages_ids[0], 3),
                                       (messages_ids[0], 4),

                                       (messages_ids[1], 2),

                                       (messages_ids[2], 4),
                                       (messages_ids[2], 5),
                                       (messages_ids[2], 6),

                                       (messages_ids[3], 4),
                                       (messages_ids[3], 2)]:
            await operations.hide_message(account_id, message_id)

        removed_messages_ids = await operations.candidates_to_remove_ids()
        self.assertNotEqual(removed_messages_ids, [])
        await operations.remove_messages(removed_messages_ids)

        messages = []

        test_account_id = 3

        for message_id in messages_ids:
            message = await operations.load_message(test_account_id, message_id, visibility=None)
            messages.append(message)

        # request data

        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-collect-data',
                                         data=data_protector_pb2.PluginReportRequest(account_id=str(test_account_id),
                                                                                      secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginReportResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginReportResponse.ResultType.Value('SUCCESS'))

        report = s11n.from_json(response.data)

        self.assertCountEqual(report, [['message', messages[message_index].data_of(test_account_id)]
                                       for message_index in [1, 2]])


class DataProtectionDeleteDataTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_wrong_secret(self):
        secret = 'wrong.secret'

        request = await self.client.post('/data-protection-delete-data',
                                         data=data_protector_pb2.PluginDeletionRequest(account_id='777',
                                                                                       secret=secret).SerializeToString())
        await self.check_error(request, 'personal_messages.data_protection_delete_data.wrong_secret')

    @test_utils.unittest_run_loop
    async def test_no_data(self):

        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-delete-data',
                                         data=data_protector_pb2.PluginDeletionRequest(account_id='777',
                                                                                       secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginDeletionResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginDeletionResponse.ResultType.Value('SUCCESS'))


    @test_utils.unittest_run_loop
    async def test_has_data(self):
        # prepair data
        message_1_id = await operations.send_message(sender_id=1, recipients_ids=[2, 3, 4], body='1')
        message_2_id = await operations.send_message(sender_id=2, recipients_ids=[3, 4, 5], body='2')
        message_3_id = await operations.send_message(sender_id=3, recipients_ids=[4, 5, 6], body='3')
        message_4_id = await operations.send_message(sender_id=4, recipients_ids=[2], body='4')

        messages_ids = [message_1_id, message_2_id, message_3_id, message_4_id]

        for message_id, account_id in [(messages_ids[0], 1),
                                       (messages_ids[0], 2),
                                       (messages_ids[0], 3),
                                       (messages_ids[0], 4),

                                       (messages_ids[1], 2),

                                       (messages_ids[2], 4),
                                       (messages_ids[2], 5),
                                       (messages_ids[2], 6),

                                       (messages_ids[3], 4),
                                       (messages_ids[3], 2)]:
            await operations.hide_message(account_id, message_id)

        removed_messages_ids = await operations.candidates_to_remove_ids()
        self.assertNotEqual(removed_messages_ids, [])
        await operations.remove_messages(removed_messages_ids)

        test_account_id = 3

        # request data

        secret = helpers.get_config()['custom']['data_protector']['secret']

        request = await self.client.post('/data-protection-delete-data',
                                         data=data_protector_pb2.PluginDeletionRequest(account_id=str(test_account_id),
                                                                                       secret=secret).SerializeToString())
        response = await self.check_success(request, data_protector_pb2.PluginDeletionResponse, raw=True)

        self.assertEqual(response.result, data_protector_pb2.PluginDeletionResponse.ResultType.Value('SUCCESS'))

        removed_messages_ids = await operations.candidates_to_remove_ids()

        self.assertCountEqual(removed_messages_ids, [messages_ids[2]])
