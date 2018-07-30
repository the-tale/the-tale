
import smart_imports

smart_imports.all()


settings = dext_app_settings.app_settings('MAP',
                                          WIDTH=70 if not django_settings.TESTS_RUNNING else 4,
                                          HEIGHT=70 if not django_settings.TESTS_RUNNING else 4,

                                          CHRONICLE_RECORDS_NUMBER=10,

                                          CELL_RANDOMIZE_FRACTION=0.1,

                                          CELL_SIZE=32,

                                          REGION_API_VERSION='0.1',
                                          REGION_VERSIONS_API_VERSION='0.1',

                                          TERRAIN_PRIORITIES_FIXTURE=os.path.join(os.path.dirname(__file__), 'fixtures', 'bioms.xls'))
