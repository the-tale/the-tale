
import smart_imports

smart_imports.all()


urlpatterns = [django_urls.url(r'^posts/', django_urls.include(dext_old_views.resource_patterns(views.PostsResource), namespace='posts')),
               django_urls.url(r'^threads/', django_urls.include(dext_old_views.resource_patterns(views.ThreadsResource), namespace='threads')),
               django_urls.url(r'^subcategories/', django_urls.include(dext_old_views.resource_patterns(views.SubCategoryResource), namespace='subcategories')),
               django_urls.url(r'^subscriptions/', django_urls.include(dext_old_views.resource_patterns(views.SubscriptionsResource), namespace='subscriptions')),
               django_urls.url(r'^', django_urls.include(dext_old_views.resource_patterns(views.ForumResource)))]
