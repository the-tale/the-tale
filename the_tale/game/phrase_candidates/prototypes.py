# coding: utf-8

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

    @property
    def text(self): return self.model.text

    @property
    def author_id(self): return self.model.author_id

    @property
    def type(self): return self.model.type

    @property
    def type_name(self): return self.model.type_name

    @property
    def subtype_name(self): return self.model.subtype_name

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
    def create(cls, type_, type_name, subtype_name, author, text):
        model = PhraseCandidate.objects.create(type=type_,
                                               type_name=type_name,
                                               subtype_name=subtype_name,
                                               author=author.model,
                                               text=text)

        return cls(model)
