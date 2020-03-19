
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('AMQP',
                                           ENVIRONMENT_MODULE='%s.amqp_environment' % django_settings.PROJECT_MODULE,
                                           WORKERS_MANAGER_PID='the_tale_ampq_workers_manager')
