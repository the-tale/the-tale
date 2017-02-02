
import time
import asyncio

from aiohttp import test_utils

from tt_web import utils
from tt_web import postgresql as db

from .. import objects
from .. import relations
from .. import operations

from . import helpers


class OperationsTests(helpers.BaseTests):

    async def check_account_created(self, number=1, id=666, new_messages_number=0, contacts=[]):
        result = await db.sql('SELECT * FROM accounts ORDER BY created_at DESC')

        self.assertEqual(len(result), number)
        self.assertEqual(result[0]['id'], id)
        self.assertEqual(result[0]['new_messages_number'], new_messages_number)


    @test_utils.unittest_run_loop
    async def test_increment_new_messages(self):
        await operations.increment_new_messages(666)
        await self.check_account_created(new_messages_number=1)

        await operations.increment_new_messages(666)
        await operations.increment_new_messages(666)
        await self.check_account_created(new_messages_number=3)


    @test_utils.unittest_run_loop
    async def test_new_messages_number__has_account(self):
        await operations.increment_new_messages(666)

        await db.sql('UPDATE accounts SET new_messages_number=7')

        number = await operations.new_messages_number(666)

        self.assertEqual(number, 7)


    @test_utils.unittest_run_loop
    async def test_new_messages_number__no_account(self):
        number = await operations.new_messages_number(666)

        self.assertEqual(number, 0)


    @test_utils.unittest_run_loop
    async def test_read_messages__has_account(self):
        await operations.increment_new_messages(666)

        await db.sql('UPDATE accounts SET new_messages_number=7')

        await operations.read_messages(666)

        number = await operations.new_messages_number(666)

        self.assertEqual(number, 0)


    @test_utils.unittest_run_loop
    async def test_read_messages__no_account(self):
        await operations.read_messages(666)

        number = await operations.new_messages_number(666)

        self.assertEqual(number, 0)


    @test_utils.unittest_run_loop
    async def test_create_visibility(self):
        message_1_id = await operations.create_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')
        message_2_id = await operations.create_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')

        await operations.create_visibility(1, message_1_id)
        await operations.create_visibility(2, message_2_id)

        result = await db.sql('SELECT account, message FROM visibilities')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account': 1, 'message': message_1_id},
                               {'account': 2, 'message': message_2_id}])



    @test_utils.unittest_run_loop
    async def test_add_to_conversation(self):
        message_1_id = await operations.create_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')
        message_2_id = await operations.create_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')

        await operations.add_to_conversation(1, 2, message_1_id)
        await operations.add_to_conversation(2, 1, message_2_id)

        result = await db.sql('SELECT account_1, account_2, message FROM conversations')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account_1': 1, 'account_2': 2, 'message': message_1_id},
                               {'account_1': 1, 'account_2': 2, 'message': message_2_id}])


    @test_utils.unittest_run_loop
    async def test_create_message(self):
        message_id = await operations.create_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')

        result = await db.sql('SELECT * FROM messages')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['sender'], 666)
        self.assertEqual(result[0]['recipients'], [1, 3, 7])
        self.assertEqual(result[0]['body'], 'some странный text')


    @test_utils.unittest_run_loop
    async def test_send_message__visibilities_created(self):
        message_id = await operations.send_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')

        result = await db.sql('SELECT account, message, visible FROM visibilities')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account': 666, 'message': message_id, 'visible': True},
                               {'account': 1, 'message': message_id, 'visible': True},
                               {'account': 3, 'message': message_id, 'visible': True},
                               {'account': 7, 'message': message_id, 'visible': True}])


    @test_utils.unittest_run_loop
    async def test_send_message__conversations_created(self):
        message_id = await operations.send_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')

        result = await db.sql('SELECT account_1, account_2, message FROM conversations')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account_1': 1, 'account_2': 666, 'message': message_id},
                               {'account_1': 3, 'account_2': 666, 'message': message_id},
                               {'account_1': 7, 'account_2': 666, 'message': message_id}])


    @test_utils.unittest_run_loop
    async def test_send_message__new_messages_increment(self):
        await operations.send_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')
        await operations.send_message(sender_id=1, recipients_ids=[7], body='some странный text')

        result = await db.sql('SELECT id, new_messages_number FROM accounts')

        self.assertCountEqual([dict(row) for row in result],
                              [{'id': 1, 'new_messages_number': 1},
                               {'id': 3, 'new_messages_number': 1},
                               {'id': 7, 'new_messages_number': 2}])


    @test_utils.unittest_run_loop
    async def test_send_message__contacts_created(self):
        message_id = await operations.send_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')

        contacts = await operations.get_contacts(666)
        self.assertCountEqual(contacts, [1, 3, 7])

        contacts = await operations.get_contacts(3)
        self.assertCountEqual(contacts, [666])


    @test_utils.unittest_run_loop
    async def test_send_message__duplicate_recipients(self):
        message_id = await operations.send_message(sender_id=666, recipients_ids=[1, 3, 7, 3, 7, 7], body='some странный text')

        result = await db.sql('SELECT recipients, body FROM messages')
        self.assertEqual([row['body'] for row in result], ['some странный text'])
        self.assertEqual(len(result[0]['recipients']), 3)
        self.assertEqual(set(result[0]['recipients']), {1, 3, 7})


    @test_utils.unittest_run_loop
    async def test_send_message__sender_is_recipient(self):
        message_id = await operations.send_message(sender_id=666, recipients_ids=[666], body='some странный text')

        self.assertEqual(message_id, None)

        result = await db.sql('SELECT body FROM messages')
        self.assertEqual(result, [])


    @test_utils.unittest_run_loop
    async def test_send_message__remove_sender_from_recipients(self):
        message_id = await operations.send_message(sender_id=666, recipients_ids=[1, 3, 666, 7], body='some странный text')

        result = await db.sql('SELECT body FROM messages')
        self.assertEqual([row['body'] for row in result], ['some странный text'])

        result = await db.sql('SELECT id FROM accounts')
        self.assertEqual({row['id'] for row in result}, {1, 3, 7})

        result = await db.sql('SELECT recipients FROM messages WHERE id=%(id)s', {'id': message_id})
        self.assertEqual(set(result[0]['recipients']), {1, 3, 7})

        result = await db.sql('SELECT account, message, visible FROM visibilities')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account': 666, 'message': message_id, 'visible': True},
                               {'account': 1, 'message': message_id, 'visible': True},
                               {'account': 3, 'message': message_id, 'visible': True},
                               {'account': 7, 'message': message_id, 'visible': True}])

        result = await db.sql('SELECT account_1, account_2, message FROM conversations')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account_1': 1, 'account_2': 666, 'message': message_id},
                               {'account_1': 3, 'account_2': 666, 'message': message_id},
                               {'account_1': 7, 'account_2': 666, 'message': message_id}])

        contacts = await operations.get_contacts(666)
        self.assertCountEqual(contacts, [1, 3, 7])

        contacts = await operations.get_contacts(3)
        self.assertCountEqual(contacts, [666])



    @test_utils.unittest_run_loop
    async def test_send_message__duplicate_contacts(self):
        await operations.send_message(sender_id=666, recipients_ids=[1, 3, 7], body='1')
        await operations.send_message(sender_id=3, recipients_ids=[1, 666], body='2')

        contacts = await operations.get_contacts(666)
        self.assertCountEqual(contacts, [1, 3, 7])

        contacts = await operations.get_contacts(1)
        self.assertCountEqual(contacts, [3, 666])

        contacts = await operations.get_contacts(3)
        self.assertCountEqual(contacts, [1, 666])

        contacts = await operations.get_contacts(7)
        self.assertCountEqual(contacts, [666])


    @test_utils.unittest_run_loop
    async def test_hide_message(self):
        message_id = await operations.send_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')
        await operations.hide_message(666, message_id)
        await operations.hide_message(3, message_id)

        result = await db.sql('SELECT account, message, visible FROM visibilities')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account': 666, 'message': message_id, 'visible': False},
                               {'account': 1, 'message': message_id, 'visible': True},
                               {'account': 3, 'message': message_id, 'visible': False},
                               {'account': 7, 'message': message_id, 'visible': True}])


    @test_utils.unittest_run_loop
    async def test_hide_all_messages(self):
        message_1_id = await operations.send_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')
        message_2_id = await operations.send_message(sender_id=3, recipients_ids=[1, 666], body='some странный text')

        await operations.hide_all_messages(666)
        await operations.hide_all_messages(1)

        result = await db.sql('SELECT account, message, visible FROM visibilities')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account': 666, 'message': message_1_id, 'visible': False},
                               {'account': 1, 'message': message_1_id, 'visible': False},
                               {'account': 3, 'message': message_1_id, 'visible': True},
                               {'account': 7, 'message': message_1_id, 'visible': True},

                               {'account': 666, 'message': message_2_id, 'visible': False},
                               {'account': 1, 'message': message_2_id, 'visible': False},
                               {'account': 3, 'message': message_2_id, 'visible': True}])


    @test_utils.unittest_run_loop
    async def test_hide_conversation(self):
        message_1_id = await operations.send_message(sender_id=666, recipients_ids=[1, 3, 7], body='some странный text')
        message_2_id = await operations.send_message(sender_id=3, recipients_ids=[1, 666], body='some странный text')
        message_3_id = await operations.send_message(sender_id=666, recipients_ids=[3], body='some странный text')

        await operations.hide_conversation(666, 3)

        result = await db.sql('SELECT account, message, visible FROM visibilities')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account': 666, 'message': message_1_id, 'visible': False},
                               {'account': 1, 'message': message_1_id, 'visible': True},
                               {'account': 3, 'message': message_1_id, 'visible': True},
                               {'account': 7, 'message': message_1_id, 'visible': True},

                               {'account': 666, 'message': message_2_id, 'visible': False},
                               {'account': 1, 'message': message_2_id, 'visible': True},
                               {'account': 3, 'message': message_2_id, 'visible': True},

                               {'account': 666, 'message': message_3_id, 'visible': False},
                               {'account': 3, 'message': message_3_id, 'visible': True} ])

        total, messages = await operations.load_conversation(666, 3)
        self.assertEqual(total, 0)

        total, messages = await operations.load_conversation(3, 666)
        self.assertEqual(total, 3)


    @test_utils.unittest_run_loop
    async def test_remove_old_messages(self):
        message_1_id = await operations.send_message(sender_id=1, recipients_ids=[2, 3, 4], body='1')
        message_2_id = await operations.send_message(sender_id=2, recipients_ids=[3, 4, 5], body='2')
        message_3_id = await operations.send_message(sender_id=3, recipients_ids=[4, 5, 6], body='3')

        result = await db.sql('SELECT created_at FROM messages WHERE id=%(id)s', {'id': message_2_id})

        await operations.remove_old_messages(accounts_ids=[1, 2, 3], barrier=result[0]['created_at'])

        result = await db.sql('SELECT count(*) FROM messages')

        result = await db.sql('SELECT sender FROM messages')
        self.assertEqual({row['sender'] for row in result}, {2, 3})

        result = await db.sql('SELECT account, message FROM visibilities')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account': 2, 'message': message_2_id},
                               {'account': 3, 'message': message_2_id},
                               {'account': 4, 'message': message_2_id},
                               {'account': 5, 'message': message_2_id},

                               {'account': 3, 'message': message_3_id},
                               {'account': 4, 'message': message_3_id},
                               {'account': 5, 'message': message_3_id},
                               {'account': 6, 'message': message_3_id}])

        result = await db.sql('SELECT account_1, account_2, message FROM conversations')

        self.assertCountEqual([dict(row) for row in result],
                              [{'account_1': 2, 'account_2': 3, 'message': message_2_id},
                               {'account_1': 2, 'account_2': 4, 'message': message_2_id},
                               {'account_1': 2, 'account_2': 5, 'message': message_2_id},

                               {'account_1': 3, 'account_2': 4, 'message': message_3_id},
                               {'account_1': 3, 'account_2': 5, 'message': message_3_id},
                               {'account_1': 3, 'account_2': 6, 'message': message_3_id}])


class LoadMessagesTests(helpers.BaseTests):

    async def fill_database(self):
        self.messages_ids = [await operations.send_message(sender_id=1, recipients_ids=[2, 3], body='1 ааа'),
                             await operations.send_message(sender_id=2, recipients_ids=[1, 3], body='2 ббб'),
                             await operations.send_message(sender_id=1, recipients_ids=[2, 4], body='3 ссс'),
                             await operations.send_message(sender_id=2, recipients_ids=[1, 4], body='4 ааа'),
                             await operations.send_message(sender_id=1, recipients_ids=[3, 4], body='5 ббб'),
                             await operations.send_message(sender_id=2, recipients_ids=[3, 4], body='6 ссс'),
                             await operations.send_message(sender_id=1, recipients_ids=[5], body='7 ааа'),
                             await operations.send_message(sender_id=2, recipients_ids=[5], body='8 ббб'),
                             await operations.send_message(sender_id=1, recipients_ids=[5], body='9 ссс')]


    @test_utils.unittest_run_loop
    async def test_no_messages(self):
        await self.fill_database()
        total, messages = await operations.load_messages(666, relations.OWNER_TYPE.random())
        self.assertEqual(total, 0)
        self.assertEqual(messages, [])


    @test_utils.unittest_run_loop
    async def test_account_and_type(self):
        await self.fill_database()

        total, messages = await operations.load_messages(1, relations.OWNER_TYPE.SENDER)
        self.assertEqual(total, 5)
        self.assertEqual({m.id for m in messages}, set(self.messages_ids[0:9:2]))

        total, messages = await operations.load_messages(1, relations.OWNER_TYPE.RECIPIENT)
        self.assertEqual(total, 2)
        self.assertEqual({m.id for m in messages}, {self.messages_ids[1], self.messages_ids[3]})

        total, messages = await operations.load_messages(2, relations.OWNER_TYPE.SENDER)
        self.assertEqual(total, 4)
        self.assertEqual({m.id for m in messages}, set(self.messages_ids[1:9:2]))

        total, messages = await operations.load_messages(2, relations.OWNER_TYPE.RECIPIENT)
        self.assertEqual(total, 2)
        self.assertEqual({m.id for m in messages}, {self.messages_ids[0], self.messages_ids[2]})


    @test_utils.unittest_run_loop
    async def test_order(self):
        await self.fill_database()

        total, messages = await operations.load_messages(1, relations.OWNER_TYPE.SENDER)
        self.assertEqual(total, 5)
        self.assertEqual([m.id for m in messages], [m_id for m_id in reversed(self.messages_ids[0:9:2])])


    @test_utils.unittest_run_loop
    async def test_text(self):
        await self.fill_database()

        total, messages = await operations.load_messages(1, relations.OWNER_TYPE.SENDER, text='ааа')
        self.assertEqual(total, 2)
        self.assertEqual({m.id for m in messages}, {self.messages_ids[0], self.messages_ids[6]})

        total, messages = await operations.load_messages(1, relations.OWNER_TYPE.RECIPIENT, text='ааа')
        self.assertEqual(total, 1)
        self.assertEqual({m.id for m in messages}, {self.messages_ids[3]})


    @test_utils.unittest_run_loop
    async def test_offset(self):
        await self.fill_database()

        total, messages = await operations.load_messages(1, relations.OWNER_TYPE.SENDER, offset=1)
        self.assertEqual(total, 5)
        self.assertEqual({m.id for m in messages}, set(self.messages_ids[0:8:2])) # does not include last record


    @test_utils.unittest_run_loop
    async def test_limit(self):
        await self.fill_database()

        total, messages = await operations.load_messages(1, relations.OWNER_TYPE.SENDER, limit=2)
        self.assertEqual(total, 5)
        self.assertEqual({m.id for m in messages}, set(self.messages_ids[6:9:2]))


    @test_utils.unittest_run_loop
    async def test_offset_and_limit(self):
        await self.fill_database()

        total, messages = await operations.load_messages(1, relations.OWNER_TYPE.SENDER, offset=1, limit=2)
        self.assertEqual(total, 5)
        self.assertEqual({m.id for m in messages}, set(self.messages_ids[4:7:2]))



class LoadConversationTests(helpers.BaseTests):

    async def fill_database(self):
        self.messages_ids = [await operations.send_message(sender_id=1, recipients_ids=[2, 3], body='1 ааа'),
                             await operations.send_message(sender_id=2, recipients_ids=[1, 3], body='2 ббб'),
                             await operations.send_message(sender_id=1, recipients_ids=[2, 4], body='3 ссс'),
                             await operations.send_message(sender_id=2, recipients_ids=[1, 4], body='4 ааа'),
                             await operations.send_message(sender_id=1, recipients_ids=[3, 4], body='5 ббб'),
                             await operations.send_message(sender_id=2, recipients_ids=[3, 4], body='6 ссс'),
                             await operations.send_message(sender_id=2, recipients_ids=[5], body='10'),
                             await operations.send_message(sender_id=2, recipients_ids=[5], body='11'),
                             await operations.send_message(sender_id=1, recipients_ids=[5], body='7 ааа'),
                             await operations.send_message(sender_id=2, recipients_ids=[5], body='8 ббб'),
                             await operations.send_message(sender_id=1, recipients_ids=[5], body='9 ссс')]


    # load_conversation(account_id, partner_id, offset=0, limit=None):
    @test_utils.unittest_run_loop
    async def test_no_messages(self):
        await self.fill_database()

        total, messages = await operations.load_conversation(666, 1)
        self.assertEqual(total, 0)
        self.assertEqual(messages, [])

        total, messages = await operations.load_conversation(3, 5)
        self.assertEqual(total, 0)
        self.assertEqual(messages, [])


    @test_utils.unittest_run_loop
    async def test_success(self):
        await self.fill_database()

        total, messages = await operations.load_conversation(1, 5)
        self.assertEqual(total, 2)
        self.assertEqual({m.id for m in messages}, {self.messages_ids[-1], self.messages_ids[-3]})

        total, messages = await operations.load_conversation(5, 1)
        self.assertEqual(total, 2)
        self.assertEqual({m.id for m in messages}, {self.messages_ids[-1], self.messages_ids[-3]})


    @test_utils.unittest_run_loop
    async def test_filter_text(self):
        await self.fill_database()

        total, messages = await operations.load_conversation(1, 2, text='ааа')
        self.assertEqual(total, 2)
        self.assertEqual({m.id for m in messages}, {self.messages_ids[0], self.messages_ids[3]})


    @test_utils.unittest_run_loop
    async def test_success__multiple_recipients(self):
        await self.fill_database()

        total, messages = await operations.load_conversation(2, 3)
        self.assertEqual(total, 2)
        self.assertEqual({m.id for m in messages}, {self.messages_ids[1], self.messages_ids[5]})

        total, messages = await operations.load_conversation(3, 2)
        self.assertEqual(total, 2)
        self.assertEqual({m.id for m in messages}, {self.messages_ids[1], self.messages_ids[5]})


    @test_utils.unittest_run_loop
    async def test_order(self):
        await self.fill_database()

        total, messages = await operations.load_conversation(1, 5)
        self.assertEqual(total, 2)
        self.assertEqual([m.id for m in messages], [self.messages_ids[-1], self.messages_ids[-3]])

        total, messages = await operations.load_conversation(5, 1)
        self.assertEqual(total, 2)
        self.assertEqual([m.id for m in messages], [self.messages_ids[-1], self.messages_ids[-3]])


    @test_utils.unittest_run_loop
    async def test_offset(self):
        await self.fill_database()

        total, messages = await operations.load_conversation(1, 5, offset=1)
        self.assertEqual(total, 2)
        self.assertEqual([m.id for m in messages], [self.messages_ids[-3]])


    @test_utils.unittest_run_loop
    async def test_limit(self):
        await self.fill_database()

        total, messages = await operations.load_conversation(1, 5, limit=1)
        self.assertEqual(total, 2)
        self.assertEqual([m.id for m in messages], [self.messages_ids[-1]])


    @test_utils.unittest_run_loop
    async def test_offset_and_limit(self):
        await self.fill_database()

        total, messages = await operations.load_conversation(2, 5)
        self.assertEqual(total, 3)
        self.assertEqual([m.id for m in messages], [self.messages_ids[-2], self.messages_ids[-4], self.messages_ids[-5]])

        total, messages = await operations.load_conversation(2, 5, offset=1, limit=1)
        self.assertEqual(total, 3)
        self.assertEqual([m.id for m in messages], [self.messages_ids[-4]])


class LoadMessageTests(helpers.BaseTests):

    async def fill_database(self):
        self.messages_ids = [await operations.send_message(sender_id=1, recipients_ids=[2], body='1 ааа')]


    @test_utils.unittest_run_loop
    async def test_sender(self):
        await self.fill_database()
        message = await operations.load_message(1, self.messages_ids[0])
        self.assertEqual(message.body, '1 ааа')


    @test_utils.unittest_run_loop
    async def test_recipient(self):
        await self.fill_database()
        message = await operations.load_message(2, self.messages_ids[0])
        self.assertEqual(message.body, '1 ааа')


    @test_utils.unittest_run_loop
    async def test_no_relation(self):
        await self.fill_database()
        message = await operations.load_message(3, self.messages_ids[0])
        self.assertEqual(message, None)
