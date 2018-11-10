
import smart_imports

smart_imports.all()


def refuse_third_party(func):

    @functools.wraps(func)
    def wrapper(resource, *argv, **kwargs):
        if conf.settings.ACCESS_TOKEN_SESSION_KEY in resource.request.session:
            return resource.auto_error('third_party.access_restricted', 'Доступ к этому функционалу запрещён для сторонних приложений')

        return func(resource, *argv, **kwargs)

    return wrapper
