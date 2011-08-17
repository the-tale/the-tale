# -*- coding: utf-8 -*-
import datetime

from .models import MessagesLog, MessagePattern
from . import settings as journal_settings

from django_next.utils.decorators import nested_commit_on_success
from django_next.utils import s11n

class JournalMessageException(Exception): pass

def get_messages_log_by_id(id):
    model = MessagesLog.obects.get(id=id)
    return get_messages_log_by_model(model)

def get_messages_log_by_model(model):
    return MessagesLogPrototype(model=model)

def get_pattern_by_id(id):
    model = MessagePattern.objects.get(id=id)
    return get_pattern_by_model(model)

def get_pattern_by_model(model):
    return MessagePatternPrototype(model=model)

def choose_pattern(type, situation_mask):
    model = MessagePattern.objects.filter(type=type, state=MessagePattern.STATE.APPROVED).order_by('?')[0]
    return get_pattern_by_model(model)


class MessagesLogPrototype(object):

    def __init__(self, model, *argv, **kwargs):
        super(MessagesLogPrototype, self).__init__(*argv, **kwargs)
        self.model = model

    @property
    def messages(self): 
        if not hasattr(self, '_messages'):
            self._messages = s11n.from_json(self.model.messages)            
        return self._messages

    def push_message(self, pattern_id, rendered_text):
        messages = self.messages

        messages.append({'pattern_id': pattern_id,
                         'text': rendered_text})
        if len(messages) > journal_settings.MESSAGES_NUMBER:
            messages = messages[-journal_settings.MESSAGES_NUMBER:]

        self.model.messages = s11n.to_json(messages)
        delattr(self, '_messages')

    def clear_messages(self):
        self.model.messages = '[]'

    ###########################################
    # Object operations
    ###########################################

    def remove(self): return self.model.delete()
    def save(self): self.model.save()

    @classmethod
    @nested_commit_on_success
    def create(cls, hero):
        messages = MessagesLog.objects.create(hero=hero.model)
        return messages    

    def ui_info(self): 
        return self.messages


class MessagePatternPrototype(object):
    
    def __init__(self, model, *argv, **kwargs):
        super(MessagePatternPrototype, self).__init__(*argv, **kwargs)
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def created_at(self): return self.model.created_at

    def get_state(self): return self.model.state
    def set_state(self, value): self.model.state = value
    state = property(get_state, set_state)

    @property
    def is_approved(self): 
        return (self.state == MessagePattern.STATE.APPROVED)

    @property
    def is_unapproved(self): 
        return (self.state == MessagePattern.STATE.UNAPPROVED)


    @property
    def is_removed(self): 
        return (self.state == MessagePattern.STATE.REMOVED)

    def get_remove_after(self): 
        if isinstance(self.model, MessagePattern):
            return None
        return self.model.remove_after
    def set_remove_after(self, value):
        self.model.remove_after = value
    remove_after = property(get_remove_after, set_remove_after)

    @property
    def type(self): return self.model.type

    def get_mask(self): return self.model.mask
    def set_mask(self, value): self.model.mask = value
    mask = property(get_mask, set_mask)

    def get_text(self): return self.model.text
    def set_text(self, value): self.model.text = value
    text = property(get_text, set_text)

    def get_comment(self): return self.model.comment
    def set_comment(self, value): self.model.comment = value
    comment = property(get_comment, set_comment)

    @property
    def author(self): return self.model.author

    def get_editor(self): return self.model.editor
    def set_editor(self, value): self.model.editor = value
    editor = property(get_editor, set_editor)

    ###########################################
    # State change operations
    ###########################################

    @nested_commit_on_success
    def approve_pattern(self, editor):
        self.state = MessagePattern.STATE.APPROVED
        self.editor = editor

    @nested_commit_on_success
    def reject_pattern(self, editor):
        self.state = MessagePattern.STATE.UNAPPROVED
        self.editor = editor

    def remove_pattern(self, editor):
        self.remove_after = datetime.datetime.now() + datetime.timedelta(days=journal_settings.REMOVE_AFTER_DAYS)
        self.state = MessagePattern.STATE.REMOVED
        self.editor = editor

    def restore_pattern(self, editor):
        self.state = MessagePattern.STATE.UNAPPROVED
        self.remove_after = None
        self.editor = editor

    ###########################################
    # Object operations
    ###########################################

    def remove(self): return self.model.delete()
    def save(self): self.model.save()

    @classmethod
    @nested_commit_on_success
    def create(cls, type, mask, text, comment, author, editor=None):
        pattern = MessagePattern.objects.create(type=type,
                                                mask=mask,
                                                text=text,
                                                comment=comment,
                                                author=author,
                                                editor=editor)
        return cls(model=pattern)
