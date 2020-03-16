
import smart_imports

smart_imports.all()


def log_command_waiting(name):
    record = models.History.objects.create(state=relations.STATE.WAITING,
                                           name=name,
                                           data={'pid': os.getpid(),
                                                 'command': sys.argv})
    return record.id


def log_command_start(record_id):
    now = datetime.datetime.now()

    models.History.objects.filter(id=record_id).update(state=relations.STATE.RUNNING,
                                                       updated_at=now,
                                                       started_at=now)


def other_command_in_queue(name, record_id):
    return models.History.objects.filter(name=name,
                                         state=relations.STATE.WAITING,
                                         id__lt=record_id).exists()


def log_command_finish(record_id, result):
    now = datetime.datetime.now()

    models.History.objects.filter(id=record_id).update(finished_at=now,
                                                       updated_at=now,
                                                       state=relations.STATE.FINISHED,
                                                       result=result)


def is_game_running():

    for proc in psutil.process_iter():
        try:
            process_cmdline = ' '.join(proc.cmdline())

            if 'django-admin' in process_cmdline and 'supervisor' in process_cmdline and 'the_tale' in process_cmdline:
                return True
        except psutil.NoSuchProcess:
            pass

    return False
