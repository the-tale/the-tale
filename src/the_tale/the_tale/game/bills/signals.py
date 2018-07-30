
import smart_imports

smart_imports.all()

bill_created = django_dispatch.Signal(providing_args=['bill'])
bill_edited = django_dispatch.Signal(providing_args=['bill'])
bill_moderated = django_dispatch.Signal(providing_args=['bill'])
bill_processed = django_dispatch.Signal(providing_args=['bill'])
bill_removed = django_dispatch.Signal(providing_args=['bill'])
bill_ended = django_dispatch.Signal(providing_args=['bill'])
bill_stopped = django_dispatch.Signal(providing_args=['bill'])
