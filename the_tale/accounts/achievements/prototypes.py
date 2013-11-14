# coding: utf-8

from django.db import models

from the_tale.common.utils.prototypes import BasePrototype

from the_tale.accounts.achievements.models import Achievement, AccountAchievements, GiveAchievementTask
from the_tale.accounts.achievements.container import AchievementsContainer
from the_tale.accounts.achievements import exceptions


class AchievementPrototype(BasePrototype):
    _model_class = Achievement
    _readonly = ('id', 'created_at', 'updated_at')
    _bidirectional = ('caption', 'description', 'order', 'group', 'type', 'approved', 'barrier')
    _get_by = ('id', )

    CAPTION_MAX_LENGTH = Achievement.CAPTION_MAX_LENGTH
    DESCRIPTION_MAX_LENGTH = Achievement.DESCRIPTION_MAX_LENGTH

    @classmethod
    def create(cls, group, type, caption, description, approved, barrier):
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
                               approved=approved)
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


    def check(self, object, old_value, new_value):
        return old_value < self.barrier <= new_value


class AccountAchievementsPrototype(BasePrototype):
    _model_class = AccountAchievements
    _readonly = ('id', 'account_id')
    _bidirectional = ()
    _get_by = ('id', 'account_id')
    _serialization_proxies = (('achievements', AchievementsContainer, None),)

    @classmethod
    def create(cls, account):
        return cls(model=cls._db_create(account=account._model))

    @classmethod
    def give_achievement(cls, account_id, achievement):
        if not achievement.approved:
            return
        GiveAchievementTaskPrototype.create(account_id=account_id, achievement_id=achievement.id)

    def has_achievement(self, achievement):
        return self.achievements.has_achievement(achievement)



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
