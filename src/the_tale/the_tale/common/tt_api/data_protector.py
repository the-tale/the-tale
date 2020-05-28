
import smart_imports

smart_imports.all()


class REPORT_STATE(enum.Enum):
    PROCESSING = 1
    READY = 2
    NOT_EXISTS = 3


@dataclasses.dataclass(frozen=True)
class Report:
    __slots__ = ('data', 'state', 'completed_at', 'expire_at')

    data: dict
    state: REPORT_STATE
    completed_at: datetime.datetime
    expire_at: datetime.datetime

    def postprocess_records(self, processor):
        self.data[:] = [processor(record) for record in self.data]

    def data_by_source(self):
        data = {}

        for source, type, value in self.data:
            if source not in data:
                data[source] = []

            data[source].append((type, value))

        return data


class Client(client.Client):
    __slots__ = ()

    def ids_to_protobuf(self, ids):
        return [tt_protocol_data_protector_pb2.SourceInfo(source=str(source), id=str(id))
                for source, id in ids]

    def cmd_request_report(self, ids):
        request = tt_protocol_data_protector_pb2.RequestReportRequest(ids=self.ids_to_protobuf(ids))

        answer = operations.sync_request(url=self.url('request-report'),
                                         data=request,
                                         AnswerType=tt_protocol_data_protector_pb2.RequestReportResponse)

        return uuid.UUID(answer.report_id)

    def cmd_get_report(self, id):
        request = tt_protocol_data_protector_pb2.GetReportRequest(report_id=id.hex)

        answer = operations.sync_request(url=self.url('get-report'),
                                         data=request,
                                         AnswerType=tt_protocol_data_protector_pb2.GetReportResponse)

        return Report(completed_at=datetime.datetime.fromtimestamp(answer.report.completed_at),
                      expire_at=datetime.datetime.fromtimestamp(answer.report.expire_at),
                      state=REPORT_STATE(answer.report.state),
                      data=s11n.from_json(answer.report.data))

    def cmd_request_deletion(self, ids):
        request = tt_protocol_data_protector_pb2.RequestDeletionRequest(ids=self.ids_to_protobuf(ids))

        operations.sync_request(url=self.url('request-deletion'),
                                data=request,
                                AnswerType=tt_protocol_data_protector_pb2.RequestDeletionResponse)

    def cmd_debug_clear_service(self):
        if not django_settings.TESTS_RUNNING:
            return

        operations.sync_request(url=self.url('debug-clear-service'),
                                data=tt_protocol_data_protector_pb2.DebugClearServiceRequest(),
                                AnswerType=tt_protocol_data_protector_pb2.DebugClearServiceResponse)
