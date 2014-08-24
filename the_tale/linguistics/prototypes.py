# coding: utf-8

from dext.common.utils import s11n

from utg import words as utg_words

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.linguistics import models
from the_tale.linguistics import relations


class WordPrototype(BasePrototype):
    _model_class = models.Word
    _readonly = ('id', 'type', 'created_at')
    _bidirectional = ('state', )
    _get_by = ('id', 'account_id')

    @lazy_property
    def utg_word(self):
        return utg_words.Word.deserialize(s11n.from_json(self._model.forms))

    def has_on_review_copy(self):
        if self.state.is_ON_REVIEW:
            return False

        return self._db_filter(state=relations.WORD_STATE.ON_REVIEW, normal_form=self.utg_word.normal_form(), type=self.type).exists()

    @classmethod
    def create(cls, utg_word):

        model = cls._db_create(type=utg_word.type,
                               state=relations.WORD_STATE.ON_REVIEW,
                               normal_form=utg_word.normal_form(),
                               forms=s11n.to_json(utg_word.serialize()))

        return cls(model)

    def save(self):
        self._model.forms = s11n.to_json(self.utg_word.serialize())
        self._model.normal_form = self.utg_word.normal_form()
        super(WordPrototype, self).save()

    def remove(self):
        self._model.delete()
