
import smart_imports

smart_imports.all()


def linguistics_context(request):  # pylint: disable=W0613
    return {'linguistics_settings': conf.settings,
            'UTG_PROPERTY_TYPE': utg_relations.PROPERTY_TYPE}
