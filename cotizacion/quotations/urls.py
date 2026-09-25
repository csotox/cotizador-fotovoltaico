from django.urls import path

from . import views

app_name = "quotations"

urlpatterns = [
    path("", views.QuotationListView.as_view(), name="list"),
    path("nueva/", views.QuotationCreateView.as_view(), name="create"),
    path("<uuid:uuid>/", views.QuotationDetailView.as_view(), name="detail"),
    path("<uuid:uuid>/editar/", views.QuotationUpdateView.as_view(), name="update"),
    path("<uuid:uuid>/eliminar/", views.QuotationDeleteView.as_view(), name="delete"),
    path(
        "<uuid:uuid>/items/nuevo/",
        views.QuotationItemCreateView.as_view(),
        name="item-create",
    ),
    path(
        "<uuid:uuid>/items/<uuid:item_uuid>/editar/",
        views.QuotationItemUpdateView.as_view(),
        name="item-update",
    ),
    path(
        "<uuid:uuid>/items/<uuid:item_uuid>/eliminar/",
        views.QuotationItemDeleteView.as_view(),
        name="item-delete",
    ),
]
