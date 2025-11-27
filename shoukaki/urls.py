from django.urls import path

from shoukaki import views

app_name = "shoukaki"
urlpatterns = [
    path("list/", views.ShoukakiListView.as_view(), name="list"),
    path("create/", views.ShoukakiCreateView.as_view(), name="create"),
    path("update_list/", views.ShoukakiUpdateListView.as_view(), name="update_list"),
    path("update/<int:pk>", views.ShoukakiUpdateView.as_view(), name="update"),
    path("typelist/", views.ShoukakiTypeListView.as_view(), name="typelist"),
    path("typecreate/", views.ShoukakiTypeCreateView.as_view(), name="typecreate"),
    path("typeupdate/<int:pk>", views.ShoukakiTypeUpdateView.as_view(), name="typeupdate"),
    path("disposal/", views.ShoukakiDisposalView.as_view(), name="disposal"),
]
