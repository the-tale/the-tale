
from django.db import models

from dext.common.utils.urls import full_url

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property
from the_tale.common.utils import bbcode

from the_tale.accounts.models import Account
from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts import logic as accounts_logic

from the_tale.accounts.personal_messages import tt_api as pm_tt_api

from the_tale.accounts.friends.models import Friendship




class FriendshipPrototype(BasePrototype):
    _model_class = Friendship
    _readonly = ('is_confirmed', 'id', 'friend_1_id', 'friend_2_id')
    _bidirectional = ()
    _get_by = ()

    def _confirm(self):
        self._model.is_confirmed = True
        self.save()

        account_link='[url={}]{}[/url]'.format(full_url('https', 'accounts:show', self.friend_2.id), self.friend_2.nick_verbose)
        message = 'игрок {account_link} подтвердил, что вы являетесь друзьями'.format(account_link=account_link)

        pm_tt_api.send_message(sender_id=accounts_logic.get_system_user_id(),
                              recipients_ids=[self.friend_1.id],
                              body=message)

    @lazy_property
    def friend_1(self): return AccountPrototype(model=self._model.friend_1)

    @lazy_property
    def friend_2(self): return AccountPrototype(model=self._model.friend_2)

    @property
    def text_html(self): return bbcode.render(self._model.text)

    @classmethod
    def _get_for(cls, friend_1, friend_2):
        try:
            return cls(model=cls._model_class.objects.get(friend_1_id=friend_1.id, friend_2_id=friend_2.id))
        except cls._model_class.DoesNotExist:
            return None

    @classmethod
    def get_for_bidirectional(cls, friend_1, friend_2):
        try:
            return cls(model=cls._model_class.objects.get(models.Q(friend_1_id=friend_1.id, friend_2_id=friend_2.id) |
                                                          models.Q(friend_1_id=friend_2.id, friend_2_id=friend_1.id)) )
        except cls._model_class.DoesNotExist:
            return None

    @classmethod
    def _get_accounts_for(cls, account, is_confirmed):
        friendship_query = cls._model_class.objects.filter(models.Q(friend_1_id=account.id)|models.Q(friend_2_id=account.id), is_confirmed=is_confirmed)
        values = list(friendship_query.values_list('friend_1_id', 'friend_2_id'))

        if not values: return []

        friends_1_ids, friends_2_ids = zip(*values)
        accounts_ids = (set(friends_1_ids) | set(friends_2_ids)) - set([account.id])
        return [AccountPrototype(model=model) for model in Account.objects.filter(id__in=accounts_ids)]

    @classmethod
    def get_friends_for(cls, account):
        friendship_query = cls._model_class.objects.filter(models.Q(friend_1_id=account.id)|models.Q(friend_2_id=account.id), is_confirmed=True)
        values = list(friendship_query.values_list('friend_1_id', 'friend_2_id'))

        if not values: return []

        friends_1_ids, friends_2_ids = zip(*values)
        accounts_ids = (set(friends_1_ids) | set(friends_2_ids)) - set([account.id])
        return [AccountPrototype(model=model) for model in Account.objects.filter(id__in=accounts_ids)]

    @classmethod
    def get_candidates_for(cls, account):
        friendship_query = cls._model_class.objects.filter(friend_2_id=account.id, is_confirmed=False)
        accounts_ids = friendship_query.values_list('friend_1_id', flat=True)
        return [AccountPrototype(model=model) for model in Account.objects.filter(id__in=accounts_ids)]

    @classmethod
    def request_friendship(cls, friend_1, friend_2, text=None):
        own_request = cls._get_for(friend_1, friend_2)
        if own_request:
            if text is not None: #
                own_request._model.text = text
                own_request.save()
            return own_request

        his_request = cls._get_for(friend_2, friend_1)
        if his_request:
            his_request._confirm()
            return his_request

        model = cls._model_class.objects.create(friend_1=friend_1._model,
                                                friend_2=friend_2._model,
                                                text=text)
        prototype = cls(model=model)

        message = '''
игрок %(account_link)s предлагает вам дружить:

%(text)s

----------
принять или отклонить предложение вы можете на этой странице: %(friends_link)s
''' % {'account_link': '[url="%s"]%s[/url]' % (full_url('https', 'accounts:show', friend_1.id), friend_1.nick_verbose),
       'text': text,
       'friends_link': '[url="%s"]предложения дружбы[/url]' % full_url('https', 'accounts:friends:candidates')}

        # send message from name of user, who request friendship
        # since many users try to respod to system user
        pm_tt_api.send_message(sender_id=friend_1.id,
                              recipients_ids=[friend_2.id],
                              body=message)


        return prototype

    @classmethod
    def remove_friendship(cls, initiator, friend):
        request = cls.get_for_bidirectional(initiator, friend)

        if request is None:
            return

        account_link = '[url="{}"]{}[/url]'.format(full_url('https', 'accounts:show', initiator.id), initiator.nick_verbose)

        if request.is_confirmed:
            message = 'игрок {account_link} удалил вас из списка друзей'.format(account_link=account_link)
        else:
            message = 'игрок {account_link} отказался добавить вас в список друзей'.format(account_link=account_link)

        pm_tt_api.send_message(sender_id=accounts_logic.get_system_user_id(),
                              recipients_ids=[friend.id],
                              body=message)

        request.remove()


    def save(self):
        self._model.save()


    def remove(self):
        self._model.delete()
