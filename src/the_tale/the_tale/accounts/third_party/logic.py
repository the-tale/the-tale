
import smart_imports

smart_imports.all()


def remove_expired_access_tokens():
    live_time = datetime.timedelta(minutes=conf.settings.UNPROCESSED_ACCESS_TOKEN_LIVE_TIME)

    prototypes.AccessTokenPrototype._db_filter(state=relations.ACCESS_TOKEN_STATE.UNPROCESSED,
                                               created_at__lt=datetime.datetime.now() - live_time).delete()
