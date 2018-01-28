
from the_tale.game.cards import views

urlpatterns = views.resource.get_urls() + views.technical_resource.get_urls()
