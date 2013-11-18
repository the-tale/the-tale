# coding: utf-8

from django.db import models

from the_tale.common.utils.decorators import lazy_property
from the_tale.common.utils.prototypes import BasePrototype

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.achievements.models import Achievement, AccountAchievements, GiveAchievementTask
from the_tale.accounts.achievements.container import AchievementsContainer
from the_tale.accounts.achievements import exceptions


class AchievementPrototype(BasePrototype):
    _model_class = Achievement
    _readonly = ('id', 'created_at', 'updated_at')
    _bidirectional = ('caption', 'description', 'order', 'group', 'type', 'approved', 'barrier', 'points')
    _get_by = ('id', )

    CAPTION_MAX_LENGTH = Achievement.CAPTION_MAX_LENGTH
    DESCRIPTION_MAX_LENGTH = Achievement.DESCRIPTION_MAX_LENGTH

    @classmethod
    def create(cls, group, type, caption, description, approved, barrier, points):
        from the_tale.accounts.achievements.storage import achievements_storage

        order = cls._db_all().aggregate(models.Max('order'))['order__max']

        if order is None:
            order = 0

        model = cls._db_create(group=group,
                               type=type,
                               caption=caption,
                               description=description,
                               order=order,
                               barrier=barrier,
                               approved=approved,
                               points=points)
        prototype = cls(model=model)

        achievements_storage.add_item(prototype.id, prototype)
        achievements_storage.update_version()

        return prototype


    def save(self):
        from the_tale.accounts.achievements.storage import achievements_storage

        if id(self) != id(achievements_storage[self.id]):
            raise exceptions.SaveNotRegisteredAchievementError(achievement=self.id)

        super(AchievementPrototype, self).save()
        achievements_storage.update_version()


    def check(self, old_value, new_value):
        return old_value < self.barrier <= new_value


class AccountAchievementsPrototype(BasePrototype):
    _model_class = AccountAchievements
    _readonly = ('id', 'account_id', 'points')
    _bidirectional = ()
    _get_by = ('id', 'account_id')
    _serialization_proxies = (('achievements', AchievementsContainer, None),)

    @lazy_property
    def account(self): return AccountPrototype(model=self._model.account)

    @classmethod
    def create(cls, account):
        return cls(model=cls._db_create(account=account._model))

    @classmethod
    def give_achievement(cls, account_id, achievement):
        if not achievement.approved:
            return
        GiveAchievementTaskPrototype.create(account_id=account_id, achievement_id=achievement.id)

    def add_achievement(self, achievement, notify):
        from the_tale.accounts.personal_messages.prototypes import MessagePrototype
        from the_tale.accounts.logic import get_system_user

        self.achievements.add_achievement(achievement)
        self._model.points = self.achievements.get_points()

        if not notify:
            return

        MessagePrototype.create(get_system_user(),
                                self.account,
                                u'Вы заработали достижение «%(achievement)s» — %(description)s' %
                                {'achievement': achievement.caption,
                                 'description': achievement.description})


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



class GiveAchievementTaskPrototype(BasePrototype):
    _model_class = GiveAchievementTask
    _readonly = ('id', 'account_id', 'achievement_id')
    _bidirectional = ()
    _get_by = ()

    @classmethod
    def create(cls, account_id, achievement_id):
        return cls(model=cls._db_create(account_id=account_id,
                                        achievement_id=achievement_id))

    def remove(self):
        self._model.delete()
