
import smart_imports

smart_imports.all()


@utils_jinja2.jinjafilter
def bb(value):
    return utils_jinja2.Markup(bbcode_renderers.default.render(value))


@utils_jinja2.jinjafilter
def bb_safe(value):
    return utils_jinja2.Markup(bbcode_renderers.safe.render(value))


@utils_jinja2.jinjafilter
def bb_chronicle(value):
    return utils_jinja2.Markup(bbcode_renderers.chronicle.render(value))
