from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^binary/tree/$', views.TreeView.as_view(), name='binary-tree'),
    url(r'^binary/change-outpouring-side/$', views.ChangeOutpouringSideView.as_view(), name='binary-change-outpouring-side'),
    url(r'^binary/search-node/$', views.SearchNodeView.as_view(), name='binary-search-node'),
]
