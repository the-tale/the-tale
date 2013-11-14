# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class ArtifactsError(TheTaleError):
    MSG = u'artifacts error'

class ArtifactsStorageError(ArtifactsError):
    MSG = u'artifacts storage error'

class SaveNotRegisteredArtifactError(ArtifactsError):
    MSG = u'try to save artifact %(artifact)r not from storage'


class UnknownArtifactRarityTypeError(ArtifactsError):
    MSG = u'unknown artifact %(artifact)r rarity type: %(type)r'


class ChangeDefaultEquipmentUIDError(ArtifactsError):
    MSG = u'we can not change uuid of default hero equipment (%(old_uid)s - > %(new_uid)s)'


class DisableDefaultEquipmentError(ArtifactsError):
    MSG = u'we can not disable default hero equipment %(artifact)s'
