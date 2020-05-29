
import smart_imports

smart_imports.all()


class LexiconError(linguistics_exceptions.LinguisticsError):
    pass


class NoFreeVerificatorSubstitutionError(linguistics_exceptions.LinguisticsError):
    MSG = 'No free verificator substitution for key %(key)s and variable %(variable)s'


class WrongFormNumberError(linguistics_exceptions.LinguisticsError):
    MSG = 'Wrong forms number'
