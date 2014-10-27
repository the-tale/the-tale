# coding: utf-8

from django.conf import settings as project_settings

from dext.common.utils.urls import url

from the_tale.accounts.third_party import prototypes


class ThirdPartyTestsMixin(object):

    def request_third_party_token(self, account=None):
        request_token_url = url('accounts:third-party:tokens:request-access', api_version='1.0', api_client=project_settings.API_CLIENT)
        self.check_ajax_ok(self.client.post(request_token_url, {'application_name': 'app-name',
                                                                'application_info': 'app-info',
                                                                'application_description': 'app-descr'}))
        if account:
            token = prototypes.AccessTokenPrototype._db_latest()
            token.accept(account)
