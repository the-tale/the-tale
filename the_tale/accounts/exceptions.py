# coding: utf-8

from the_tale.common.utils.exceptions import TheTaleError


class AccountError(TheTaleError):
    MSG = u'account error'

class UnkwnownAchievementTypeError(AccountError):
    MSG = u'unknown achievement type: %(achievement_type)r'


class EmailAndPasswordError(AccountError):
    MSG = u'email & password must be specified or not specified together'

class BotIsFastError(AccountError):
    MSG = u'can not cant fast account for bot'



class ChangeCredentialsError(AccountError):
    MSG = u'change credentials error'


class MailNotSpecifiedForFastAccountError(ChangeCredentialsError):
    MSG = u'new_email must be specified for fast account'

class PasswordNotSpecifiedForFastAccountError(ChangeCredentialsError):
    MSG = u'password must be specified for fast account'

class NickNotSpecifiedForFastAccountError(ChangeCredentialsError):
    MSG = u'nick must be specified for fast account'

class NewEmailNotSpecifiedError(ChangeCredentialsError):
    MSG = u'email not specified'
