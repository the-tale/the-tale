
import smart_imports

smart_imports.all()


class CompanionsAbilitiesError(companions_exceptions.CompanionsError):
    MSG = 'companions abilities error'


class NotOrderedUIDSError(CompanionsAbilitiesError):
    MSG = 'uids in container MUST be ordered'
