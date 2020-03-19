
import smart_imports
smart_imports.all()


def set(key, value, timeout):
    django_cache.cache.set(key, value, timeout)


def get(key):
    return django_cache.cache.get(key)


def set_many(cache_dict, timeout):
    django_cache.cache.set_many(cache_dict, timeout)


def delete(key):
    django_cache.cache.delete(key)


def memoize(key, timeout):

    @functools.wraps(memoize)
    def decorator(function):

        @functools.wraps(function)
        def wrapper(*argv, **kwargs):

            data = django_cache.cache.get(key)

            if data is not None:
                return data

            data = function(*argv, **kwargs)

            django_cache.cache.set(key, data, timeout)

            return data

        return wrapper

    return decorator
