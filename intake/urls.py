from django.urls import path

from . import views

urlpatterns = [
    path("collections/batch/", views.CollectionBatchView.as_view(),
         name="collection-batch"),
    path("collections/", views.CollectionListView.as_view(),
         name="collection-list"),
]
