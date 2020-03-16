
import smart_imports

smart_imports.all()


def create_lock_request(name, comment=None):
    data = {'pid': os.getpid(),
            'command': sys.argv,
            'comment': comment}

    return models.LockRequest.objects.create(name=name,
                                             state=relations.STATE.REQUESTED,
                                             data=data)


def try_to_lock(lock_request):
    requests_ids = list(models.LockRequest.objects.filter(name=lock_request.name).order_by('id').values_list('id', flat=True))

    if lock_request.id not in requests_ids:
        return False

    if lock_request.id == requests_ids[0]:
        lock_request.state = relations.STATE.ACTIVE
        lock_request.save()
        return True

    return None


def delete_lock_request(lock_request):
    lock_request.delete()


@contextlib.contextmanager
def lock(name, comment=None, delay_on_retry=0.1, logger=None):

    lock_request = create_lock_request(name, comment)

    if logger:
        logger.info(f'lock "{lock_request.name}" requested')

    try:

        while (result := try_to_lock(lock_request)) is None:

            if logger:
                logger.info(f'lock "{lock_request.name}" is busy')

            time.sleep(delay_on_retry)

        if not result:
            if logger:
                logger.info(f'lock "{lock_request.name}" is lost')

            raise exceptions.LockLostBeforeLockingError(lock_request.name)
        else:
            if logger:
                logger.info(f'lock "{lock_request.name}" received')

        yield

    except Exception:
        if logger:
            logger.info(f'exception cached, try to free lock "{lock_request.name}"')

        raise

    finally:
        delete_lock_request(lock_request)

        if logger:
            logger.info(f'lock "{lock_request.name}" freed')
