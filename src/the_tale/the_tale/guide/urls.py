
import smart_imports

smart_imports.all()


urlpatterns = dext_old_views.resource_patterns(views.GuideResource)

urlpatterns += [django_urls.url(r'^mobs/', django_urls.include(dext_old_views.resource_patterns(mobs_views.GuideMobResource), namespace='mobs')),
                django_urls.url(r'^artifacts/', django_urls.include(dext_old_views.resource_patterns(artifacts_views.GuideArtifactResource), namespace='artifacts')),
                django_urls.url(r'^cards/', django_urls.include(cards_views.guide_resource.get_urls(), namespace='cards')),
                django_urls.url(r'^companions/', django_urls.include(companions_views.resource.get_urls(), namespace='companions'))]
