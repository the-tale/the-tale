# coding: utf-8

from django.db import models

from the_tale.common.utils.prototypes import BasePrototype

from the_tale.accounts.achievements.models import Achievement, AccountAchievements



class AchievementPrototype(BasePrototype):
    _model_class = Achievement
    _readonly = ('id', 'created_at', 'updated_at')
    _bidirectional = ('caption', 'description', 'order', 'group', 'type')
    _get_by = ('id', )


    CAPTION_MAX_LENGTH = Achievement.CAPTION_MAX_LENGTH
    DESCRIPTION_MAX_LENGTH = Achievement.DESCRIPTION_MAX_LENGTH


    @classmethod
    def create(cls, group, type, caption, description):
        order = cls._db_all().aggregate(models.Max('order')).get('order__max', 0) + 1

        model = cls._db_create(group=group,
                               type=type,
                               caption=caption,
                               description=description,
                               order=order)
        return cls(model=model)



class AccountAchievementsPrototype(BasePrototype):
    _model_class = AccountAchievements
    _readonly = ('id', 'account_id')
    _bidirectional = ('caption', 'description', 'order', 'group', 'type')
    _get_by = ('id', 'account_id')


    @classmethod
    def create(cls, account):
        return cls(model=cls._db_create(account=account._model))
