# coding: utf-8

import functools

from dext.common.utils import views as dext_views


def check_client_version(client_version):
    try:
        client, version = client_version.split('-')
        return client and version
    except:
        return False

def handler(versions):

    @functools.wraps(handler)
    def decorator(view):

        pass_client_identificator = True

        expected = view._handler_info['expected']

        if 'api_version' not in expected['args']:
            expected['args'].append('api_version')

        if 'api_client' not in expected['args']:
            pass_client_identificator = False
            expected['args'].append('api_client')

        if expected['defaults'] is None:
            expected['defaults'] = {}

        expected['defaults'].update({'api_version': None, 'api_client': None})

        @functools.wraps(view)
        def view_wrapper(resource, **kwargs):

            api_version = kwargs.get('api_version')
            api_client = kwargs.get('api_client')

            if not api_version:
                return resource.json_error('api.no_method_version', u'Не указана версия метода')

            if not api_client:
                return resource.json_error('api.no_client_identificator', u'Не указана версия клиента')

            if not check_client_version(api_client):
                return resource.json_error('api.wrong_client_identificator_format',
                                           u'Неверный идентификатор клиента, ожидается <название программы>-<версия программы>')
            if api_version not in versions:
                return resource.json_error('api.wrong_method_version',
                                           u'Неверная версия метода, ожидается одна из: %s' % ', '.join(versions))

            if not pass_client_identificator and 'api_client' in kwargs:
                del kwargs['api_client']

            response = view(resource, **kwargs)

            if not isinstance(response, dict):
                return response

            if api_version != versions[0]:
                response['depricated'] = True

            return resource.json(**response)

        return view_wrapper

    return decorator


class Processor(dext_views.BaseViewProcessor):
    __slots__ = ('versions',)

    def __init__(self, versions, **kwargs):
        super(Processor, self).__init__(**kwargs)
        self.versions = versions

    def preprocess(self, context):

        api_version = context.django_request.GET.get('api_version', '').strip()

        if not api_version:
            raise dext_views.ViewError(code='api.no_method_version', message=u'Не указана версия метода')

        if api_version not in self.versions:
            raise dext_views.ViewError(code='api.wrong_method_version',
                                       message=u'Неверная версия метода, ожидается одна из: %s' % ', '.join(self.versions))

        context.api_version = api_version

        api_client = context.django_request.GET.get('api_client', '').strip()

        if not api_client:
            raise dext_views.ViewError(code='api.no_client_identificator', message=u'Не указана версия клиента')

        if not check_client_version(api_client):
            raise dext_views.ViewError(code='api.wrong_client_identificator_format',
                                       message=u'Неверный идентификатор клиента, ожидается <название программы>-<версия программы>')

        context.api_client = api_client


    def postprocess(self, context, response):
        response = super(Processor, self).postprocess(context, response)

        if context.api_version != self.versions[0]:
            response.content['depricated'] = True

        return response
