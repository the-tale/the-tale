
from the_tale.common.utils.exceptions import TheTaleError


class AccountError(TheTaleError):
    MSG = 'account error'


class UnkwnownAchievementTypeError(AccountError):
    MSG = 'unknown achievement type: %(achievement_type)r'


class EmailAndPasswordError(AccountError):
    MSG = 'email & password must be specified or not specified together'


class BotIsFastError(AccountError):
    MSG = 'can not cant fast account for bot'


class ChangeCredentialsError(AccountError):
    MSG = 'change credentials error'


class MailNotSpecifiedForFastAccountError(ChangeCredentialsError):
    MSG = 'new_email must be specified for fast account'


class PasswordNotSpecifiedForFastAccountError(ChangeCredentialsError):
    MSG = 'password must be specified for fast account'


class NickNotSpecifiedForFastAccountError(ChangeCredentialsError):
    MSG = 'nick must be specified for fast account'


class NewEmailNotSpecifiedError(ChangeCredentialsError):
    MSG = 'email not specified'


class CanNotCreateCardsTimer(AccountError):
    MSG = 'can not create cards timer'


class CanNotChangeCardsTimerSpeed(AccountError):
    MSG = 'can not change cards timer speed'
