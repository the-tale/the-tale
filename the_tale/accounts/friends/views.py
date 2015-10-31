# coding: utf-8

from dext.views import handler, validate_argument

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.views import validate_fast_account
from the_tale.accounts.logic import get_system_user

from the_tale.game.heroes import logic as heroes_logic

from the_tale.accounts.friends.prototypes import FriendshipPrototype
from the_tale.accounts.friends.forms import RequestForm

from the_tale.accounts.clans.prototypes import ClanPrototype


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
        clans_ids = [ model.clan_id for model in friends]
        heroes = {hero.account_id: hero for hero in  heroes_logic.load_heroes_by_account_ids(accounts_ids)}
        clans = {clan.id:clan for clan in ClanPrototype.get_list_by_id(clans_ids)}
        return self.template('friends/friends_list.html',
                             {'friends': friends,
                              'candidates': candidates,
                              'heroes': heroes,
                              'clans': clans})

    @handler('candidates', method='get')
    def candidates(self):
        candidates = FriendshipPrototype.get_candidates_for(self.account)
        accounts_ids = [account.id for account in candidates]
        clans_ids = [ model.clan_id for model in candidates]
        heroes = {hero.account_id: hero for hero in  heroes_logic.load_heroes_by_account_ids(accounts_ids)}
        clans = {clan.id:clan for clan in ClanPrototype.get_list_by_id(clans_ids)}
        return self.template('friends/friends_candidates.html',
                             {'candidates': candidates,
                              'heroes': heroes,
                              'clans': clans})

    @validate_argument('friend', AccountPrototype.get_by_id, 'friends', u'Игрок не найден')
    @handler('request', method='get')
    def request_dialog(self, friend):

        if friend.id == get_system_user().id:
            return self.auto_error('friends.request_dialog.system_user', u'Вы не можете пригласить в друзья системного пользователя')

        return self.template('friends/request_dialog.html',
                             {'friend': friend,
                              'form': RequestForm()})

    @validate_argument('friend', AccountPrototype.get_by_id, 'friends', u'Игрок не найден')
    @handler('request', method='post')
    def request_friendship(self, friend):

        if friend.is_fast:
            return self.json_error('friends.request_friendship.fast_friend', u'Вы не можете пригласить в друзья игрока не завершившего регистрацию')

        if friend.id == get_system_user().id:
            return self.json_error('friends.request_friendship.system_user', u'Вы не можете пригласить в друзья системного пользователя')

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
