# coding: utf-8


from dext.common.utils.app_settings import app_settings

post_service_settings = app_settings('POST_SERVICE',
                                     MESSAGE_SENDER_DELAY=60,                                 # Задержка между проверкой наличия новых собщений
                                     ENABLE_MESSAGE_SENDER=True,                              # Включить/выключить фонового рабочего
                                     SETTINGS_ALLOWED_KEY='post service allowed',             # Идентификатор настройки в таблице settings в админке Django
                                                                                              # используется как дополнительная защита во время разработки
                                                                                              # (чтобы случайно не послать письма в время отладки рабочего)
                                                                                              # рабочий шлёт письма только в том случае, если в таблице settings есть запись
                                                                                              # с таким ключём и любым значением.
                                     SETTINGS_FORCE_ALLOWED_KEY='post service force allowed', # Идентификатор настройки в таблице settings в админке Django
                                                                                              # c перечнем уникальных идентификаторов сообщений, который будут отправляться
                                                                                              # независимо от настройки SETTINGS_ALLOWED_KEY
                                     MESSAGE_LIVE_TIME=2*24*60*60)                            # Время жизни запроса на отправку письма
