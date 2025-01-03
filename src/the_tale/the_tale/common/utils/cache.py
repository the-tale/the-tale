
import smart_imports
smart_imports.all()


# cache is disabled due to moving the game into readonly mode


def set(key, value, timeout):
    # django_cache.cache.set(key, value, timeout)
    pass


def get(key):
    # return django_cache.cache.get(key)
    return None


def set_many(cache_dict, timeout):
    # django_cache.cache.set_many(cache_dict, timeout)
    pass


def delete(key):
    # django_cache.cache.delete(key)
    pass


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
