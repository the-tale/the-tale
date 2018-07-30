
import smart_imports

smart_imports.all()


_GET_ACCOUNT_ID_BY_EMAIL_FUNCTION = dext_discovering.get_function(conf.settings.GET_ACCOUNT_ID_BY_EMAIL)


def get_account_id(email):
    return _GET_ACCOUNT_ID_BY_EMAIL_FUNCTION(email)
