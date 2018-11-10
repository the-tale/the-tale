
import smart_imports

smart_imports.all()


class ArtifactsError(utils_exceptions.TheTaleError):
    MSG = 'artifacts error'


class ArtifactsStorageError(ArtifactsError):
    MSG = 'artifacts storage error: %(message)s'


class SaveNotRegisteredArtifactError(ArtifactsError):
    MSG = 'try to save artifact %(artifact)r not from storage'


class DisableDefaultEquipmentError(ArtifactsError):
    MSG = 'we can not disable default hero equipment %(artifact)s'


class UnknownRarityType(ArtifactsError):
    MSG = 'unknown rare type: %(type)r'
