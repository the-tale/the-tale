# coding: utf-8

from dext.views import handler, validate_argument, validator
from dext.utils.urls import url

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required, lazy_property
from the_tale.common.utils.logic import split_into_table

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.collections.prototypes import CollectionPrototype, KitPrototype, ItemPrototype, AccountItemsPrototype
from the_tale.collections.forms import EditCollectionForm, EditKitForm, EditItemForm
from the_tale.collections.logic import get_collections_statistics
from the_tale.collections.conf import collections_settings
from the_tale.collections.storage import collections_storage, kits_storage, items_storage


class BaseCollectionsResource(Resource):

    @validate_argument('collection', lambda value: collections_storage[int(value)], 'collections', u'Коллекция не найдена')
    @validate_argument('kit', lambda value: kits_storage[int(value)], 'collections', u'Набор не найден')
    @validate_argument('item', lambda value: items_storage[int(value)], 'collections', u'Предмет не найден')
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

    @lazy_property
    def edit_collection_permission(self): return self.account.has_perm('collections.edit_collection')

    @lazy_property
    def moderate_collection_permission(self): return self.account.has_perm('collections.moderate_collection')

    @lazy_property
    def edit_kit_permission(self): return self.account.has_perm('collections.edit_kit')

    @lazy_property
    def moderate_kit_permission(self): return self.account.has_perm('collections.moderate_kit')

    @lazy_property
    def edit_item_permission(self): return self.account.has_perm('collections.edit_item')

    @lazy_property
    def moderate_item_permission(self): return self.account.has_perm('collections.moderate_item')

    @lazy_property
    def can_see_all_collections(self): return self.edit_collection_permission or self.moderate_collection_permission

    @lazy_property
    def can_edit_collection(self):
        if self.collection and self.collection.approved:
            return self.can_moderate_collection
        return self.edit_collection_permission or self.moderate_collection_permission

    @lazy_property
    def can_moderate_collection(self): return self.moderate_collection_permission

    @lazy_property
    def can_edit_kit(self):
        if self.kit and self.kit.approved:
            return self.can_moderate_kit
        return self.edit_kit_permission or self.moderate_kit_permission

    @lazy_property
    def can_moderate_kit(self): return self.moderate_kit_permission

    def _can_edit_item(self, item):
        if item and item.approved:
            return self.can_moderate_item
        return self.edit_item_permission or self.moderate_item_permission

    @lazy_property
    def can_edit_item(self): return self._can_edit_item(self.item)

    @lazy_property
    def can_moderate_item(self): return self.moderate_item_permission

    @lazy_property
    def collections(self):
        if self.moderate_collection_permission or self.edit_collection_permission:
            return sorted(CollectionPrototype.all_collections(), key=lambda c: c.caption)
        else:
            return sorted(CollectionPrototype.approved_collections(), key=lambda c: c.caption)

    @lazy_property
    def kits(self):
        if self.moderate_kit_permission or self.edit_kit_permission:
            return sorted(KitPrototype.all_kits(), key=lambda k: k.caption)
        else:
            return sorted(KitPrototype.approved_kits(), key=lambda k: k.caption)

    def collection_url(self, collection):
        if self.master_account:
            return url('collections:collections:show', collection.id, account=self.master_account.id)
        else:
            return url('collections:collections:show', collection.id)


    def index_url(self):
        if self.master_account:
            return url('collections:collections:', account=self.master_account.id)
        else:
            return url('collections:collections:')


class CollectionsResource(BaseCollectionsResource):


    @validator(code='collections.collections.no_edit_rights', message=u'нет прав для редактирования коллекции')
    def validate_can_edit_collection(self, *args, **kwargs):
        return self.can_edit_collection

    @validator(code='collections.collections.no_moderate_rights', message=u'нет прав для модерации коллекции')
    def validate_can_moderate_collection(self, *args, **kwargs):
        return self.can_moderate_collection

    @validator(code='collections.collections.not_approved', message=u'коллекция не найдена', status_code=404)
    def validate_collection_approved(self, *args, **kwargs):
        return self.collection and (self.can_edit_collection or self.collection.approved)

    @validate_argument('account', AccountPrototype.get_by_id, 'collections', u'Игрок не найден')
    @handler('')
    def index(self, account=None):

        if account is None and self.account.is_authenticated():
            return self.redirect(url('collections:collections:', account=self.account.id))

        self.master_account = account

        master_account_items = None
        last_items = []
        if self.master_account:
            master_account_items = AccountItemsPrototype.get_by_account_id(self.master_account.id)
            last_items = master_account_items.last_items(number=collections_settings.LAST_ITEMS_NUMBER)

        account_items = None
        if self.account.is_authenticated():
            account_items = AccountItemsPrototype.get_by_account_id(self.account.id)

        collections_statistics = get_collections_statistics(account_items=master_account_items)

        collections_table = split_into_table(self.collections, 3)


        return self.template('collections/collections/index.html',
                             {'collections_statistics': collections_statistics,
                              'collections_table': collections_table,
                              'account_items': account_items,
                              'master_account_items': master_account_items,
                              'last_items': last_items})

    @login_required
    @validate_can_edit_collection()
    @handler('new')
    def new(self):
        return self.template('collections/collections/new.html',
                             {'form': EditCollectionForm()})


    @login_required
    @validate_can_edit_collection()
    @handler('create', method='post')
    def create(self):
        form = EditCollectionForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.collections.create.form_errors', form.errors)

        collection = CollectionPrototype.create(caption=form.c.caption,
                                          description=form.c.description)

        return self.json_ok(data={'next_url': url('collections:collections:show', collection.id)})


    @validate_collection_approved()
    @validate_argument('account', AccountPrototype.get_by_id, 'collections', u'Игрок не найден')
    @handler('#collection', name='show')
    def show(self, account=None):

        if account is None and self.account.is_authenticated():
            return self.redirect(url('collections:collections:show', self.collection.id, account=self.account.id))

        self.master_account = account

        master_account_items = None
        if self.master_account:
            master_account_items = AccountItemsPrototype.get_by_account_id(self.master_account.id)

        account_items = None
        if self.account.is_authenticated():
            account_items = AccountItemsPrototype.get_by_account_id(self.account.id)

        collections_statistics = get_collections_statistics(account_items=master_account_items)


        kits = sorted([kit for kit in kits_storage.all() if kit.collection_id == self.collection.id], key=lambda k: k.caption)

        if not (self.can_edit_kit or self.can_moderate_kit):
            kits = [kit for kit in kits if kit.approved]

        items = {kit.id: [] for kit in kits}

        items_query = ItemPrototype._db_all()

        if not self.edit_item_permission and not self.moderate_item_permission:
            items_query = items_query.filter(approved=True)

        for item in ItemPrototype.from_query(items_query.filter(kit_id__in=[kit.id for kit in kits])):
            items[item.kit_id].append(item)

        return self.template('collections/collections/show.html',
                             {'kits': kits,
                              'items': items,
                              'account_items': account_items,
                              'master_account_items': master_account_items,
                              'collections_statistics': collections_statistics})

    @login_required
    @validate_can_edit_collection()
    @handler('#collection', 'edit')
    def edit(self):
        form = EditCollectionForm(initial={'caption': self.collection.caption,
                                        'description': self.collection.description})

        return self.template('collections/collections/edit.html',
                             {'form': form})


    @login_required
    @validate_can_edit_collection()
    @handler('#collection', 'update')
    def update(self, method='post'):
        form = EditCollectionForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.collections.update.form_errors', form.errors)

        self.collection.caption = form.c.caption
        self.collection.description = form.c.description
        self.collection.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_collection()
    @handler('#collection', 'approve')
    def approve(self, method='post'):
        self.collection.approved = True
        self.collection.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_collection()
    @handler('#collection', 'disapprove')
    def disapprove(self, method='post'):
        self.collection.approved = False
        self.collection.save()

        return self.json_ok()


class KitsResource(BaseCollectionsResource):

    @validator(code='collections.kits.no_edit_rights', message=u'нет прав для редактирования набора')
    def validate_can_edit_kit(self, *args, **kwargs):
        return self.can_edit_kit or self.can_moderate_kit

    @validator(code='collections.kits.no_moderate_rights', message=u'нет прав для модерации набора')
    def validate_can_moderate_kit(self, *args, **kwargs):
        return self.can_moderate_kit

    @validator(code='collections.kits.not_approved', message=u'набор не найден', status_code=404)
    def validate_kit_approved(self, *args, **kwargs):
        return self.kit and (self.can_edit_kit or self.kit.approved)

    @login_required
    @validate_can_edit_kit()
    @handler('new')
    def new(self):
        return self.template('collections/kits/new.html',
                             {'form': EditKitForm()})

    @login_required
    @validate_can_edit_kit()
    @handler('create', method='post')
    def create(self):
        form = EditKitForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.kits.create.form_errors', form.errors)

        kit = KitPrototype.create(collection=form.c.collection,
                                  caption=form.c.caption,
                                  description=form.c.description)

        return self.json_ok(data={'next_url': url('collections:collections:show', kit.collection_id)})


    @login_required
    @validate_can_edit_kit()
    @handler('#kit', 'edit')
    def edit(self):
        form = EditKitForm(initial={'collection': self.kit.collection_id,
                                    'caption': self.kit.caption,
                                    'description': self.kit.description})

        return self.template('collections/kits/edit.html',
                             {'form': form})

    @login_required
    @validate_can_edit_kit()
    @handler('#kit', 'update')
    def update(self, method='post'):
        form = EditKitForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.kits.update.form_errors', form.errors)

        self.kit.collection_id = form.c.collection.id
        self.kit.caption = form.c.caption
        self.kit.description = form.c.description
        self.kit.save()

        return self.json_ok(data={'next_url': url('collections:collections:show', self.kit.collection_id)})


    @login_required
    @validate_can_moderate_kit()
    @handler('#kit', 'approve')
    def approve(self, method='post'):
        self.kit.approved = True
        self.kit.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_kit()
    @handler('#kit', 'disapprove')
    def disapprove(self, method='post'):
        self.kit.approved = False
        self.kit.save()

        return self.json_ok()


class ItemsResource(BaseCollectionsResource):

    @validator(code='collections.items.no_edit_rights', message=u'нет прав для редактирования предмета')
    def validate_can_edit_item(self, *args, **kwargs):
        return self.can_edit_item or self.can_moderate_item
        # if self.item is None or not self.item.approved:
        #     print self.item.approved
        #     return self.can_edit_item or self.can_moderate_item
        # else:
        #     return self.can_moderate_item

    @validator(code='collections.items.no_moderate_rights', message=u'нет прав для модерации предмета')
    def validate_can_moderate_item(self, *args, **kwargs):
        return self.can_moderate_item

    @login_required
    @validate_can_edit_item()
    @handler('new')
    def new(self):
        return self.template('collections/items/new.html',
                             {'form': EditItemForm()})

    @login_required
    @validate_can_edit_item()
    @handler('create', method='post')
    def create(self):
        form = EditItemForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.items.create.form_errors', form.errors)

        item = ItemPrototype.create(kit=form.c.kit,
                                        caption=form.c.caption,
                                        text=form.c.text)

        return self.json_ok(data={'next_url': url('collections:collections:show', item.kit.collection_id)})

    @login_required
    @validate_can_edit_item()
    @handler('#item', 'edit')
    def edit(self):
        form = EditItemForm(initial={ 'kit': self.item.kit_id,
                                        'caption': self.item.caption,
                                        'text': self.item.text})

        return self.template('collections/items/edit.html',
                             {'form': form})

    @login_required
    @validate_can_edit_item()
    @handler('#item', 'update')
    def update(self, method='post'):

        form = EditItemForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('collections.items.update.form_errors', form.errors)

        self.item.kit_id = form.c.kit.id
        self.item.caption = form.c.caption
        self.item.text = form.c.text
        self.item.save()

        return self.json_ok(data={'next_url': url('collections:collections:show', self.item.kit.collection_id)})


    @login_required
    @validate_can_moderate_item()
    @handler('#item', 'approve')
    def approve(self, method='post'):
        self.item.approved = True
        self.item.save()

        return self.json_ok()


    @login_required
    @validate_can_moderate_item()
    @handler('#item', 'disapprove')
    def disapprove(self, method='post'):
        self.item.approved = False
        self.item.save()

        return self.json_ok()
