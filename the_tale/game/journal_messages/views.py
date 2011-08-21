# -*- coding: utf-8 -*-

from django_next.views.resources import handler
from django_next.utils.decorators import  nested_commit_on_success

from common.utils.resources import Resource
from accounts.decorators import login_required

from . import forms
from .models import MessagePattern
from .prototypes import MessagePatternPrototype, get_pattern_by_model, get_pattern_by_id

#TODO: add permissions check
#TODO: management command to clean 'remove query'

class JournalMessagesResource(Resource):

    def __init__(self, request, pattern_id=None, *args, **kwargs):
        super(JournalMessagesResource, self).__init__(request, *args, **kwargs)
        self.pattern_id = pattern_id

    @property
    def pattern(self):
        if not hasattr(self, '_pattern'):
            self._pattern = None
            if self.pattern_id is not None:
                self._pattern = get_pattern_by_id(self.pattern_id)
        return self._pattern

    @handler('#pattern_id', 'edit', method='get')
    @login_required
    def edit(self):
        if not self.pattern.is_unapproved:
            return self.template('error.html', 
                                 {'error_msg': 'you can edit only unapproved messages'})

        initials = forms.EditMessagePatternForm.make_initials(self.pattern)
        form = forms.EditMessagePatternForm(initial=initials)
        return self.template('journal_messages/edit.html',
                             {'pattern': self.pattern,
                              'form': form} )

    @handler('#pattern_id', 'update', method='post')
    @login_required
    @nested_commit_on_success
    def update(self):

        form = forms.EditMessagePatternForm(self.request.POST)

        if form.is_valid():
            self.pattern.text = form.c.text
            self.pattern.command = form.c.comment
            self.pattern.editor = self.account
            self.save()
            return self.json(status='ok')

        return self.json(status='error', errors=form.errors)


    @handler('new', method='get')
    @login_required
    def new(self):

        form = forms.NewMessagePatternForm()

        return self.template('journal_messages/new.html',
                             {'form': form} )


    @handler('create', method='post')
    @login_required
    @nested_commit_on_success
    def create(self):
        form = forms.NewMessagePatternForm(self.request.POST)

        if form.is_valid():
            pattern = MessagePatternPrototype.create(type=form.c.type, 
                                                     mask=0, 
                                                     text=form.c.text, 
                                                     comment=form.c.comment,
                                                     author=self.account)
            return self.json(status='ok')

        return self.json(status='error', errors=form.errors)

    @handler('#pattern_id', 'approve', method='post')
    @login_required
    @nested_commit_on_success
    def approve(self):
        if not self.pattern.is_unapproved:
            return self.json(status='error', error='you can approve only unapproved messages')

        self.pattern.approve_pattern(editor=self.account)
        self.pattern.save()
        return self.json(status='ok')

    @handler('#pattern_id', 'reject', method='post')
    @login_required
    @nested_commit_on_success
    def reject(self):
        if not self.pattern.is_approved:
            return self.json(status='error', error='you can reject only approved messages')
        self.pattern.reject_pattern(editor=self.account)
        self.pattern.save()
        return self.json(status='ok')

    @handler('#pattern_id', 'remove', method='post')
    @login_required
    @nested_commit_on_success
    def remove(self):
        if not self.pattern.is_unapproved:
            return self.json(status='error', error='you can remove only unapproved messages')

        self.pattern.remove_pattern(editor=self.account)
        self.pattern.save()
        return self.json(status='ok')

    @handler('#pattern_id', 'restore', method='post')
    @login_required
    @nested_commit_on_success
    def restore(self):
        if not self.pattern.is_removed:
            return self.json(status='error', error='you can restore only removed messages')
        self.pattern.restore_pattern(editor=self.account)
        self.pattern.save()
        return self.json(status='ok')

    @handler('admin', method='get')
    @login_required
    def admin(self):
        return self.template('journal_messages/admin.html',
                             {})
        

    @handler('', method='get', args=[('type', 'approved')])
    @login_required
    def approved_list(self):
        patterns = list(MessagePattern.objects.filter(state=MessagePattern.STATE.APPROVED))
        patterns = [get_pattern_by_model(pattern) for pattern in patterns]

        return self.template('journal_messages/approved_list.html',
                             {'patterns': patterns})


    @handler('', method='get', args=[('type', 'unapproved')])
    @login_required
    def unapproved_list(self):
        patterns = list(MessagePattern.objects.filter(state=MessagePattern.STATE.UNAPPROVED))
        patterns = [get_pattern_by_model(pattern) for pattern in patterns]

        return self.template('journal_messages/unapproved_list.html',
                             {'patterns': patterns})


    @handler('', method='get', args=[('type', 'removed')])
    @login_required
    def removed_list(self):
        patterns = list(MessagePattern.objects.filter(state=MessagePattern.STATE.REMOVED))
        patterns = [get_pattern_by_model(pattern) for pattern in patterns]

        return self.template('journal_messages/removed_list.html',
                             {'patterns': patterns})

