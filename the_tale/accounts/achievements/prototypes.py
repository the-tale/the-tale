# coding: utf-8

from django.db import models

from the_tale.common.utils.prototypes import BasePrototype

from the_tale.accounts.achievements.models import Achievement, AccountAchievements
from the_tale.accounts.achievements.container import AchievementsContainer


class AchievementPrototype(BasePrototype):
    _model_class = Achievement
    _readonly = ('id', 'created_at', 'updated_at')
    _bidirectional = ('caption', 'description', 'order', 'group', 'type', 'approved')
    _get_by = ('id', )

    CAPTION_MAX_LENGTH = Achievement.CAPTION_MAX_LENGTH
    DESCRIPTION_MAX_LENGTH = Achievement.DESCRIPTION_MAX_LENGTH

    @classmethod
    def create(cls, group, type, caption, description, approved):
        order = cls._db_all().aggregate(models.Max('order'))['order__max']

        if order is None:
            order = 0

        model = cls._db_create(group=group,
                               type=type,
                               caption=caption,
                               description=description,
                               order=order,
                               approved=approved)
        return cls(model=model)



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
        pass

    def has_achievement(self, achievement):
        return self.achievements.has_achievement(achievement)
