# coding: utf-8


class BaseBill(object):

    @property
    def moderator_form_initials(self):
        return {}

    def initialize_with_moderator_data(self, moderator_form):
        pass

    @classmethod
    def get_user_form_create(cls, post=None):
        return cls.UserForm(post)

    def get_user_form_update(self, post=None, initial=None):
        if initial:
            return self.UserForm(initial=initial)
        return  self.UserForm(post)

    def apply(self, bill=None):
        raise NotImplementedError

    def decline(self, bill):
        pass

    def end(self, bill):
        raise NotImplementedError
