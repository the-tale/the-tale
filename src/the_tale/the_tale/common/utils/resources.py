
import smart_imports

smart_imports.all()


class Resource(old_views.BaseResource):

    ERROR_TEMPLATE = 'error.html'
    DIALOG_ERROR_TEMPLATE = 'dialog_error.html'

    def __init__(self, request, *args, **kwargs):
        super(Resource, self).__init__(request, *args, **kwargs)

        self.account = self.request.user
        if self.account.is_authenticated:
            self.account = accounts_prototypes.AccountPrototype(model=self.account)

    def validate_account_argument(self, account_id):
        if self.account and self.account.id == int(account_id):
            return self.account

        return accounts_prototypes.AccountPrototype.get_by_id(account_id)
