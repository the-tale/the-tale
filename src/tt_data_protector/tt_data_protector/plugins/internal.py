
import copy
import aiohttp

from tt_protocol.protocol import data_protector_pb2

from tt_web import log
from tt_web import s11n

from .. import relations


class Plugin:
    __slots__ = ('report_url', 'deletion_url', 'secret')

    def __init__(self, report_url, deletion_url, secret):
        self.report_url = report_url
        self.deletion_url = deletion_url
        self.secret = secret

    async def request_report(self, account_id, logger):
        try:
            async with aiohttp.ClientSession() as session:
                data = data_protector_pb2.PluginReportRequest(account_id=account_id,
                                                              secret=self.secret)

                logger.info('request %s', self.report_url)

                async with session.post(self.report_url, data=data.SerializeToString()) as response:
                    logger.info('answer status: %s', response.status)

                    if response.status != 200:
                        return None

                    content = await response.read()
        except Exception:
            logger.exception('error while doing request')
            return None

        logger.info('answer received')

        return data_protector_pb2.PluginReportResponse.FromString(content)

    async def request_deletion(self, account_id, logger):
        try:
            async with aiohttp.ClientSession() as session:
                data = data_protector_pb2.PluginDeletionRequest(account_id=account_id,
                                                                secret=self.secret)

                logger.info('request %s', self.deletion_url)

                async with session.post(self.deletion_url, data=data.SerializeToString()) as response:
                    logger.info('answer status: %s', response.status)

                    if response.status != 200:
                        return None

                    content = await response.read()
        except Exception:
            logger.exception('error while doing request')
            return None

        logger.info('answer received')

        return data_protector_pb2.PluginDeletionResponse.FromString(content)

    async def fill_subreport(self, subreport):

        logger = log.ContextLogger()

        logger.info('fill subreport for %s', subreport)

        answer = await self.request_report(str(subreport.data['id']), logger=logger)

        if answer is None:
            logger.error('no answer received, stop processing')
            return None

        if answer.result == data_protector_pb2.PluginReportResponse.ResultType.Value('FAILED'):
            logger.error('answer FAILED, stop processing')
            return None

        if answer.result != data_protector_pb2.PluginReportResponse.ResultType.Value('SUCCESS'):
            raise NotImplementedError('unknowm result type')

        if answer.data:
            report = s11n.from_json(answer.data)
        else:
            report = []

        data = copy.copy(subreport.data)

        new_data = [(subreport.source, data_type, data_value)
                    for data_type, data_value in report]

        data['report'].extend(new_data)

        logger.error('subreport updated, collected data: %s', len(new_data))

        return subreport.replace(state=relations.SUBREPORT_STATE.READY,
                                 data=data)

    async def process_deletion_request(self, request):
        logger = log.ContextLogger()

        logger.info('process deletion for %s', request)

        answer = await self.request_deletion(str(request.data['id']), logger)

        if answer is None:
            logger.error('no answer received, stop processing')
            return False, None

        if answer.result == data_protector_pb2.PluginReportResponse.ResultType.Value('FAILED'):
            logger.error('answer FAILED, stop processing')
            return False, None

        if answer.result != data_protector_pb2.PluginReportResponse.ResultType.Value('SUCCESS'):
            raise NotImplementedError('unknowm result type')

        logger.info('deletion processed successfully')

        return True, None


async def construct_plugin(config):
    return Plugin(report_url=config['report_url'],
                  deletion_url=config['deletion_url'],
                  secret=config['secret'])
