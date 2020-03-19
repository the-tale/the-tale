
import smart_imports

smart_imports.all()


class CollectionsStorage(utils_storage.PrototypeStorage):
    SETTINGS_KEY = 'collections change time'
    EXCEPTION = exceptions.CollectionsError
    PROTOTYPE = prototypes.CollectionPrototype

    def get_form_choices(self):
        return [('', '----')] + [(c.id, c.caption) for c in self.all()]


class KitsStorage(utils_storage.PrototypeStorage):
    SETTINGS_KEY = 'kits change time'
    EXCEPTION = exceptions.CollectionsError
    PROTOTYPE = prototypes.KitPrototype

    def get_form_choices(self):
        return [('', '----')] + [(k.id, k.caption) for k in self.all()]


class ItemsStorage(utils_storage.PrototypeStorage):
    SETTINGS_KEY = 'items change time'
    EXCEPTION = exceptions.CollectionsError
    PROTOTYPE = prototypes.ItemPrototype

    def form_choices(self):
        self.sync()

        choices = []

        for kit in kits.all():
            items = []

            for item in self.all():
                if item.kit_id == kit.id:
                    items.append((item.id, item.caption))

            choices.append((kit.caption, sorted(items, key=lambda record: record[1])))

        return sorted(choices)


collections = CollectionsStorage()
kits = KitsStorage()
items = ItemsStorage()
