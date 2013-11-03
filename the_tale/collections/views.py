# coding: utf-8

from dext.views import handler, validate_argument, validator
from dext.utils.urls import url

from common.utils.resources import Resource
from common.utils.decorators import login_required

from achievements.prototypes import CollectionPrototype, KitPrototype, ItemPrototype
from achievements.forms import EditCollectionForm, EditKitForm, EditItemForm


class BaseAchievementsResource(Resource):

    @validate_argument('collection', CollectionPrototype.get_by_id, 'achievements', u'Коллекция не найдена')
    @validate_argument('kit', KitPrototype.get_by_id, 'achievements', u'Набор не найден')
    @validate_argument('item', ItemPrototype.get_by_id, 'achievements', u'Предмет не найден')
    def initialize(self, collection=None, kit=None, item=None, **kwargs):
        super(BaseAchievementsResource, self).initialize(**kwargs)
        self.item = item
        self.kit = kit
        self.collection = collection

        if self.item:
            self.kit = self.item.kit

        if self.kit:
            self.collection = self.kit.collection

    @property
    def edit_collection_permission(self): return self.account.has_perm('achievements.edit_collection')

    @property
    def moderate_collection_permission(self): return self.account.has_perm('achievements.moderate_collection')

    @property
    def edit_kit_permission(self): return self.account.has_perm('achievements.edit_kit')

    @property
    def moderate_kit_permission(self): return self.account.has_perm('achievements.moderate_kit')

    @property
    def edit_item_permission(self): return self.account.has_perm('achievements.edit_item')

    @property
    def moderate_item_permission(self): return self.account.has_perm('achievements.moderate_item')

    @property
    def can_see_all_collections(self): return self.edit_collection_permission or self.moderate_collection_permission

    @property
    def can_edit_collection(self):
        if self.collection and self.collection.approved:
            return self.can_moderate_collection
        return self.edit_collection_permission or self.moderate_collection_permission

    @property
    def can_moderate_collection(self): return self.moderate_collection_permission

    @property
    def can_edit_kit(self):
        if self.kit and self.kit.approved:
            return self.can_moderate_kit
        return self.edit_kit_permission or self.moderate_kit_permission

    @property
    def can_moderate_kit(self): return self.moderate_kit_permission

    def _can_edit_item(self, item):
        if item and item.approved:
            return self.can_moderate_item
        return self.edit_item_permission or self.moderate_item_permission

    @property
    def can_edit_item(self): return self._can_edit_item(self.item)

    @property
    def can_moderate_item(self): return self.moderate_item_permission

    @property
    def collections(self):
        if self.moderate_collection_permission or self.edit_collection_permission:
            return CollectionPrototype.all_collections()
        else:
            return CollectionPrototype.approved_collections()

    @property
    def kits(self):
        if self.moderate_kit_permission or self.edit_kit_permission:
            return KitPrototype.all_kits()
        else:
            return KitPrototype.approved_kits()


class CollectionsResource(BaseAchievementsResource):


    @validator(code='achievements.collections.no_edit_rights', message=u'нет прав для редактирования коллекции')
    def validate_can_edit_collection(self, *args, **kwargs):
        return self.can_edit_collection

    @validator(code='achievements.collections.no_moderate_rights', message=u'нет прав для модерации коллекции')
    def validate_can_moderate_collection(self, *args, **kwargs):
        return self.can_moderate_collection

    @validator(code='achievements.collections.not_approved', message=u'коллекция не найдена', status_code=404)
    def validate_collection_approved(self, *args, **kwargs):
        return self.collection and (self.can_edit_collection or self.collection.approved)

    @login_required
    @validate_can_edit_collection()
    @handler('')
    def index(self):
        return self.template('achievements/collections/index.html',
                             {})

    @login_required
    @validate_can_edit_collection()
    @handler('new')
    def new(self):
        return self.template('achievements/collections/new.html',
                             {'form': EditCollectionForm()})


    @login_required
    @validate_can_edit_collection()
    @handler('create', method='post')
    def create(self):
        form = EditCollectionForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.collections.create.form_errors', form.errors)

        collection = CollectionPrototype.create(caption=form.c.caption,
                                          description=form.c.description)

        return self.json_ok(data={'next_url': url('achievements:collections:show', collection.id)})


    @validate_collection_approved()
    @handler('#collection', name='show')
    def show(self):
        kits = KitPrototype.get_list_by_collection_id(self.collection.id)
        if not (self.can_edit_kit or self.can_moderate_kit):
            kits = [kit for kit in kits if kit.approved]
        return self.template('achievements/collections/show.html',
                             {'kits': kits})

    @login_required
    @validate_can_edit_collection()
    @handler('#collection', 'edit')
    def edit(self):
        form = EditCollectionForm(initial={'caption': self.collection.caption,
                                        'description': self.collection.description})

        return self.template('achievements/collections/edit.html',
                             {'form': form})


    @login_required
    @validate_can_edit_collection()
    @handler('#collection', 'update')
    def update(self, method='post'):
        form = EditCollectionForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.collections.update.form_errors', form.errors)

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


class KitsResource(BaseAchievementsResource):

    @validator(code='achievements.kits.no_edit_rights', message=u'нет прав для редактирования набора')
    def validate_can_edit_kit(self, *args, **kwargs):
        return self.can_edit_kit or self.can_moderate_kit

    @validator(code='achievements.kits.no_moderate_rights', message=u'нет прав для модерации набора')
    def validate_can_moderate_kit(self, *args, **kwargs):
        return self.can_moderate_kit

    @validator(code='achievements.kits.not_approved', message=u'набор не найден', status_code=404)
    def validate_kit_approved(self, *args, **kwargs):
        return self.kit and (self.can_edit_kit or self.kit.approved)

    @login_required
    @validate_can_edit_kit()
    @handler('')
    def index(self):
        return self.template('achievements/kits/index.html',
                             {})

    @login_required
    @validate_can_edit_kit()
    @handler('new')
    def new(self):
        return self.template('achievements/kits/new.html',
                             {'form': EditKitForm()})

    @login_required
    @validate_can_edit_kit()
    @handler('create', method='post')
    def create(self):
        form = EditKitForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.kits.create.form_errors', form.errors)

        kit = KitPrototype.create(collection=form.c.collection,
                                  caption=form.c.caption,
                                  description=form.c.description)

        return self.json_ok(data={'next_url': url('achievements:kits:show', kit.id)})


    @handler('#kit', name='show')
    def show(self):
        items = ItemPrototype.get_list_by_kit_id(self.kit.id)
        if not (self.can_edit_item or self.can_moderate_item):
            items = [item for item in items if item.approved]
        return self.template('achievements/kits/show.html',
                             {'items': items})

    @login_required
    @validate_can_edit_kit()
    @handler('#kit', 'edit')
    def edit(self):
        form = EditKitForm(initial={'collection': self.kit.collection_id,
                                    'caption': self.kit.caption,
                                    'description': self.kit.description})

        return self.template('achievements/kits/edit.html',
                             {'form': form})

    @login_required
    @validate_can_edit_kit()
    @handler('#kit', 'update')
    def update(self, method='post'):
        form = EditKitForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.kits.update.form_errors', form.errors)

        self.kit.collection_id = form.c.collection.id
        self.kit.caption = form.c.caption
        self.kit.description = form.c.description
        self.kit.save()

        return self.json_ok(data={'next_url': url('achievements:collections:show', self.kit.collection_id)})


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


class ItemsResource(BaseAchievementsResource):

    @validator(code='achievements.items.no_edit_rights', message=u'нет прав для редактирования предмета')
    def validate_can_edit_item(self, *args, **kwargs):
        return self.can_edit_item or self.can_moderate_item

    @validator(code='achievements.items.no_moderate_rights', message=u'нет прав для модерации предмета')
    def validate_can_moderate_item(self, *args, **kwargs):
        return self.can_moderate_item

    @login_required
    @validate_can_edit_item()
    @handler('new')
    def new(self):
        return self.template('achievements/items/new.html',
                             {'form': EditItemForm()})

    @login_required
    @validate_can_edit_item()
    @handler('create', method='post')
    def create(self):
        form = EditItemForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.items.create.form_errors', form.errors)

        item = ItemPrototype.create(kit=form.c.kit,
                                        caption=form.c.caption,
                                        text=form.c.text)

        return self.json_ok(data={'next_url': url('achievements:kits:show', item.kit_id)})

    @login_required
    @validate_can_edit_item()
    @handler('#item', 'edit')
    def edit(self):
        form = EditItemForm(initial={ 'kit': self.item.kit_id,
                                        'caption': self.item.caption,
                                        'text': self.item.text})

        return self.template('achievements/items/edit.html',
                             {'form': form})

    @login_required
    @validate_can_edit_item()
    @handler('#item', 'update')
    def update(self, method='post'):
        form = EditItemForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('achievements.items.update.form_errors', form.errors)

        self.item.kit_id = form.c.kit.id
        self.item.caption = form.c.caption
        self.item.text = form.c.text
        self.item.save()

        return self.json_ok(data={'next_url': url('achievements:kits:show', self.item.kit_id)})


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


class AccountsResource(BaseAchievementsResource):
    pass
