# coding: utf-8


class BaseBill(object):

    UserForm = NotImplemented
    ModeratorForm = NotImplemented

    @classmethod
    def user_form_template(cls):
        return 'bills/bills/{type}_user_form.html'.format(type=cls.type.name.lower())

    @classmethod
    def show_template(cls):
        return 'bills/bills/{type}_show.html'.format(type=cls.type.name.lower())

    def initialize_with_form(self, form):
        pass

    @classmethod
    def get_user_form_create(cls, post=None, **kwargs):
        return cls.UserForm(post)

    def get_user_form_update(self, post=None, initial=None, **kwargs):
        if initial:
            return self.UserForm(initial=initial)
        return self.UserForm(post)

    def get_moderator_form_update(self, post=None, initial=None, **kwargs):
        if initial:
            return self.ModeratorForm(initial=initial)
        return self.ModeratorForm(post)

    def apply(self, bill=None):
        raise NotImplementedError

    def decline(self, bill):
        pass

    def end(self, bill):
        raise NotImplementedError

    def has_meaning(self):
        raise NotImplementedError
