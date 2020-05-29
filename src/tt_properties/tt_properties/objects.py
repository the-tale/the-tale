
import dataclasses

from .relations import MODE


@dataclasses.dataclass
class Property:
    object_id: int
    type: int
    value: str
    mode: MODE = dataclasses.field(compare=False)
