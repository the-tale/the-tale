

from dext.common.utils import jinja2

from the_tale.game.chronicle.prototypes import RecordToActorPrototype


@jinja2.jinjaglobal
def chronicle_actors(records):
    return RecordToActorPrototype.get_actors_for_records(records)
