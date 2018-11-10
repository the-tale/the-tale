
import smart_imports

smart_imports.all()


settings = dext_app_settings.app_settings('BLOGS',
                                          FORUM_CATEGORY_UID='folclor',
                                          MIN_TEXT_LENGTH=1000,
                                          POSTS_ON_PAGE=15,
                                          FORUM_TAGS_THREAD=4437,
                                          DEFAULT_TAGS=[1],
                                          IS_ABOUT_MAXIMUM=100,
                                          CANON_TAG=3)
