
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^registration/', django_urls.include(views.registration_resource.get_urls(), namespace='registration')),
               django_urls.url(r'^profile/', django_urls.include(dext_old_views.resource_patterns(views.ProfileResource), namespace='profile')),
               django_urls.url(r'^auth/', django_urls.include(dext_old_views.resource_patterns(views.AuthResource), namespace='auth')),
               django_urls.url(r'^messages/', django_urls.include('the_tale.accounts.personal_messages.urls', namespace='messages')),
               django_urls.url(r'^friends/', django_urls.include('the_tale.accounts.friends.urls', namespace='friends')),
               django_urls.url(r'^achievements/', django_urls.include('the_tale.accounts.achievements.urls', namespace='achievements')),
               django_urls.url(r'^third-party/', django_urls.include('the_tale.accounts.third_party.urls', namespace='third-party')),
               django_urls.url(r'^', django_urls.include(views.accounts_resource.get_urls()))]
