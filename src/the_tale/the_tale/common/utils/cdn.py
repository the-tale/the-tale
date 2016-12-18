# coding: utf-8

import urllib.request, urllib.error, urllib.parse
import collections


def get_cdns_info(cdns):

    info = {}

    for cdn in cdns:
        variable_name, local_path, cdn_path, checked_url = cdn

        variable_value = local_path

        if isinstance(checked_url, collections.Callable):
            checked_url = checked_url()

        if cdn_path is not None:
            try:
                resource = urllib.request.urlopen(checked_url)
                resource.close()
                variable_value = cdn_path
            except urllib.error.URLError:
                pass

        info[variable_name] = variable_value

    return info


def get_local_paths(cdns):
    info = {}

    for cdn in cdns:
        variable_name, local_path, cdn_path, checked_url = cdn
        info[variable_name] = local_path

    return info
