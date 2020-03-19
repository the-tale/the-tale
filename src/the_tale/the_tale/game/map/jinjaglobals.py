
import smart_imports

smart_imports.all()


@utils_jinja2.jinjaglobal
def region_url(turn=None):
    return logic.region_url(turn=turn)


@utils_jinja2.jinjaglobal
def power_color(power, percents, reverse):
    if percents:
        if power > 0.01:
            return 'Chartreuse' if not reverse else 'red'

        elif power < -0.01:
            return 'red' if not reverse else 'Chartreuse'

        return 'yellow'

    if power > 1:
        return 'Chartreuse' if not reverse else 'red'

    elif power < -1:
        return 'red' if not reverse else 'Chartreuse'

    return 'yellow'
