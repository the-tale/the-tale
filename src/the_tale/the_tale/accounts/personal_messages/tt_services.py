
import smart_imports

smart_imports.all()


class PersonalMessagesClient(tt_api_personal_messages.Client):
    pass


personal_messages = PersonalMessagesClient(entry_point=conf.settings.TT_PERSONAL_MESSAGES_ENTRY_POINT)
