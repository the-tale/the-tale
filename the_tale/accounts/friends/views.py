# coding: utf-8

from dext.views import handler, validate_argument

from common.utils.resources import Resource
from common.utils.decorators import login_required

from accounts.prototypes import AccountPrototype
from accounts.views import validate_fast_account

from game.heroes.models import Hero
from game.heroes.prototypes import HeroPrototype

from accounts.friends.prototypes import FriendshipPrototype
from accounts.friends.forms import RequestForm

class FriendsResource(Resource):

    @login_required
    @validate_fast_account()
    def initialize(self, *args, **kwargs):
        super(FriendsResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def friends(self):
        friends = FriendshipPrototype.get_friends_for(self.account)
        candidates = FriendshipPrototype.get_candidates_for(self.account)
        accounts_ids = [account.id for account in friends]
        heroes = dict( (model.account_id, HeroPrototype(model=model)) for model in Hero.objects.filter(account_id__in=accounts_ids))

        return self.template('friends/friends_list.html',
                             {'friends': friends,
                              'candidates': candidates,
                              'heroes': heroes})

    @handler('candidates', method='get')
    def candidates(self):
        candidates = FriendshipPrototype.get_candidates_for(self.account)
        accounts_ids = [account.id for account in candidates]
        heroes = dict( (model.account_id, HeroPrototype(model=model)) for model in Hero.objects.filter(account_id__in=accounts_ids))
        return self.template('friends/friends_candidates.html',
                             {'candidates': candidates,
                              'heroes': heroes})

    @validate_argument('friend', AccountPrototype.get_by_id, 'friends', u'Игрок не найден')
    @handler('request', method='get')
    def request_dialog(self, friend):
        return self.template('friends/request_dialog.html',
                             {'friend': friend,
                              'form': RequestForm()})

    @validate_argument('friend', AccountPrototype.get_by_id, 'friends', u'Игрок не найден')
    @handler('request', method='post')
    def request_friendship(self, friend):

        if friend.is_fast:
            return self.json_error('friends.request_friendship.fast_friend', u'Вы не можете пригласить в друзья игрока не завершившего регистрацию')

        form = RequestForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('friends.request_friendship.form_errors', form.errors)

        FriendshipPrototype.request_friendship(self.account, friend, text=form.c.text)
        return self.json_ok()

    @validate_argument('friend', AccountPrototype.get_by_id, 'friends', u'Игрок не найден')
    @handler('accept', method='post')
    def accept_friendship(self, friend):
        FriendshipPrototype.request_friendship(self.account, friend)
        return self.json_ok()

    @validate_argument('friend', AccountPrototype.get_by_id, 'friends', u'Игрок не найден')
    @handler('remove', method='post')
    def remove(self, friend):
        FriendshipPrototype.remove_friendship(self.account, friend)
        return self.json_ok()
