
import smart_imports

smart_imports.all()


class Battle1x1ResultPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Battle1x1Result
    _readonly = ('id', 'created_at', 'participant_1_id', 'participant_2_id', 'result')
    _bidirectional = ()
    _get_by = ()

    @classmethod
    def create(cls, participant_1, participant_2, result):
        return cls(model=cls._model_class.objects.create(participant_1=participant_1._model,
                                                         participant_2=participant_2._model,
                                                         result=result))
