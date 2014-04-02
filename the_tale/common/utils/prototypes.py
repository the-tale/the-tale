# coding: utf-8
import time

from dext.utils import s11n

from the_tale.common.utils.decorators import lazy_property


class PrototypeError(Exception): pass



def _serialization_proxy(Class, field_name, unload_after):

    class SerializationProxy(object):

        __slots__ = ('_prototype', '_object', '_accessed_at')

        def __init__(self, prototype):
            self._prototype = prototype
            self._object = None
            self._accessed_at = 0

        def _load_object(self):
            self._object = Class.deserialize(self._prototype, s11n.from_json(getattr(self._prototype._model, field_name)))

        def _unload_object(self):
            self.serialize()
            del self._object
            self._object = None
            self._accessed_at = 0

        def updated_get(self):
            return self._object is not None and self._object.updated

        def updated_set(self, value):
            if self._object is None:
                self._load_object()
            self._object.updated = value

        updated = property(updated_get, updated_set)

        def serialize(self, **kwargs):
            if self._object is None:
                return
            self._object.updated = False
            setattr(self._prototype._model, field_name, s11n.to_json(self._object.serialize(**kwargs)))

        def __getattr__(self, name):
            if self._object is None:
                self._load_object()
            self._accessed_at = time.time()
            return getattr(self._object, name)

        def _unload_if_can(self, timestamp):
            if unload_after is None:
                return
            if timestamp < self._accessed_at + unload_after:
                return
            self._unload_object()

        def __len__(self):
            if self._object is None:
                self._load_object()
            self._accessed_at = time.time()
            return self._object.__len__()


    SerializationProxy.__name__ = '%sSerializationProxy' % Class.__name__

    return SerializationProxy


class _PrototypeMetaclass(type):

    @classmethod
    def create_get_property(mcs, property_name):
        return lambda self: getattr(self._model, property_name)

    @classmethod
    def create_set_property(mcs, property_name):
        return lambda self, value: setattr(self._model, property_name, value)

    @classmethod
    def create_get_by(mcs, method_name, attribute_name):

        def get_by(cls, identifier):
            try:
                return cls(model=cls._model_class.objects.get(**{attribute_name: identifier}))
            except cls._model_class.DoesNotExist:
                return None

        get_by.__name__ = method_name

        return classmethod(get_by)

    @classmethod
    def create_get_list_by(mcs, method_name, attribute_name):

        def get_list_by(cls, identifiers):
            if isinstance(identifiers, (tuple, list)):
                query = cls._model_class.objects.filter(**{'%s__in' % attribute_name: identifiers})
            else:
                query = cls._model_class.objects.filter(**{'%s' % attribute_name: identifiers})
            return [cls(model=model) for model in query]

        get_list_by.__name__ = method_name

        return classmethod(get_list_by)

    @classmethod
    def create_serialization_proxy(cls, Class, field_name, unload_after):
        ProxyClass = _serialization_proxy(Class=Class, field_name=field_name, unload_after=unload_after)

        def proxy(self):
            return ProxyClass(prototype=self)

        proxy.__name__ = field_name

        return proxy


    def __new__(mcs, name, bases, attributes):

        # create readonly properties
        readonly_attributes = attributes.get('_readonly', ())
        for readonly_attribute in readonly_attributes:
            if readonly_attribute in attributes:
                raise PrototypeError('can not set readonly attribute "%s" class has already had attribue with such name' % readonly_attribute)
            attributes[readonly_attribute] = property(mcs.create_get_property(readonly_attribute))

        # create bidirectional properties
        bidirectional_attributes = attributes.get('_bidirectional', ())
        for bidirectional_attribute in bidirectional_attributes:
            if bidirectional_attribute in attributes:
                raise PrototypeError('can not set bidirectional attribute "%s" class has already had attribue with such name' % bidirectional_attribute)
            attributes[bidirectional_attribute] = property(mcs.create_get_property(bidirectional_attribute),
                                                           mcs.create_set_property(bidirectional_attribute))

        # create get_by_<unique_key> and get_list_by_<unique_key> methods
        get_by_attributes = attributes.get('_get_by', ())
        for get_by_attribute in get_by_attributes:
            method_name = 'get_by_%s' % get_by_attribute
            if method_name in attributes:
                raise PrototypeError('can not set attribute "%s" class has already had attribue with such name' % method_name)
            attributes[method_name] = mcs.create_get_by(method_name, get_by_attribute)

            method_name = 'get_list_by_%s' % get_by_attribute
            if method_name in attributes:
                raise PrototypeError('can not set attribute "%s" class has already had attribue with such name' % method_name)
            attributes[method_name] = mcs.create_get_list_by(method_name, get_by_attribute)

        serialization_proxies = attributes.get('_serialization_proxies', ())
        for proxy_field, proxy_class, unload_after in serialization_proxies:
            if proxy_field in attributes:
                raise PrototypeError('can not set attribute "%s" class has already had attribue with such name' % proxy_field)
            attributes[proxy_field] = lazy_property(mcs.create_serialization_proxy(Class=proxy_class, field_name=proxy_field, unload_after=unload_after))

        return super(_PrototypeMetaclass, mcs).__new__(mcs, name, bases, attributes)


class BasePrototype(object):

    __metaclass__ = _PrototypeMetaclass
    __slots__ = ('_model',)

    _model_class = None
    _readonly = ()
    _bidirectional = ()
    _get_by = ()
    _serialization_proxies = ()

    def __init__(self, model):
        self._model = model

    def reload(self):
        self._model = self._model_class.objects.get(id=self._model.id)
        for field_name, Class, timeout in self._serialization_proxies:
            getattr(self, field_name)._load_object()

    def create(self, *argv, **kwargs):
        raise NotImplementedError

    def save(self):
        for field_name, Class, timeout in self._serialization_proxies:
            object = getattr(self, field_name)
            if object.updated:
                object._unload_object()
        self._model.save()

    def unload_serializable_items(self, timestamp):
        for field_name, Class, timeout in self._serialization_proxies:
            getattr(self, field_name)._unload_if_can(timestamp)

    @classmethod
    def from_query(cls, query):
        return [cls(model=model) for model in query]

    def __unicode__(self):
        return self._model.__unicode__()

    def __repr__(self):
        return '%s(model=%s)' % (self.__class__.__name__, self._model.__repr__())

    #############################
    # db query shortcuts
    #############################

    @classmethod
    def _db_create(cls, **kwargs):
        return cls._model_class.objects.create(**kwargs)

    @classmethod
    def _db_all(cls):
        return cls._model_class.objects.all()

    @classmethod
    def _db_count(cls): # DEPRECTATED: use _db_all().count() || _db_filter().count()
        return cls._model_class.objects.all().count()

    @classmethod
    def _db_filter(cls, *argv, **kwargs):
        return cls._model_class.objects.filter(*argv, **kwargs)

    @classmethod
    def _db_exclude(cls, **kwargs):
        return cls._model_class.objects.exclude(**kwargs)

    #############################
    # most for tests
    #############################
    @classmethod
    def _db_get_object(cls, number=0):
        return cls(model=cls._model_class.objects.all().order_by('id')[number])
