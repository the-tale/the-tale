
import asyncio

from aiohttp import test_utils

from tt_protocol.protocol import diary_pb2

from tt_diary import utils
from tt_diary import objects
from tt_diary import exceptions
from tt_diary import operations
from tt_diary import protobuf

from . import helpers


class HandlersTestsMixin(object):

    def create_message(self, uid):
        return objects.Message(timestamp=uid,
                               turn_number=100 + uid,
                               type=1000 + uid,
                               game_time='time {}'.format(uid),
                               game_date='date {}'.format(uid),
                               position='position {}'.format(uid),
                               message='message {}'.format(uid),
                               variables={'x': 'y', 'uid': str(uid)})



class VersionHandlerTests(helpers.BaseTests, HandlersTestsMixin):

    @test_utils.unittest_run_loop
    async def test_version__not_exists(self):
        request = await self.client.post('/version', data=diary_pb2.VersionRequest(account_id=1).SerializeToString())

        data = await self.check_answer(request, diary_pb2.VersionResponse)

        self.assertEqual(data.version, 0)


    @test_utils.unittest_run_loop
    async def test_version(self):
        request = await self.client.post('/push-message', data=diary_pb2.PushMessageRequest(account_id=1, message=diary_pb2.Message(), diary_size=100).SerializeToString())
        await self.check_answer(request, diary_pb2.PushMessageResponse)

        request = await self.client.post('/version', data=diary_pb2.VersionRequest(account_id=1).SerializeToString())
        data = await self.check_answer(request, diary_pb2.VersionResponse)

        self.assertGreater(data.version, 0)


    @test_utils.unittest_run_loop
    async def test_version__update(self):
        request = await self.client.post('/push-message', data=diary_pb2.PushMessageRequest(account_id=1, message=diary_pb2.Message(), diary_size=100).SerializeToString())
        await self.check_answer(request, diary_pb2.PushMessageResponse)

        request = await self.client.post('/version', data=diary_pb2.VersionRequest(account_id=1).SerializeToString())
        data_1 = await self.check_answer(request, diary_pb2.VersionResponse)

        request = await self.client.post('/push-message', data=diary_pb2.PushMessageRequest(account_id=1, message=diary_pb2.Message(), diary_size=100).SerializeToString())
        await self.check_answer(request, diary_pb2.PushMessageResponse)

        request = await self.client.post('/version', data=diary_pb2.VersionRequest(account_id=1).SerializeToString())
        data_2 = await self.check_answer(request, diary_pb2.VersionResponse)

        self.assertGreater(data_2.version, data_1.version)


class PushMessageTests(helpers.BaseTests, HandlersTestsMixin):

    @test_utils.unittest_run_loop
    async def test_first_message(self):
        message = self.create_message(1)
        request = await self.client.post('/push-message', data=diary_pb2.PushMessageRequest(account_id=1, message=protobuf.from_message(message), diary_size=100).SerializeToString())
        await self.check_answer(request, diary_pb2.PushMessageResponse)

        diary = await operations.load_diary(1)

        self.assertEqual(list(diary.messages()), [message])


    @test_utils.unittest_run_loop
    async def test_second_message(self):
        message_1 = self.create_message(1)
        request = await self.client.post('/push-message', data=diary_pb2.PushMessageRequest(account_id=1, message=protobuf.from_message(message_1), diary_size=100).SerializeToString())
        await self.check_answer(request, diary_pb2.PushMessageResponse)

        message_2 = self.create_message(2)
        request = await self.client.post('/push-message', data=diary_pb2.PushMessageRequest(account_id=1, message=protobuf.from_message(message_2), diary_size=100).SerializeToString())
        await self.check_answer(request, diary_pb2.PushMessageResponse)

        diary = await operations.load_diary(1)

        self.assertEqual(list(diary.messages()), [message_1, message_2])


    @test_utils.unittest_run_loop
    async def test_message_overflow(self):
        messages = []

        for i in range(21):
            message = self.create_message(i)
            request = await self.client.post('/push-message', data=diary_pb2.PushMessageRequest(account_id=1, message=protobuf.from_message(message), diary_size=20).SerializeToString())
            await self.check_answer(request, diary_pb2.PushMessageResponse)
            await request.release()
            messages.append(message)

        diary = await operations.load_diary(1)

        self.assertEqual(list(diary.messages()), messages[1:])


class DiaryTests(helpers.BaseTests, HandlersTestsMixin):

    @test_utils.unittest_run_loop
    async def test_no_diary(self):
        request = await self.client.post('/diary', data=diary_pb2.DiaryRequest(account_id=1).SerializeToString())
        data = await self.check_answer(request, diary_pb2.DiaryResponse)
        self.assertEqual(data.diary, protobuf.from_diary(objects.Diary()))


    @test_utils.unittest_run_loop
    async def test_has_diary(self):
        for i in range(21):
            message = self.create_message(i)
            request = await self.client.post('/push-message', data=diary_pb2.PushMessageRequest(account_id=1, message=protobuf.from_message(message), diary_size=20).SerializeToString())
            await self.check_answer(request, diary_pb2.PushMessageResponse)
            await request.release()

        diary = await operations.load_diary(1)

        request = await self.client.post('/diary', data=diary_pb2.DiaryRequest(account_id=1).SerializeToString())
        data = await self.check_answer(request, diary_pb2.DiaryResponse)
        self.assertEqual(data.diary, protobuf.from_diary(diary))
