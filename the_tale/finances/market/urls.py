# coding: utf-8

from the_tale.finances.market import views as market_views

urlpatterns = market_views.resource.get_urls()
urlpatterns += market_views.index_resource.get_urls()
