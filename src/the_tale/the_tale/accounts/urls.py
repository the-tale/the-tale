
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^registration/', django_urls.include((views.registration_resource.get_urls(), 'registration'))),
               django_urls.url(r'^profile/', django_urls.include((views.profile_resource.get_urls() +
                                                                  views.technical_resource.get_urls(), 'profile'))),
               django_urls.url(r'^auth/', django_urls.include((views.auth_resource.get_urls(), 'auth'))),
               django_urls.url(r'^messages/', django_urls.include(('the_tale.accounts.personal_messages.urls', 'messages'))),
               django_urls.url(r'^friends/', django_urls.include(('the_tale.accounts.friends.urls', 'friends'))),
               django_urls.url(r'^achievements/', django_urls.include(('the_tale.accounts.achievements.urls', 'achievements'))),
               django_urls.url(r'^third-party/', django_urls.include(('the_tale.accounts.third_party.urls', 'third-party'))),
               django_urls.url(r'^', django_urls.include(views.accounts_resource.get_urls()))]
