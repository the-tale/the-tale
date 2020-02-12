
import smart_imports

smart_imports.all()


class FriendsResource(utils_resources.Resource):

    @utils_decorators.login_required
    @accounts_views.validate_fast_account()
    def initialize(self, *args, **kwargs):
        super(FriendsResource, self).initialize(*args, **kwargs)

    @old_views.handler('', method='get')
    def friends(self):
        friends = prototypes.FriendshipPrototype.get_friends_for(self.account)
        candidates = prototypes.FriendshipPrototype.get_candidates_for(self.account)
        accounts_ids = [account.id for account in friends]
        clans_ids = [model.clan_id for model in friends]
        heroes = {hero.account_id: hero for hero in heroes_logic.load_heroes_by_account_ids(accounts_ids)}
        clans = {clan.id: clan for clan in clans_logic.load_clans(clans_ids)}
        return self.template('friends/friends_list.html',
                             {'friends': friends,
                              'candidates': candidates,
                              'heroes': heroes,
                              'clans': clans})

    @old_views.handler('candidates', method='get')
    def candidates(self):
        candidates = prototypes.FriendshipPrototype.get_candidates_for(self.account)
        accounts_ids = [account.id for account in candidates]
        clans_ids = [model.clan_id for model in candidates]
        heroes = {hero.account_id: hero for hero in heroes_logic.load_heroes_by_account_ids(accounts_ids)}
        clans = {clan.id: clan for clan in clans_logic.load_clans(clans_ids)}
        return self.template('friends/friends_candidates.html',
                             {'candidates': candidates,
                              'heroes': heroes,
                              'clans': clans})

    @accounts_views.validate_ban_forum()
    @old_views.validate_argument('friend', accounts_prototypes.AccountPrototype.get_by_id, 'friends', 'Игрок не найден')
    @old_views.handler('request', method='get')
    def request_dialog(self, friend):

        if friend.id == accounts_logic.get_system_user().id:
            return self.auto_error('friends.request_dialog.system_user', 'Вы не можете пригласить в друзья системного пользователя')

        return self.template('friends/request_dialog.html',
                             {'friend': friend,
                              'form': forms.RequestForm()})

    @accounts_views.validate_ban_forum()
    @old_views.validate_argument('friend', accounts_prototypes.AccountPrototype.get_by_id, 'friends', 'Игрок не найден')
    @old_views.handler('request', method='post')
    def request_friendship(self, friend):

        if friend.is_fast:
            return self.json_error('friends.request_friendship.fast_friend', 'Вы не можете пригласить в друзья игрока не завершившего регистрацию')

        if friend.id == accounts_logic.get_system_user().id:
            return self.json_error('friends.request_friendship.system_user', 'Вы не можете пригласить в друзья системного пользователя')

        form = forms.RequestForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('friends.request_friendship.form_errors', form.errors)

        prototypes.FriendshipPrototype.request_friendship(self.account, friend, text=form.c.text)
        return self.json_ok()

    @old_views.validate_argument('friend', accounts_prototypes.AccountPrototype.get_by_id, 'friends', 'Игрок не найден')
    @old_views.handler('accept', method='post')
    def accept_friendship(self, friend):
        prototypes.FriendshipPrototype.request_friendship(self.account, friend)
        return self.json_ok()

    @old_views.validate_argument('friend', accounts_prototypes.AccountPrototype.get_by_id, 'friends', 'Игрок не найден')
    @old_views.handler('remove', method='post')
    def remove(self, friend):
        prototypes.FriendshipPrototype.remove_friendship(self.account, friend)
        return self.json_ok()
