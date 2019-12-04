
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^', django_urls.include(old_views.resource_patterns(views.AchievementsResource)))]
