
from django_next.utils.app_settings import app_settings

settings = app_settings('JM', 
                        MESSAGES_NUMBER=10,
                        REMOVE_AFTER_DAYS=30)
