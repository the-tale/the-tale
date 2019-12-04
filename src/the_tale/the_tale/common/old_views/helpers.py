
import smart_imports

smart_imports.all()


class EmptyResourceTestClass(resources.BaseResource):

    def initialize(self):
        super(ResourceTestClass, self).initialize()


class ResourceTestClass(resources.BaseResource):

    def initialize(self):
        super(ResourceTestClass, self).initialize()

    @resources.handler('')
    def index(self):
        pass

    @resources.handler('#object_id', 'show')
    def show(self):
        pass
