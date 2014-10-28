# coding: utf-8

from django.dispatch import receiver

from the_tale.accounts import signals as accounts_signals

from the_tale.accounts.third_party.conf import third_party_settings
from the_tale.accounts.third_party.prototypes import AccessTokenPrototype


@receiver(accounts_signals.on_before_logout, dispatch_uid='third_party__on_before_logout')
def on_before_logout(sender, **kwargs):
    request = kwargs['request']

    # remove third party access token on logout IF IT HAS BEEN ACCEPTED
    if third_party_settings.ACCESS_TOKEN_SESSION_KEY in request.session:
        token = AccessTokenPrototype.get_by_uid(request.session[third_party_settings.ACCESS_TOKEN_SESSION_KEY])
        if token is not None and token.state.is_ACCEPTED:
            token.remove()
