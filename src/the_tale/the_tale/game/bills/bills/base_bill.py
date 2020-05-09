
import smart_imports

smart_imports.all()


class BaseBill(object):

    type = NotImplemented

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
        return cls.UserForm(post, original_bill_id=None)

    def get_user_form_update(self, post=None, initial=None, original_bill_id=None, **kwargs):
        if initial:
            return self.UserForm(initial=initial, original_bill_id=original_bill_id)
        return self.UserForm(post, original_bill_id=original_bill_id)

    def get_moderator_form_update(self, post=None, initial=None, original_bill_id=None, **kwargs):
        if initial:
            return self.ModeratorForm(initial=initial, original_bill_id=original_bill_id)
        return self.ModeratorForm(post, original_bill_id=original_bill_id)

    def apply(self, bill=None):
        raise NotImplementedError

    def decline(self, bill):
        pass

    def end(self, bill):
        raise NotImplementedError

    def has_meaning(self):
        raise NotImplementedError
