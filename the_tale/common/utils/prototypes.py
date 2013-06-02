# coding: utf-8

class PrototypeError(Exception): pass


class _PrototypeMetaclass(type):

    @classmethod
    def create_get_property(cls, property_name):
        return lambda self: getattr(self._model, property_name)

    @classmethod
    def create_set_property(cls, property_name):
        return lambda self, value: setattr(self._model, property_name, value)

    @classmethod
    def create_get_by(cls, method_name, attribute_name):

        def get_by(cls, identifier):
            try:
                return cls(model=cls._model_class.objects.get(**{attribute_name: identifier}))
            except cls._model_class.DoesNotExist:
                return None

        get_by.__name__ = method_name

        return classmethod(get_by)

    @classmethod
    def create_get_list_by(cls, method_name, attribute_name):

        def get_list_by(cls, identifiers):
            return [cls(model=model) for model in cls._model_class.objects.filter(**{'%s__in' % attribute_name: identifiers})]

        get_list_by.__name__ = method_name

        return classmethod(get_list_by)


    def __new__(cls, name, bases, attributes):

        # create readonly properties
        readonly_attributes = attributes.get('_readonly', ())
        for readonly_attribute in readonly_attributes:
            if readonly_attribute in attributes:
                raise PrototypeError('can not set readonly attribute "%s" class has already had attribue with such name' % readonly_attribute)
            attributes[readonly_attribute] = property(cls.create_get_property(readonly_attribute))

        # create bidirectional properties
        bidirectional_attributes = attributes.get('_bidirectional', ())
        for bidirectional_attribute in bidirectional_attributes:
            if bidirectional_attribute in attributes:
                raise PrototypeError('can not set bidirectional attribute "%s" class has already had attribue with such name' % bidirectional_attribute)
            attributes[bidirectional_attribute] = property(cls.create_get_property(bidirectional_attribute),
                                                           cls.create_set_property(bidirectional_attribute))

        # create get_by_<unique_key> and get_list_by_<unique_key> methods
        get_by_attributes = attributes.get('_get_by', ())
        for get_by_attribute in get_by_attributes:
            method_name = 'get_by_%s' % get_by_attribute
            if method_name in attributes:
                raise PrototypeError('can not set attribute "%s" class has already had attribue with such name' % method_name)
            attributes[method_name] = cls.create_get_by(method_name, get_by_attribute)

            method_name = 'get_list_by_%s' % get_by_attribute
            if method_name in attributes:
                raise PrototypeError('can not set attribute "%s" class has already had attribue with such name' % method_name)
            attributes[method_name] = cls.create_get_list_by(method_name, get_by_attribute)

        return super(_PrototypeMetaclass, cls).__new__(cls, name, bases, attributes)


class BasePrototype(object):

    __metaclass__ = _PrototypeMetaclass
    __slots__ = ('_model',)

    _model_class = None
    _readonly = ()
    _bidirectional = ()
    _get_by = ()

    def __init__(self, model):
        self._model = model

    def reload(self):
        self._model = self._model_class.objects.get(id=self._model.id)

    def create(self, *argv, **kwargs):
        raise NotImplementedError

    def __unicode__(self):
        return self._model.__unicode__()

    def __repr__(self):
        return self._model.__repr__()

    # most for tests
    @classmethod
    def _db_get_object(cls, number=0):
        return cls(model=cls._model_class.objects.all().order_by('id')[number])

    @classmethod
    def _db_all(cls):
        return [cls(model=model) for model in cls._model_class.objects.all()]

    @classmethod
    def _db_count(cls):
        return cls._model_class.objects.all().count()

    @classmethod
    def _db_delete_all(cls):
        return cls._model_class.objects.all().delete()

    @classmethod
    def _db_filter(cls, **kwargs):
        return cls._model_class.objects.filter(**kwargs)
