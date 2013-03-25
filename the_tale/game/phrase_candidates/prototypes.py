# coding: utf-8

from accounts.prototypes import AccountPrototype

from game.phrase_candidates.models import PhraseCandidate, PHRASE_CANDIDATE_STATE


class PhraseCandidatePrototype(object):

    def __init__(self, model):
        self.model = model


    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(PhraseCandidate.objects.get(id=id_))
        except PhraseCandidate.DoesNotExist:
            return None


    @property
    def id(self): return self.model.id

    @property
    def created_at(self): return self.model.created_at

    def get_text(self): return self.model.text
    def set_text(self, value): self.model.text = value
    text = property(get_text, set_text)

    @property
    def author_id(self): return self.model.author_id

    @property
    def author(self):
        if not hasattr(self, '_author'):
            self._author = AccountPrototype.get_by_id(self.model.author_id)
        return self._author

    def get_moderator_id(self): return self.model.moderator_id
    def set_moderator_id(self, value): self.model.moderator_id = value
    moderator_id = property(get_moderator_id, set_moderator_id)

    def get_type(self): return self.model.type
    def set_type(self, value): self.model.type = value
    type = property(get_type, set_type)

    def get_subtype(self): return self.model.subtype
    def set_subtype(self, value): self.model.subtype = value
    subtype = property(get_subtype, set_subtype)

    def get_type_name(self): return self.model.type_name
    def set_type_name(self, value): self.model.type_name = value
    type_name = property(get_type_name, set_type_name)

    def get_subtype_name(self): return self.model.subtype_name
    def set_subtype_name(self, value): self.model.subtype_name = value
    subtype_name = property(get_subtype_name, set_subtype_name)

    def get_state(self):
        if not hasattr(self, '_state'):
            self._state = PHRASE_CANDIDATE_STATE(self.model.state)
        return self._state
    def set_state(self, value):
        self.state.update(value)
        self.model.state = self.state.value
    state = property(get_state, set_state)

    def save(self):
        self.model.save()


    @classmethod
    def create(cls, type_, type_name, subtype, subtype_name, author, text):
        model = PhraseCandidate.objects.create(type=type_,
                                               type_name=type_name,
                                               subtype=subtype,
                                               subtype_name=subtype_name,
                                               author=author._model,
                                               text=text)

        return cls(model)
