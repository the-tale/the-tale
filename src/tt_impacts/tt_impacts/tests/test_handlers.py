
from aiohttp import test_utils

from tt_protocol.protocol import impacts_pb2

from tt_web import postgresql as db

from .. import objects
from .. import protobuf
from .. import operations

from . import helpers


class AddImpactsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        impacts = [helpers.test_impact(),
                   helpers.test_impact(),
                   helpers.test_impact()]

        request_impacts = [protobuf.from_impact(impact) for impact in impacts]

        request = await self.client.post('/add-impacts', data=impacts_pb2.AddImpactsRequest(impacts=request_impacts).SerializeToString())
        await self.check_success(request, impacts_pb2.AddImpactsResponse)

        created_impacts = await operations.last_impacts(limit=100)

        for impact, created_impact in zip(impacts, created_impacts):
            impact.time = created_impact.time
            self.assertEqual(impact, created_impact)


class GetImpactsHistoryTests(helpers.BaseTests):

    async def prepere_data(self):

        impacts = [helpers.test_impact(actor_type=1, actor_id=10, target_type=100, target_id=1000),
                   helpers.test_impact(actor_type=1, actor_id=10, target_type=200, target_id=1000),
                   helpers.test_impact(actor_type=1, actor_id=10, target_type=100, target_id=2000),

                   helpers.test_impact(actor_type=2, actor_id=10, target_type=100, target_id=1000),
                   helpers.test_impact(actor_type=1, actor_id=20, target_type=100, target_id=1000),

                   helpers.test_impact(actor_type=1, actor_id=10, target_type=100, target_id=1000),
                   helpers.test_impact(actor_type=1, actor_id=10, target_type=200, target_id=1000),
                   helpers.test_impact(actor_type=1, actor_id=10, target_type=100, target_id=2000),

                   helpers.test_impact(actor_type=2, actor_id=10, target_type=100, target_id=1000),
                   helpers.test_impact(actor_type=1, actor_id=20, target_type=100, target_id=1000)]

        request_impacts = [protobuf.from_impact(impact) for impact in impacts]

        for impact in request_impacts:
            request = await self.client.post('/add-impacts', data=impacts_pb2.AddImpactsRequest(impacts=[impact]).SerializeToString())
            await self.check_success(request, impacts_pb2.AddImpactsResponse)

        return await operations.last_impacts(limit=100)

    @test_utils.unittest_run_loop
    async def test_last_impacts(self):
        all_impacts = await self.prepere_data()

        data = impacts_pb2.GetImpactsHistoryRequest(filter=impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('NONE'),
                                                    limit=100).SerializeToString()

        request = await self.client.post('/get-impacts-history', data=data)
        answer = await self.check_success(request, impacts_pb2.GetImpactsHistoryResponse)

        self.assertEqual([protobuf.to_impact(impact, use_time=True) for impact in answer.impacts],
                         all_impacts)

    @test_utils.unittest_run_loop
    async def test_last_impacts__limit(self):
        all_impacts = await self.prepere_data()

        data = impacts_pb2.GetImpactsHistoryRequest(filter=impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('NONE'),
                                                    limit=1).SerializeToString()

        request = await self.client.post('/get-impacts-history', data=data)
        answer = await self.check_success(request, impacts_pb2.GetImpactsHistoryResponse)

        self.assertEqual([protobuf.to_impact(impact, use_time=True) for impact in answer.impacts],
                         [all_impacts[0]])

    @test_utils.unittest_run_loop
    async def test_last_actor_impacts(self):
        all_impacts = await self.prepere_data()

        data = impacts_pb2.GetImpactsHistoryRequest(filter=impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('ONLY_ACTOR'),
                                                    actor=impacts_pb2.Object(type=1, id=10),
                                                    limit=100).SerializeToString()

        request = await self.client.post('/get-impacts-history', data=data)
        answer = await self.check_success(request, impacts_pb2.GetImpactsHistoryResponse)

        self.assertEqual([protobuf.to_impact(impact, use_time=True) for impact in answer.impacts],
                         [all_impacts[2],
                          all_impacts[3],
                          all_impacts[4],
                          all_impacts[7],
                          all_impacts[8],
                          all_impacts[9]])

    @test_utils.unittest_run_loop
    async def test_last_actor_impacts__limit(self):
        all_impacts = await self.prepere_data()

        data = impacts_pb2.GetImpactsHistoryRequest(filter=impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('ONLY_ACTOR'),
                                                    actor=impacts_pb2.Object(type=1, id=10),
                                                    limit=2).SerializeToString()

        request = await self.client.post('/get-impacts-history', data=data)
        answer = await self.check_success(request, impacts_pb2.GetImpactsHistoryResponse)

        self.assertEqual([protobuf.to_impact(impact, use_time=True) for impact in answer.impacts],
                         [all_impacts[2],
                          all_impacts[3]])

    @test_utils.unittest_run_loop
    async def test_last_target_impacts(self):
        all_impacts = await self.prepere_data()

        data = impacts_pb2.GetImpactsHistoryRequest(filter=impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('ONLY_TARGET'),
                                                    target=impacts_pb2.Object(type=100, id=1000),
                                                    limit=100).SerializeToString()

        request = await self.client.post('/get-impacts-history', data=data)
        answer = await self.check_success(request, impacts_pb2.GetImpactsHistoryResponse)

        self.assertEqual([protobuf.to_impact(impact, use_time=True) for impact in answer.impacts],
                         [all_impacts[0],
                          all_impacts[1],
                          all_impacts[4],
                          all_impacts[5],
                          all_impacts[6],
                          all_impacts[9]])

    @test_utils.unittest_run_loop
    async def test_last_target_impacts__limit(self):
        all_impacts = await self.prepere_data()

        data = impacts_pb2.GetImpactsHistoryRequest(filter=impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('ONLY_TARGET'),
                                                    target=impacts_pb2.Object(type=100, id=1000),
                                                    limit=3).SerializeToString()

        request = await self.client.post('/get-impacts-history', data=data)
        answer = await self.check_success(request, impacts_pb2.GetImpactsHistoryResponse)

        self.assertEqual([protobuf.to_impact(impact, use_time=True) for impact in answer.impacts],
                         [all_impacts[0],
                          all_impacts[1],
                          all_impacts[4]])

    @test_utils.unittest_run_loop
    async def test_last_actor_targets_impacts(self):
        all_impacts = await self.prepere_data()

        data = impacts_pb2.GetImpactsHistoryRequest(filter=impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('BOTH'),
                                                    actor=impacts_pb2.Object(type=1, id=10),
                                                    target=impacts_pb2.Object(type=100, id=1000),
                                                    limit=100).SerializeToString()

        request = await self.client.post('/get-impacts-history', data=data)
        answer = await self.check_success(request, impacts_pb2.GetImpactsHistoryResponse)

        self.assertEqual([protobuf.to_impact(impact, use_time=True) for impact in answer.impacts],
                         [all_impacts[4],
                          all_impacts[9]])

    @test_utils.unittest_run_loop
    async def test_last_actor_targets_impacts__limit(self):
        all_impacts = await self.prepere_data()

        data = impacts_pb2.GetImpactsHistoryRequest(filter=impacts_pb2.GetImpactsHistoryRequest.FilterType.Value('BOTH'),
                                                    actor=impacts_pb2.Object(type=1, id=10),
                                                    target=impacts_pb2.Object(type=100, id=1000),
                                                    limit=1).SerializeToString()

        request = await self.client.post('/get-impacts-history', data=data)
        answer = await self.check_success(request, impacts_pb2.GetImpactsHistoryResponse)

        self.assertEqual([protobuf.to_impact(impact, use_time=True) for impact in answer.impacts],
                         [all_impacts[4]])


class GetTargetsImpactsTests(helpers.BaseTests):

    async def prepere_data(self):

        impacts = [helpers.test_impact(target_type=1, target_id=10),
                   helpers.test_impact(target_type=1, target_id=20),
                   helpers.test_impact(target_type=2, target_id=10),
                   helpers.test_impact(target_type=2, target_id=30),

                   helpers.test_impact(target_type=1, target_id=10),
                   helpers.test_impact(target_type=1, target_id=20)]

        request_impacts = [protobuf.from_impact(impact) for impact in impacts]

        for impact in request_impacts:
            request = await self.client.post('/add-impacts', data=impacts_pb2.AddImpactsRequest(impacts=[impact]).SerializeToString())
            await self.check_success(request, impacts_pb2.AddImpactsResponse)

        return await operations.last_impacts(limit=100)

    @test_utils.unittest_run_loop
    async def test_success(self):
        all_impacts = await self.prepere_data()

        data = impacts_pb2.GetTargetsImpactsRequest(targets=[impacts_pb2.Object(type=1, id=10),
                                                             impacts_pb2.Object(type=1, id=20),
                                                             impacts_pb2.Object(type=2, id=30)]).SerializeToString()

        request = await self.client.post('/get-targets-impacts', data=data)
        answer = await self.check_success(request, impacts_pb2.GetTargetsImpactsResponse)

        self.assertCountEqual([protobuf.to_target_impact(impact) for impact in answer.impacts],
                              [objects.TargetImpact(target=objects.Object(1,10),
                                                    amount=all_impacts[-1].amount+all_impacts[-5].amount,
                                                    turn=max(all_impacts[-1].turn, all_impacts[-5].turn),
                                                    time=max(all_impacts[-1].time, all_impacts[-5].time)),
                               objects.TargetImpact(target=objects.Object(1, 20),
                                                    amount=all_impacts[-2].amount+all_impacts[-6].amount,
                                                    turn=max(all_impacts[-2].turn, all_impacts[-6].turn),
                                                    time=max(all_impacts[-2].time, all_impacts[-6].time)),
                               objects.TargetImpact(target=objects.Object(2, 30),
                                                    amount=all_impacts[-4].amount,
                                                    turn=all_impacts[-4].turn,
                                                    time=all_impacts[-4].time)])


class GetActorImpactsTests(helpers.BaseTests):

    async def prepair_data(self):
        all_impacts = [helpers.test_impact(actor_type=100, actor_id=1000, target_type=1, target_id=10),
                       helpers.test_impact(actor_type=100, actor_id=2000, target_type=1, target_id=20),
                       helpers.test_impact(actor_type=200, actor_id=1000, target_type=2, target_id=10),
                       helpers.test_impact(actor_type=100, actor_id=1000, target_type=2, target_id=30),
                       helpers.test_impact(actor_type=100, actor_id=1000, target_type=1, target_id=10),
                       helpers.test_impact(actor_type=200, actor_id=2000, target_type=1, target_id=20)]

        request_impacts = [protobuf.from_impact(impact) for impact in all_impacts]

        for impact in request_impacts:
            request = await self.client.post('/add-impacts', data=impacts_pb2.AddImpactsRequest(impacts=[impact]).SerializeToString())
            await self.check_success(request, impacts_pb2.AddImpactsResponse)

        return await operations.last_impacts(limit=100)

    @test_utils.unittest_run_loop
    async def test_no_impacts(self):
        await self.prepair_data()

        data = impacts_pb2.GetActorImpactsRequest(actor=impacts_pb2.Object(type=666, id=1000),
                                                  target_types=[1, 2]).SerializeToString()

        request = await self.client.post('/get-actor-impacts', data=data)
        answer = await self.check_success(request, impacts_pb2.GetActorImpactsResponse)

        self.assertCountEqual([protobuf.to_target_impact(impact) for impact in answer.impacts],
                              [])

    @test_utils.unittest_run_loop
    async def test_has_impacts(self):
        all_impacts = await self.prepair_data()

        data = impacts_pb2.GetActorImpactsRequest(actor=impacts_pb2.Object(type=100, id=1000),
                                                  target_types=[1, 2]).SerializeToString()

        request = await self.client.post('/get-actor-impacts', data=data)
        answer = await self.check_success(request, impacts_pb2.GetActorImpactsResponse)

        self.assertCountEqual([protobuf.to_target_impact(impact) for impact in answer.impacts],
                              [objects.TargetImpact(target=objects.Object(1,10),
                                                    amount=all_impacts[-1].amount+all_impacts[-5].amount,
                                                    turn=max(all_impacts[-1].turn, all_impacts[-5].turn),
                                                    time=max(all_impacts[-1].time, all_impacts[-5].time)),
                               objects.TargetImpact(target=objects.Object(2, 30),
                                                    amount=all_impacts[-4].amount,
                                                    turn=all_impacts[-4].turn,
                                                    time=all_impacts[-4].time)])

    @test_utils.unittest_run_loop
    async def test_has_impacts__filter_target_types(self):
        all_impacts = await self.prepair_data()

        data = impacts_pb2.GetActorImpactsRequest(actor=impacts_pb2.Object(type=100, id=1000),
                                                  target_types=[2]).SerializeToString()

        request = await self.client.post('/get-actor-impacts', data=data)
        answer = await self.check_success(request, impacts_pb2.GetActorImpactsResponse)

        self.assertCountEqual([protobuf.to_target_impact(impact) for impact in answer.impacts],
                              [objects.TargetImpact(target=objects.Object(2, 30),
                                                    amount=all_impacts[-4].amount,
                                                    turn=all_impacts[-4].turn,
                                                    time=all_impacts[-4].time)])


class GetImpactersRatingsTests(helpers.BaseTests):

    async def prepere_data(self):
        impacts = [helpers.test_impact(actor_type=0, actor_id=0, target_type=1, target_id=10),
                   helpers.test_impact(actor_type=0, actor_id=1, target_type=1, target_id=20),
                   helpers.test_impact(actor_type=0, actor_id=2, target_type=1, target_id=20),
                   helpers.test_impact(actor_type=0, actor_id=3, target_type=2, target_id=10),
                   helpers.test_impact(actor_type=0, actor_id=4, target_type=2, target_id=10),
                   helpers.test_impact(actor_type=0, actor_id=5, target_type=2, target_id=10)]

        request_impacts = [protobuf.from_impact(impact) for impact in impacts]

        for impact in request_impacts:
            request = await self.client.post('/add-impacts', data=impacts_pb2.AddImpactsRequest(impacts=[impact]).SerializeToString())
            await self.check_success(request, impacts_pb2.AddImpactsResponse)

    @test_utils.unittest_run_loop
    async def test_success(self):
        await self.prepere_data()

        data = impacts_pb2.GetImpactersRatingsRequest(targets=[impacts_pb2.Object(type=1, id=10),
                                                               impacts_pb2.Object(type=1, id=20),
                                                               impacts_pb2.Object(type=2, id=10),
                                                               impacts_pb2.Object(type=3, id=30)],
                                                      actor_types=[0],
                                                      limit=2).SerializeToString()

        request = await self.client.post('/get-impacters-ratings', data=data)
        answer = await self.check_success(request, impacts_pb2.GetImpactersRatingsResponse)

        self.assertEqual(len(answer.ratings), 4)

        ratings = sorted(answer.ratings, key=lambda rating: (rating.target.type, rating.target.id))

        self.assertEqual(ratings[0].target, impacts_pb2.Object(type=1, id=10))
        self.assertEqual(len(ratings[0].records), 1)

        self.assertEqual(ratings[1].target, impacts_pb2.Object(type=1, id=20))
        self.assertEqual(len(ratings[1].records), 2)

        self.assertEqual(ratings[2].target, impacts_pb2.Object(type=2, id=10))
        self.assertEqual(len(ratings[2].records), 2)  # limit

        self.assertEqual(ratings[3].target, impacts_pb2.Object(type=3, id=30))
        self.assertEqual(len(ratings[3].records), 0)


class ScaleImpactsTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):
        impacts = [helpers.test_impact(target_type=1, amount=100),
                   helpers.test_impact(target_type=2, amount=200),
                   helpers.test_impact(target_type=3, amount=300)]

        request_impacts = [protobuf.from_impact(impact) for impact in impacts]

        for impact in request_impacts:
            request = await self.client.post('/add-impacts', data=impacts_pb2.AddImpactsRequest(impacts=[impact]).SerializeToString())
            await self.check_success(request, impacts_pb2.AddImpactsResponse)

        data = impacts_pb2.ScaleImpactsRequest(target_types=[1, 3], scale=2.5).SerializeToString()

        request = await self.client.post('/scale-impacts', data=data)
        await self.check_success(request, impacts_pb2.ScaleImpactsResponse)

        results = await db.sql('SELECT target_type, amount FROM actors_impacts')
        self.assertCountEqual([dict(row) for row in results],
                              [{'target_type': 1, 'amount': 250},
                               {'target_type': 2, 'amount': 200},
                               {'target_type': 3, 'amount': 750}])

        results = await db.sql('SELECT target_type, amount FROM targets_impacts')
        self.assertCountEqual([dict(row) for row in results],
                              [{'target_type': 1, 'amount': 250},
                               {'target_type': 2, 'amount': 200},
                               {'target_type': 3, 'amount': 750}])
