
import uuid

from psycopg2.extras import Json as PGJson

from tt_web import postgresql as db

from . import objects
from . import relations


async def create_report_base(ids):

    result = await db.transaction(_create_report_base, {'ids': ids})

    return result


async def _create_report_base(execute, arguments):
    ids = arguments['ids']

    result = await execute('''INSERT INTO reports (id, state, data, created_at, updated_at, completed_at, expire_at)
                              VALUES (%(id)s, %(state)s, %(data)s, NOW(), NOW(), NULL, NULL)
                              RETURNING id''',
                           {'id': uuid.uuid4(),
                            'state': relations.REPORT_STATE.PROCESSING.value,
                            'data': PGJson({'report': []})})

    report_id = result[0]['id']

    for source, id in ids:
        await execute('''INSERT INTO subreports (report, source, state, data, created_at, updated_at)
                         VALUES (%(report)s, %(source)s, %(state)s, %(data)s, NOW(), NOW())''',
                      {'report': report_id,
                       'source': source,
                       'state': relations.SUBREPORT_STATE.PROCESSING.value,
                       'data': PGJson({'report': [],
                                       'id': id})})

    return report_id


async def get_unprocessed_subpreports():
    result = await db.sql('SELECT id FROM subreports WHERE state=%(state)s',
                          {'state': relations.SUBREPORT_STATE.PROCESSING.value})

    return [row['id'] for row in result]


async def get_report(id):

    result = await db.sql('SELECT * FROM reports WHERE id=%(id)s',
                          {'id': id})

    if not result:
        return objects.Report(id=id,
                              state=relations.REPORT_STATE.NOT_EXISTS,
                              data=None,
                              completed_at=None,
                              expire_at=None)

    row = result[0]

    return objects.Report(id=row['id'],
                          state=relations.REPORT_STATE(row['state']),
                          data=row['data'],
                          completed_at=row['completed_at'],
                          expire_at=row['expire_at'])


def row_to_subreport(row):
    return objects.SubReport(id=row['id'],
                             report_id=row['report'],
                             source=row['source'],
                             state=relations.SUBREPORT_STATE(row['state']),
                             data=row['data'])


async def get_subreport(id):

    result = await db.sql('SELECT * FROM subreports WHERE id=%(id)s',
                          {'id': id})

    if not result:
        raise NotImplementedError('Service logic expects that get_subreport called only for existed subreports')

    return row_to_subreport(result[0])


async def update_subreport(subreport):
    result = await db.sql('''UPDATE subreports SET state=%(state)s,
                                                   data=%(data)s
                             WHERE id=%(id)s
                             RETURNING id''',
                         {'id': subreport.id,
                          'state': subreport.state.value,
                          'data': PGJson(subreport.data)})

    if not result:
        raise NotImplementedError('Service logic expects that update_subreport called only for existed subreports')


async def get_reports_with_ready_subreports():

    result = await db.sql('SELECT report FROM subreports GROUP BY report HAVING EVERY(state=%(state)s)',
                          {'state': relations.SUBREPORT_STATE.READY.value})

    return [row['report'] for row in result]


async def get_report_subreports(report_id):
    result = await db.sql('SELECT * FROM subreports WHERE report=%(report_id)s',
                          {'report_id': report_id})

    return [row_to_subreport(row) for row in result]


async def complete_report(report_id, full_data, livetime):

    await db.transaction(_complete_report, {'report_id': report_id,
                                            'full_data': full_data,
                                            'livetime': livetime})


async def _complete_report(execute, arguments):
    report_id = arguments['report_id']
    full_data = arguments['full_data']
    livetime = arguments['livetime']

    report = await get_report(report_id)

    report.data['report'] = full_data

    await execute('''UPDATE reports SET state=%(state)s,
                                        data=%(data)s,
                                        completed_at=NOW(),
                                        expire_at=NOW() + %(livetime)s * INTERVAL '1 second'
                     WHERE id=%(report_id)s''',
                  {'report_id': report_id,
                   'state': relations.REPORT_STATE.READY.value,
                   'data': PGJson(report.data),
                   'livetime': livetime})

    await execute('DELETE FROM subreports WHERE report=%(report_id)s',
                  {'report_id': report_id})


async def remove_old_reports():
    await db.sql('DELETE FROM reports WHERE expire_at < NOW()')


async def mark_for_deletion(core_id, ids):

    result = await db.transaction(_mark_for_deletion, {'ids': ids,
                                                       'core_id': core_id})

    return result


async def _mark_for_deletion(execute, arguments):
    core_id = arguments['core_id']
    ids = arguments['ids']

    for source, id in ids:
        await execute('''INSERT INTO deletion_requests (core_id, source, data, created_at, updated_at)
                         VALUES (%(core_id)s, %(source)s, %(data)s, NOW(), NOW())''',
                      {'core_id': core_id,
                       'source': source,
                       'data': PGJson({'id': id})})

    await execute('''INSERT INTO deletion_history (core_id, created_at)
                     VALUES (%(core_id)s, NOW())''',
                  {'core_id': core_id})


async def get_unprocessed_deletion_requests():
    result = await db.sql('SELECT * FROM deletion_requests')
    return [row['id'] for row in result]


async def get_deletion_request(request_id):
    result = await db.sql('SELECT * FROM deletion_requests WHERE id=%(request_id)s',
                          {'request_id': request_id})
    if not result:
        return None

    return objects.DeletionRequest(id=result[0]['id'],
                                   source=result[0]['source'],
                                   data=result[0]['data'])


async def remove_deletion_request(reques_id):
    await db.sql('DELETE FROM deletion_requests WHERE id=%(reques_id)s', {'reques_id': reques_id})


async def update_deletion_request(deletion_request):
    result = await db.sql('''UPDATE deletion_requests SET data=%(data)s
                             WHERE id=%(id)s
                             RETURNING id''',
                          {'id': deletion_request.id,
                           'data': PGJson(deletion_request.data)})

    if not result:
        raise NotImplementedError('Service logic expects that update_deletion_request called only for existed requests')


async def clean_database():
    await db.sql('TRUNCATE reports, subreports, deletion_requests, deletion_history')
