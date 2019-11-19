
import smart_imports

smart_imports.all()


def balance(request):
    return {'c': constants,
            'f': formulas,
            'tt_emissaries_constants': tt_emissaries_constants,
            'tt_clans_constants': tt_clans_constants}
