
import smart_imports

smart_imports.all()


@dext_jinja2.jinjaglobal
def chronicle_actors(records):
    return prototypes.RecordToActorPrototype.get_actors_for_records(records)
