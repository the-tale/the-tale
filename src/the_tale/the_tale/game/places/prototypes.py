
import smart_imports

smart_imports.all()


class ResourceExchangePrototype(utils_prototypes.BasePrototype):
    _model_class = models.ResourceExchange
    _readonly = ('id', 'bill_id', 'resource_1', 'resource_2')
    _bidirectional = ()
    _get_by = ('id',)

    @property
    def place_1(self):
        return storage.places.get(self._model.place_1_id)

    @property
    def place_2(self):
        return storage.places.get(self._model.place_2_id)

    @utils_decorators.lazy_property
    def bill(self):
        return bills_prototypes.BillPrototype.get_by_id(self.bill_id)

    def get_resources_for_place(self, place):
        if self.place_1 and place.id == self.place_1.id:
            return (self.resource_1, self.resource_2, self.place_2)
        if self.place_2 and place.id == self.place_2.id:
            return (self.resource_2, self.resource_1, self.place_1)
        return (relations.RESOURCE_EXCHANGE_TYPE.NONE, relations.RESOURCE_EXCHANGE_TYPE.NONE, None)

    @classmethod
    def create(cls, place_1, place_2, resource_1, resource_2, bill):
        model = cls._model_class.objects.create(bill=bill._model if bill is not None else None,
                                                place_1_id=place_1.id if place_1 is not None else None,
                                                place_2_id=place_2.id if place_2 is not None else None,
                                                resource_1=resource_1,
                                                resource_2=resource_2)
        prototype = cls(model=model)

        storage.resource_exchanges.add_item(prototype.id, prototype)
        storage.resource_exchanges.update_version()

        return prototype

    def remove(self):
        self._model.delete()

        storage.resource_exchanges.update_version()
        storage.resource_exchanges.refresh()
