
import enum


class BIND_RESULT(enum.Enum):
    CODE_NOT_FOUND = 1
    CODE_EXPIRED = 2
    ALREADY_BINDED = 3
    SUCCESS_NEW = 4
    SUCCESS_REBIND = 5

    def is_success(self):
        return self in (self.ALREADY_BINDED,
                        self.SUCCESS_NEW,
                        self.SUCCESS_REBIND)


BIND_RESULT_MESSAGES = {BIND_RESULT.CODE_NOT_FOUND: 'Код привязки аккаунта не найден, введён неверно или устарел. Пожалуйста, получите новый код на сайте игры.',
                        BIND_RESULT.CODE_EXPIRED: 'Код привязки аккаунта устарел. Пожалуйста, получите новый код на сайте игры.',
                        BIND_RESULT.ALREADY_BINDED: 'Ваши аккаунты уже были связаны. Дополнительные действия не требуются.',
                        BIND_RESULT.SUCCESS_NEW: 'Ура! Ваши аккаунты связаны!',
                        BIND_RESULT.SUCCESS_REBIND: 'Ваш аккаунт Discord привязан к новому аккаунту игры.'}


class GAME_DATA_TYPE(enum.Enum):
    NICKNAME = 1
    ROLES = 2
    BAN = 3
