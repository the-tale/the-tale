# coding: utf-8

import uuid

from the_tale.common.utils.prototypes import BasePrototype

from the_tale.accounts.third_party import models
from the_tale.accounts.third_party import relations


class AccessTokenPrototype(BasePrototype): #pylint: disable=R0904
    _model_class = models.AccessToken
    _readonly = ('id', 'uid', 'account_id', 'application_name', 'application_info', 'application_description', 'created_at', 'updated_at')
    _bidirectional = ('state', )
    _get_by = ('uid', 'account_id')


    @classmethod
    def create(cls, application_name, application_info, application_description, account=None, state=relations.ACCESS_TOKEN_STATE.UNACCEPTED):
        model = cls._db_create(uid=str(uuid.uuid4()),
                               application_name=application_name,
                               application_info=application_info,
                               application_description=application_description,
                               state=state,
                               account=account._model if account else None)

        return cls(model)

    def accept(self, account):
        self._model.account = account._model
        self.state = relations.ACCESS_TOKEN_STATE.ACCEPTED
        self.save()


    def cache_data(self):
        return {'account_id': self.account_id}


    def remove(self):
        # TODO: reset cache
        self._model.delete()

    @classmethod
    def fast_create(cls, id, account=None, state=relations.ACCESS_TOKEN_STATE.UNACCEPTED):
        token = cls.create(application_name='app-name-%d' % id,
                           application_info='app-info-%d' % id,
                           application_description='app-descr-%d' % id,
                           account=account,
                           state=state)

        return token
