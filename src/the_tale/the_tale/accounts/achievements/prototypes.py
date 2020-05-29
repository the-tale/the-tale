
import smart_imports

smart_imports.all()


class AchievementPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Achievement
    _readonly = ('id', 'created_at', 'updated_at')
    _bidirectional = ('caption', 'description', 'order', 'group', 'type', 'approved', 'barrier', 'points', 'item_1_id', 'item_2_id', 'item_3_id')
    _get_by = ('id', )

    CAPTION_MAX_LENGTH = models.Achievement.CAPTION_MAX_LENGTH
    DESCRIPTION_MAX_LENGTH = models.Achievement.DESCRIPTION_MAX_LENGTH

    @property
    def item_1(self):
        return collections_storage.items.get(self.item_1_id)

    @property
    def item_2(self):
        return collections_storage.items.get(self.item_2_id)

    @property
    def item_3(self):
        return collections_storage.items.get(self.item_3_id)

    @classmethod
    def create(cls, group, type, caption, description, approved, barrier, points, item_1=None, item_2=None, item_3=None):
        order = cls._db_all().aggregate(django_models.Max('order'))['order__max']

        if order is None:
            order = 0

        model = cls._db_create(group=group,
                               type=type,
                               caption=caption,
                               description=description,
                               order=order,
                               barrier=barrier,
                               approved=approved,
                               points=points,
                               item_1=item_1._model if item_1 is not None else None,
                               item_2=item_2._model if item_2 is not None else None,
                               item_3=item_3._model if item_3 is not None else None)
        prototype = cls(model=model)

        storage.achievements.add_item(prototype.id, prototype)
        storage.achievements.update_version()

        return prototype

    def save(self):
        if id(self) != id(storage.achievements[self.id]):
            raise exceptions.SaveNotRegisteredAchievementError(achievement=self.id)

        super(AchievementPrototype, self).save()
        storage.achievements.update_version()

    def check(self, old_value, new_value):
        if new_value < 0:
            return old_value > self.barrier >= new_value
        else:
            return old_value < self.barrier <= new_value

    @property
    def rewards(self):
        rewards = []
        if self.item_1 is not None:
            rewards.append(self.item_1)
        if self.item_2 is not None:
            rewards.append(self.item_2)
        if self.item_3 is not None:
            rewards.append(self.item_3)
        return rewards

    @property
    def approved_rewards(self):
        return [reward for reward in self.rewards if reward.approved]


class AccountAchievementsPrototype(utils_prototypes.BasePrototype):
    _model_class = models.AccountAchievements
    _readonly = ('id', 'account_id', 'points')
    _bidirectional = ()
    _get_by = ('id', 'account_id')
    _serialization_proxies = (('achievements', container.AchievementsContainer, None),)

    @utils_decorators.lazy_property
    def account(self): return accounts_prototypes.AccountPrototype(model=self._model.account)

    @classmethod
    def create(cls, account):
        return cls(model=cls._db_create(account=account._model))

    @classmethod
    def give_achievement(cls, account_id, achievement):
        if not achievement.approved:
            return

        GiveAchievementTaskPrototype.create(account_id=account_id, achievement_id=achievement.id)

    def add_achievement(self, achievement, notify):
        already_had_achievement = self.achievements.has_achievement(achievement)

        self.achievements.add_achievement(achievement)
        self._model.points = self.achievements.get_points()

        rewards = achievement.rewards
        approved_rewards = achievement.approved_rewards

        for item in rewards:
            collections_prototypes.GiveItemTaskPrototype.create(self.account_id, item.id)

        if not notify or already_had_achievement:
            return

        rewards_message = ''

        if approved_rewards:
            reward_texts = []
            for item in approved_rewards:
                reward_texts.append('[url=%s#k%d]%s[/url]' % (utils_urls.full_url('https', 'collections:collections:show', item.kit.collection.id),
                                                              item.kit.id,
                                                              item.caption))
            rewards_message = 'Награды: %s' % ', '.join(reward_texts)

        message = ('Вы заработали достижение «%(achievement)s» — %(description)s %(rewards_message)s' %
                   {'achievement': '[url=%s#a%d]%s[/url]' % (utils_urls.full_url('https', 'accounts:achievements:group', achievement.group.slug),
                                                             achievement.id,
                                                             achievement.caption),
                    'description': achievement.description,
                    'rewards_message': rewards_message})

        personal_messages_logic.send_message(accounts_logic.get_system_user().id, [self.account.id], message, asynchronous=True)

    def remove_achievement(self, achievement):
        self.achievements.remove_achievement(achievement)
        self._model.points = self.achievements.get_points()

    def has_achievement(self, achievement):
        return self.achievements.has_achievement(achievement)

    def timestamp_for(self, achievement):
        return self.achievements.timestamp_for(achievement)

    def achievements_ids(self): return self.achievements.achievements_ids()

    def last_achievements(self, number): return self.achievements.last_achievements(number=number)

    def sort_key_for(self, achievement):
        if not achievement.approved:
            return (2, achievement.order)
        if self.has_achievement(achievement):
            return (0, achievement.order)
        return (1, achievement.order)


class GiveAchievementTaskPrototype(utils_prototypes.BasePrototype):
    _model_class = models.GiveAchievementTask
    _readonly = ('id', 'account_id', 'achievement_id')
    _bidirectional = ()
    _get_by = ()

    @classmethod
    def create(cls, account_id, achievement_id):
        return cls(model=cls._db_create(account_id=account_id,
                                        achievement_id=achievement_id))

    def remove(self):
        self._model.delete()
