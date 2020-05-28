
import importlib

from . import relations
from . import exceptions
from . import operations


_PLUGINS = {}


async def clear_plugins():
    _PLUGINS.clear()


async def get_pluging_for_source(config, source_name):

    if source_name in _PLUGINS:
        return _PLUGINS[source_name]

    try:
        plugin_module = importlib.import_module(config['sources'][source_name]['plugin'])

        plugin = await plugin_module.construct_plugin(config['sources'][source_name])

    except Exception as e:
        raise exceptions.CanNotConstructPlugin(exception=repr(e))

    _PLUGINS[source_name] = plugin

    return plugin


async def process_subreport(config, subreport_id):
    old_subreport = await operations.get_subreport(subreport_id)

    if old_subreport.state == relations.SUBREPORT_STATE.READY:
        return

    plugin = await get_pluging_for_source(config, old_subreport.source)

    new_subreport = await plugin.fill_subreport(old_subreport)

    if new_subreport is None:
        return

    if old_subreport == new_subreport:
        return

    await operations.update_subreport(new_subreport)


async def process_subreports(config):

    unprocessed_ids = await operations.get_unprocessed_subpreports()

    for unprocessed_id in unprocessed_ids:
        await process_subreport(config, unprocessed_id)


async def form_report(config, report_id):
    subreports = await operations.get_report_subreports(report_id)

    full_data = merge_report([subreport.data['report'] for subreport in subreports])

    await operations.complete_report(report_id, full_data, livetime=config['report_livetime'])


async def form_reports(config):

    new_reports_ids = await operations.get_reports_with_ready_subreports()

    for report_id in new_reports_ids:
        await form_report(config, report_id)


def merge_report(records_lists):
    merged_records = []

    for records in records_lists:
        merged_records.extend(records)

    return normalize_report(merged_records)


def normalize_report(records):

    new_report = []

    for record in records:
        if record not in new_report:
            new_report.append(record)

    new_report.sort(key=lambda record: (record[0], record[1]))

    return new_report


async def process_deletion_request(config, request_id):
    old_request = await operations.get_deletion_request(request_id)

    if old_request is None:
        return

    plugin = await get_pluging_for_source(config, old_request.source)

    success, new_request = await plugin.process_deletion_request(old_request)

    if new_request is not None:
        await operations.update_deletion_request(new_request)

    if success:
        await operations.remove_deletion_request(request_id)


async def process_deletion_requests(config):

    unprocessed_ids = await operations.get_unprocessed_deletion_requests()

    for unprocessed_id in unprocessed_ids:
        await process_deletion_request(config, unprocessed_id)


async def process_all(config):
    await process_subreports(config)
    await form_reports(config)
    await operations.remove_old_reports()
    await process_deletion_requests(config)
