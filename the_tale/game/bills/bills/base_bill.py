# coding: utf-8


class BaseBill(object):

    @classmethod
    def user_form_template(cls):
        return 'bills/bills/{type}_user_form.html'.format(type=cls.type.name.lower())

    @classmethod
    def moderator_form_template(cls):
        return 'bills/bills/{type}_moderator_form.html'.format(type=cls.type.name.lower())

    @classmethod
    def show_template(cls):
        return 'bills/bills/{type}_show.html'.format(type=cls.type.name.lower())

    @property
    def moderator_form_initials(self):
        return {}

    def initialize_with_moderator_data(self, moderator_form):
        pass

    @classmethod
    def get_user_form_create(cls, post=None, **kwargs):
        return cls.UserForm(post)

    def get_user_form_update(self, post=None, initial=None, **kwargs):
        if initial:
            return self.UserForm(initial=initial)
        return  self.UserForm(post)

    def apply(self, bill=None):
        raise NotImplementedError

    def decline(self, bill):
        pass

    def end(self, bill):
        raise NotImplementedError

    def has_meaning(self):
        raise NotImplementedError
