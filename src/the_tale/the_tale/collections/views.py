
import smart_imports

smart_imports.all()


class BaseCollectionsResource(utils_resources.Resource):

    @dext_old_views.validate_argument('collection', lambda value: storage.collections[int(value)], 'collections', 'Коллекция не найдена')
    @dext_old_views.validate_argument('kit', lambda value: storage.kits[int(value)], 'collections', 'Набор не найден')
    @dext_old_views.validate_argument('item', lambda value: storage.items[int(value)], 'collections', 'Предмет не найден')
    def initialize(self, collection=None, kit=None, item=None, **kwargs):
        super(BaseCollectionsResource, self).initialize(**kwargs)
        self.item = item
        self.kit = kit
        self.collection = collection

        self.master_account = None

        if self.item:
            self.kit = self.item.kit

        if self.kit:
            self.collection = self.kit.collection

    @utils_decorators.lazy_property
    def edit_collection_permission(self): return self.account.has_perm('collections.edit_collection')

    @utils_decorators.lazy_property
    def moderate_collection_permission(self): return self.account.has_perm('collections.moderate_collection')

    @utils_decorators.lazy_property
    def edit_kit_permission(self): return self.account.has_perm('collections.edit_kit')

    @utils_decorators.lazy_property
    def moderate_kit_permission(self): return self.account.has_perm('collections.moderate_kit')

    @utils_decorators.lazy_property
    def edit_item_permission(self): return self.account.has_perm('collections.edit_item')

    @utils_decorators.lazy_property
    def moderate_item_permission(self): return self.account.has_perm('collections.moderate_item')

    @utils_decorators.lazy_property
    def can_see_all_collections(self): return self.edit_collection_permission or self.moderate_collection_permission

    @utils_decorators.lazy_property
    def can_edit_collection(self):
        if self.collection and self.collection.approved:
            return self.can_moderate_collection
        return self.edit_collection_permission or self.moderate_collection_permission

    @utils_decorators.lazy_property
    def can_moderate_collection(self): return self.moderate_collection_permission

    @utils_decorators.lazy_property
    def can_edit_kit(self):
        if self.kit and self.kit.approved:
            return self.can_moderate_kit
        return self.edit_kit_permission or self.moderate_kit_permission

    @utils_decorators.lazy_property
    def can_moderate_kit(self): return self.moderate_kit_permission

    def _can_edit_item(self, item):
        if item and item.approved:
            return self.can_moderate_item
        return self.edit_item_permission or self.moderate_item_permission

    @utils_decorators.lazy_property
    def can_edit_item(self): return self._can_edit_item(self.item)

    @utils_decorators.lazy_property
    def can_moderate_item(self): return self.moderate_item_permission

    @utils_decorators.lazy_property
    def collections(self):
        if self.moderate_collection_permission or self.edit_collection_permission:
            return sorted(prototypes.CollectionPrototype.all_collections(), key=lambda c: c.caption)
        else:
            return sorted(prototypes.CollectionPrototype.approved_collections(), key=lambda c: c.caption)

    @utils_decorators.lazy_property
    def kits(self):
        if self.moderate_kit_permission or self.edit_kit_permission:
            return sorted(prototypes.KitPrototype.all_kits(), key=lambda k: k.caption)
        else:
            return sorted(prototypes.KitPrototype.approved_kits(), key=lambda k: k.caption)

    def collection_url(self, collection):
        if self.master_account:
            return dext_urls.url('collections:collections:show', collection.id, account=self.master_account.id)
        else:
            return dext_urls.url('collections:collections:show', collection.id)

    def index_url(self):
        if self.master_account:
            return dext_urls.url('collections:collections:', account=self.master_account.id)
        else:
            return dext_urls.url('collections:collections:')


@dext_old_views.validator(code='collections.collections.no_edit_rights', message='нет прав для редактирования коллекции')
def validate_can_edit_collection(resource, *args, **kwargs):
    return resource.can_edit_collection


@dext_old_views.validator(code='collections.collections.no_moderate_rights', message='нет прав для модерации коллекции')
def validate_can_moderate_collection(resource, *args, **kwargs):
    return resource.can_moderate_collection


@dext_old_views.validator(code='collections.collections.not_approved', message='коллекция не найдена', status_code=404)
def validate_collection_approved(resource, *args, **kwargs):
    return resource.collection and (resource.can_edit_collection or resource.collection.approved)


class CollectionsResource(BaseCollectionsResource):

    @dext_old_views.validate_argument('account', accounts_prototypes.AccountPrototype.get_by_id, 'collections', 'Игрок не найден')
    @dext_old_views.handler('')
    def index(self, account=None):

        if account is None and self.account.is_authenticated:
            return self.redirect(dext_urls.url('collections:collections:', account=self.account.id))

        self.master_account = account

        master_account_items = None
        last_items = []
        if self.master_account:
            master_account_items = prototypes.AccountItemsPrototype.get_by_account_id(self.master_account.id)
            last_items = master_account_items.last_items(number=conf.settings.LAST_ITEMS_NUMBER)

        account_items = None
        if self.account.is_authenticated:
            account_items = prototypes.AccountItemsPrototype.get_by_account_id(self.account.id)

        collections_statistics = logic.get_collections_statistics(account_items=master_account_items)

        collections_table = utils_logic.split_into_table(self.collections, 3)

        return self.template('collections/collections/index.html',
                             {'collections_statistics': collections_statistics,
                              'collections_table': collections_table,
                              'account_items': account_items,
                              'master_account_items': master_account_items,
                              'last_items': last_items})

    @utils_decorators.login_required
    @validate_can_edit_collection()
    @dext_old_views.handler('new')
    def new(self):
        return self.template('collections/collections/new.html',
                             {'form': forms.EditCollectionForm()})

    @utils_decorators.login_required
    @validate_can_edit_collection()
    @dext_old_views.handler('create', method='post')
    def create(self):
        form = forms.EditCollectionForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.collections.create.form_errors', form.errors)

        collection = prototypes.CollectionPrototype.create(caption=form.c.caption,
                                                           description=form.c.description)

        return self.json_ok(data={'next_url': dext_urls.url('collections:collections:show', collection.id)})

    @validate_collection_approved()
    @dext_old_views.validate_argument('account', accounts_prototypes.AccountPrototype.get_by_id, 'collections', 'Игрок не найден')
    @dext_old_views.handler('#collection', name='show')
    def show(self, account=None):

        if account is None and self.account.is_authenticated:
            return self.redirect(dext_urls.url('collections:collections:show', self.collection.id, account=self.account.id))

        self.master_account = account

        master_account_items = None
        if self.master_account:
            master_account_items = prototypes.AccountItemsPrototype.get_by_account_id(self.master_account.id)

        account_items = None
        if self.account.is_authenticated:
            account_items = prototypes.AccountItemsPrototype.get_by_account_id(self.account.id)

        collections_statistics = logic.get_collections_statistics(account_items=master_account_items)

        kits = sorted([kit for kit in storage.kits.all() if kit.collection_id == self.collection.id], key=lambda k: k.caption)

        if not (self.can_edit_kit or self.can_moderate_kit):
            kits = [kit for kit in kits if kit.approved]

        items = {kit.id: [] for kit in kits}

        items_query = storage.items.all()

        if not self.edit_item_permission and not self.moderate_item_permission:
            items_query = (item for item in items_query if item.approved)

        items_query = sorted([item for item in items_query if item.kit_id in items], key=lambda i: i.caption)

        for item in items_query:
            items[item.kit_id].append(item)

        return self.template('collections/collections/show.html',
                             {'kits': kits,
                              'items': items,
                              'account_items': account_items,
                              'master_account_items': master_account_items,
                              'collections_statistics': collections_statistics})

    @utils_decorators.login_required
    @validate_can_edit_collection()
    @dext_old_views.handler('#collection', 'edit')
    def edit(self):
        form = forms.EditCollectionForm(initial={'caption': self.collection.caption,
                                                 'description': self.collection.description})

        return self.template('collections/collections/edit.html',
                             {'form': form})

    @utils_decorators.login_required
    @validate_can_edit_collection()
    @dext_old_views.handler('#collection', 'update')
    def update(self, method='post'):
        form = forms.EditCollectionForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.collections.update.form_errors', form.errors)

        self.collection.caption = form.c.caption
        self.collection.description = form.c.description
        self.collection.save()

        return self.json_ok()

    @utils_decorators.login_required
    @validate_can_moderate_collection()
    @dext_old_views.handler('#collection', 'approve')
    def approve(self, method='post'):
        self.collection.approved = True
        self.collection.save()

        return self.json_ok()

    @utils_decorators.login_required
    @validate_can_moderate_collection()
    @dext_old_views.handler('#collection', 'disapprove')
    def disapprove(self, method='post'):
        self.collection.approved = False
        self.collection.save()

        return self.json_ok()


@dext_old_views.validator(code='collections.kits.no_edit_rights', message='нет прав для редактирования набора')
def validate_can_edit_kit(resource, *args, **kwargs):
    return resource.can_edit_kit or resource.can_moderate_kit


@dext_old_views.validator(code='collections.kits.no_moderate_rights', message='нет прав для модерации набора')
def validate_can_moderate_kit(resource, *args, **kwargs):
    return resource.can_moderate_kit


@dext_old_views.validator(code='collections.kits.not_approved', message='набор не найден', status_code=404)
def validate_kit_approved(resource, *args, **kwargs):
    return resource.kit and (resource.can_edit_kit or resource.kit.approved)


class KitsResource(BaseCollectionsResource):

    @utils_decorators.login_required
    @validate_can_edit_kit()
    @dext_old_views.handler('new')
    def new(self):
        return self.template('collections/kits/new.html',
                             {'form': forms.EditKitForm()})

    @utils_decorators.login_required
    @validate_can_edit_kit()
    @dext_old_views.handler('create', method='post')
    def create(self):
        form = forms.EditKitForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.kits.create.form_errors', form.errors)

        kit = prototypes.KitPrototype.create(collection=form.c.collection,
                                             caption=form.c.caption,
                                             description=form.c.description)

        return self.json_ok(data={'next_url': dext_urls.url('collections:collections:show', kit.collection_id)})

    @utils_decorators.login_required
    @validate_can_edit_kit()
    @dext_old_views.handler('#kit', 'edit')
    def edit(self):
        form = forms.EditKitForm(initial={'collection': self.kit.collection_id,
                                          'caption': self.kit.caption,
                                          'description': self.kit.description})

        return self.template('collections/kits/edit.html',
                             {'form': form})

    @utils_decorators.login_required
    @validate_can_edit_kit()
    @dext_old_views.handler('#kit', 'update')
    def update(self, method='post'):
        form = forms.EditKitForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.kits.update.form_errors', form.errors)

        self.kit.collection_id = form.c.collection.id
        self.kit.caption = form.c.caption
        self.kit.description = form.c.description
        self.kit.save()

        return self.json_ok(data={'next_url': dext_urls.url('collections:collections:show', self.kit.collection_id)})

    @utils_decorators.login_required
    @validate_can_moderate_kit()
    @dext_old_views.handler('#kit', 'approve')
    def approve(self, method='post'):
        self.kit.approved = True
        self.kit.save()

        return self.json_ok()

    @utils_decorators.login_required
    @validate_can_moderate_kit()
    @dext_old_views.handler('#kit', 'disapprove')
    def disapprove(self, method='post'):
        self.kit.approved = False
        self.kit.save()

        return self.json_ok()


@dext_old_views.validator(code='collections.items.no_edit_rights', message='нет прав для редактирования предмета')
def validate_can_edit_item(resource, *args, **kwargs):
    return resource.can_edit_item or resource.can_moderate_item


@dext_old_views.validator(code='collections.items.no_moderate_rights', message='нет прав для модерации предмета')
def validate_can_moderate_item(resource, *args, **kwargs):
    return resource.can_moderate_item


class ItemsResource(BaseCollectionsResource):

    @utils_decorators.login_required
    @validate_can_edit_item()
    @dext_old_views.handler('new')
    def new(self):
        return self.template('collections/items/new.html',
                             {'form': forms.EditItemForm()})

    @utils_decorators.login_required
    @validate_can_edit_item()
    @dext_old_views.handler('create', method='post')
    def create(self):
        form = forms.EditItemForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.items.create.form_errors', form.errors)

        item = prototypes.ItemPrototype.create(kit=form.c.kit,
                                               caption=form.c.caption,
                                               text=form.c.text)

        return self.json_ok(data={'next_url': dext_urls.url('collections:collections:show', item.kit.collection_id)})

    @utils_decorators.login_required
    @validate_can_edit_item()
    @dext_old_views.handler('#item', 'edit')
    def edit(self):
        form = forms.EditItemForm(initial={'kit': self.item.kit_id,
                                           'caption': self.item.caption,
                                           'text': self.item.text})

        return self.template('collections/items/edit.html',
                             {'form': form})

    @utils_decorators.login_required
    @validate_can_edit_item()
    @dext_old_views.handler('#item', 'update')
    def update(self, method='post'):

        form = forms.EditItemForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.items.update.form_errors', form.errors)

        self.item.kit_id = form.c.kit.id
        self.item.caption = form.c.caption
        self.item.text = form.c.text
        self.item.save()

        return self.json_ok(data={'next_url': dext_urls.url('collections:collections:show', self.item.kit.collection_id)})

    @utils_decorators.login_required
    @validate_can_moderate_item()
    @dext_old_views.handler('#item', 'approve')
    def approve(self, method='post'):
        self.item.approved = True
        self.item.save()

        return self.json_ok()

    @utils_decorators.login_required
    @validate_can_moderate_item()
    @dext_old_views.handler('#item', 'disapprove')
    def disapprove(self, method='post'):
        self.item.approved = False
        self.item.save()

        return self.json_ok()
