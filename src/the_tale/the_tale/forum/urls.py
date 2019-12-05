
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^posts/', django_urls.include((old_views.resource_patterns(views.PostsResource), 'posts'))),
               django_urls.url(r'^threads/', django_urls.include((old_views.resource_patterns(views.ThreadsResource), 'threads'))),
               django_urls.url(r'^subcategories/', django_urls.include((old_views.resource_patterns(views.SubCategoryResource), 'subcategories'))),
               django_urls.url(r'^subscriptions/', django_urls.include((old_views.resource_patterns(views.SubscriptionsResource), 'subscriptions'))),
               django_urls.url(r'^', django_urls.include(old_views.resource_patterns(views.ForumResource)))]
