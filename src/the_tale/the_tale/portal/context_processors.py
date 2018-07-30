
import smart_imports

smart_imports.all()


def section(request):
    section_ = None
    for regex, section_name in conf.SITE_SECTIONS:
        if regex.match(request.path):
            section_ = section_name
            break
    return {'SECTION': section_}


def cdn_paths(request):
    return logic.cdn_paths()
